#!/usr/bin/env python3
"""
Database Setup Verification Script

This script verifies that the Supabase database and Upstash Redis
are properly configured and accessible.

Usage:
    python verify_setup.py

Requirements:
    pip install asyncpg redis python-dotenv
"""

import asyncio
import os
import sys
from typing import Dict, List, Tuple

try:
    import asyncpg
    import redis
    from dotenv import load_dotenv
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install asyncpg redis python-dotenv")
    sys.exit(1)


# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "")


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_result(check: str, passed: bool, details: str = ""):
    """Print a check result."""
    status = "✅" if passed else "❌"
    print(f"{status} {check}")
    if details:
        print(f"   {details}")


async def verify_postgres_connection() -> Tuple[bool, str]:
    """Verify PostgreSQL connection."""
    try:
        # Extract connection details from Supabase URL
        if not SUPABASE_URL:
            return False, "SUPABASE_URL not set in environment"
        
        # Parse Supabase URL to get host
        host = SUPABASE_URL.replace("https://", "").replace("http://", "")
        project_ref = host.split(".")[0]
        
        # Construct connection string
        conn_str = f"postgresql://postgres:{SUPABASE_SERVICE_KEY}@db.{project_ref}.supabase.co:5432/postgres"
        
        conn = await asyncpg.connect(conn_str)
        await conn.close()
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)


async def verify_extensions(conn: asyncpg.Connection) -> Dict[str, bool]:
    """Verify required extensions are installed."""
    extensions = {}
    
    try:
        rows = await conn.fetch(
            "SELECT extname FROM pg_extension WHERE extname IN ('vector', 'pg_trgm')"
        )
        installed = {row['extname'] for row in rows}
        
        extensions['vector'] = 'vector' in installed
        extensions['pg_trgm'] = 'pg_trgm' in installed
    except Exception as e:
        print(f"   Error checking extensions: {e}")
    
    return extensions


async def verify_tables(conn: asyncpg.Connection) -> List[str]:
    """Verify all required tables exist."""
    expected_tables = {
        'videos', 'transcripts', 'transcript_chunks', 
        'notes', 'collections', 'collection_items'
    }
    
    try:
        rows = await conn.fetch(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = ANY($1::text[])
            """,
            list(expected_tables)
        )
        return [row['table_name'] for row in rows]
    except Exception as e:
        print(f"   Error checking tables: {e}")
        return []


async def verify_indexes(conn: asyncpg.Connection) -> Dict[str, bool]:
    """Verify critical indexes exist."""
    indexes = {}
    
    critical_indexes = {
        'idx_chunks_embedding': 'IVFFLAT vector index',
        'idx_transcripts_fulltext': 'Full-text search index',
        'idx_videos_title_trgm': 'Trigram title index',
        'idx_notes_keywords': 'Keywords GIN index'
    }
    
    try:
        for idx_name, description in critical_indexes.items():
            result = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = $1 AND schemaname = 'public'
                )
                """,
                idx_name
            )
            indexes[description] = result
    except Exception as e:
        print(f"   Error checking indexes: {e}")
    
    return indexes


def verify_redis_connection() -> Tuple[bool, str]:
    """Verify Redis connection."""
    try:
        if not REDIS_URL:
            return False, "REDIS_URL not set in environment"
        
        r = redis.from_url(REDIS_URL)
        r.ping()
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)


async def main():
    """Run all verification checks."""
    print_header("ClipBrain Database Setup Verification")
    
    # Check environment variables
    print_header("Environment Variables")
    print_result("SUPABASE_URL", bool(SUPABASE_URL), SUPABASE_URL[:50] + "..." if SUPABASE_URL else "Not set")
    print_result("SUPABASE_SERVICE_KEY", bool(SUPABASE_SERVICE_KEY), "***" if SUPABASE_SERVICE_KEY else "Not set")
    print_result("REDIS_URL", bool(REDIS_URL), REDIS_URL[:50] + "..." if REDIS_URL else "Not set")
    
    if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY, REDIS_URL]):
        print("\n❌ Missing required environment variables. Check your .env file.")
        return
    
    # Verify PostgreSQL connection
    print_header("PostgreSQL Connection")
    pg_connected, pg_message = await verify_postgres_connection()
    print_result("Database connection", pg_connected, pg_message)
    
    if not pg_connected:
        print("\n❌ Cannot connect to PostgreSQL. Fix connection issues before proceeding.")
        return
    
    # Connect and run detailed checks
    host = SUPABASE_URL.replace("https://", "").replace("http://", "")
    project_ref = host.split(".")[0]
    conn_str = f"postgresql://postgres:{SUPABASE_SERVICE_KEY}@db.{project_ref}.supabase.co:5432/postgres"
    
    conn = await asyncpg.connect(conn_str)
    
    try:
        # Check extensions
        print_header("PostgreSQL Extensions")
        extensions = await verify_extensions(conn)
        print_result("pgvector extension", extensions.get('vector', False))
        print_result("pg_trgm extension", extensions.get('pg_trgm', False))
        
        # Check tables
        print_header("Database Tables")
        tables = await verify_tables(conn)
        expected = {'videos', 'transcripts', 'transcript_chunks', 'notes', 'collections', 'collection_items'}
        
        for table in expected:
            print_result(f"Table: {table}", table in tables)
        
        # Check indexes
        print_header("Database Indexes")
        indexes = await verify_indexes(conn)
        for description, exists in indexes.items():
            print_result(description, exists)
        
    finally:
        await conn.close()
    
    # Verify Redis connection
    print_header("Redis Connection")
    redis_connected, redis_message = verify_redis_connection()
    print_result("Redis connection", redis_connected, redis_message)
    
    # Summary
    print_header("Summary")
    
    all_checks = [
        pg_connected,
        extensions.get('vector', False),
        extensions.get('pg_trgm', False),
        len(tables) == 6,
        all(indexes.values()),
        redis_connected
    ]
    
    if all(all_checks):
        print("✅ All checks passed! Your database setup is complete.")
        print("\nNext steps:")
        print("  1. Proceed to Task 2: Initialize backend FastAPI project")
        print("  2. Configure AI service API keys (Deepgram, Gemini)")
    else:
        print("❌ Some checks failed. Review the errors above and:")
        print("  1. Ensure migrations were run in Supabase SQL Editor")
        print("  2. Verify environment variables are correct")
        print("  3. Check Supabase and Upstash dashboards for service status")


if __name__ == "__main__":
    asyncio.run(main())
