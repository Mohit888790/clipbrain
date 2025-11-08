#!/usr/bin/env python3
"""Quick verification that database is set up correctly."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("  ClipBrain Setup Verification")
print("=" * 60)

# Check environment variables
print("\n✓ Checking environment variables...")
required_vars = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY", 
    "REDIS_URL",
    "DEEPGRAM_API_KEY",
    "GEMINI_API_KEY"
]

missing = []
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"  ✅ {var}: {'*' * 20}")
    else:
        print(f"  ❌ {var}: NOT SET")
        missing.append(var)

if missing:
    print(f"\n❌ Missing variables: {', '.join(missing)}")
    print("\nPlease set these in your .env file")
    exit(1)

print("\n✅ All environment variables are set!")
print("\n" + "=" * 60)
print("Next Steps:")
print("=" * 60)
print("\n1. Run database migrations in Supabase SQL Editor:")
print("   - Open: https://app.supabase.com/project/ifzdryytyqfufmjzchrr/sql")
print("   - Run: database/migrations/001_initial_schema.sql")
print("   - Run: database/migrations/002_storage_setup.sql")
print("\n2. Install Python dependencies:")
print("   pip install asyncpg redis python-dotenv")
print("\n3. Run full verification:")
print("   python database/verify_setup.py")
print("\n4. Proceed to Task 2: Initialize backend FastAPI project")
print("\n" + "=" * 60)
