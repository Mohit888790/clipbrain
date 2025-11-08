#!/usr/bin/env python3
"""Test all service connections."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from database import db
from storage import storage_service
import redis.asyncio as redis
import httpx


async def test_redis():
    """Test Redis connection."""
    print("\n" + "=" * 60)
    print("Testing Redis Connection")
    print("=" * 60)
    
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True)
        await r.ping()
        print("✅ Redis connection successful")
        
        # Test set/get
        await r.set("test_key", "test_value")
        value = await r.get("test_key")
        assert value == "test_value"
        print("✅ Redis read/write successful")
        
        await r.delete("test_key")
        await r.close()
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


async def test_database():
    """Test database connection via Supabase REST API."""
    print("\n" + "=" * 60)
    print("Testing Database Connection (REST API)")
    print("=" * 60)
    
    try:
        # Test REST API connection
        url = f"{settings.supabase_url}/rest/v1/"
        headers = {
            "apikey": settings.supabase_service_key,
            "Authorization": f"Bearer {settings.supabase_service_key}",
        }
        
        async with httpx.AsyncClient() as client:
            # Try to query videos table (should work even if empty)
            response = await client.get(
                f"{url}videos?limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ Database REST API connection successful")
                
                # Check all tables exist by trying to query them
                expected_tables = [
                    'videos', 'transcripts', 'transcript_chunks',
                    'notes', 'collections', 'collection_items'
                ]
                
                missing = []
                for table in expected_tables:
                    resp = await client.get(
                        f"{url}{table}?limit=0",
                        headers=headers
                    )
                    if resp.status_code != 200:
                        missing.append(table)
                
                if missing:
                    print(f"⚠️  Missing tables: {missing}")
                    print("   Run migrations in Supabase SQL Editor")
                    return False
                else:
                    print(f"✅ All {len(expected_tables)} tables exist")
                    return True
            else:
                print(f"❌ Database connection failed (status: {response.status_code})")
                return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_storage():
    """Test Supabase Storage connection."""
    print("\n" + "=" * 60)
    print("Testing Supabase Storage")
    print("=" * 60)
    
    try:
        # Test bucket access by listing (will fail if bucket doesn't exist)
        url = f"{settings.supabase_url}/storage/v1/bucket/videos"
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_key}",
            "apikey": settings.supabase_service_key,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                print("✅ Storage bucket 'videos' exists")
                return True
            elif response.status_code == 404:
                print("❌ Storage bucket 'videos' not found")
                print("   Run migration: database/migrations/002_storage_setup.sql")
                return False
            else:
                print(f"⚠️  Unexpected response: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Storage connection failed: {e}")
        return False


async def test_deepgram():
    """Test Deepgram API key."""
    print("\n" + "=" * 60)
    print("Testing Deepgram API")
    print("=" * 60)
    
    try:
        url = "https://api.deepgram.com/v1/projects"
        headers = {
            "Authorization": f"Token {settings.deepgram_api_key}",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                print("✅ Deepgram API key valid")
                data = response.json()
                if data.get("projects"):
                    print(f"   Projects: {len(data['projects'])}")
                return True
            else:
                print(f"❌ Deepgram API key invalid (status: {response.status_code})")
                return False
    except Exception as e:
        print(f"❌ Deepgram API test failed: {e}")
        return False


async def test_gemini():
    """Test Gemini API key."""
    print("\n" + "=" * 60)
    print("Testing Gemini API")
    print("=" * 60)
    
    try:
        # Test with a simple embedding request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={settings.gemini_api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "model": "models/text-embedding-004",
                    "content": {
                        "parts": [{"text": "test"}]
                    }
                }
            )
            
            if response.status_code == 200:
                print("✅ Gemini API key valid")
                data = response.json()
                if "embedding" in data:
                    embedding_dim = len(data["embedding"]["values"])
                    print(f"   Embedding dimension: {embedding_dim}")
                return True
            else:
                print(f"❌ Gemini API key invalid (status: {response.status_code})")
                if response.status_code == 400:
                    print(f"   Error: {response.json()}")
                return False
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("ClipBrain Backend Connection Tests")
    print("=" * 60)
    
    results = {
        "Redis": await test_redis(),
        "Database": await test_database(),
        "Storage": await test_storage(),
        "Deepgram": await test_deepgram(),
        "Gemini": await test_gemini(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {service}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Backend is ready.")
        print("\nNext steps:")
        print("  1. Start the backend: cd backend && python main.py")
        print("  2. Test health endpoint: curl http://localhost:8000/healthz")
        print("  3. Proceed to Task 3: Implement media downloader service")
    else:
        print("\n⚠️  Some tests failed. Fix the issues above before proceeding.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
