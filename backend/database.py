"""Database connection management using asyncpg."""

import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from config import settings


class Database:
    """Database connection pool manager."""
    
    def __init__(self):
        self.pool: asyncpg.Pool | None = None
    
    async def connect(self):
        """Create database connection pool."""
        # Extract project ref from Supabase URL
        host = settings.supabase_url.replace("https://", "").replace("http://", "")
        project_ref = host.split(".")[0]
        
        # Construct PostgreSQL connection string using direct connection
        # Format: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
        dsn = (
            f"postgresql://postgres:{settings.supabase_service_key}"
            f"@db.{project_ref}.supabase.co:5432/postgres"
        )
        
        self.pool = await asyncpg.create_pool(
            dsn,
            min_size=2,
            max_size=10,
            command_timeout=60,
        )
        print("✅ Database connection pool created")
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            print("✅ Database connection pool closed")
    
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Acquire a connection from the pool."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args):
        """Execute a query without returning results."""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows."""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch a single row."""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch a single value."""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global database instance
db = Database()
