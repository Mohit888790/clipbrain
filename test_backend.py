#!/usr/bin/env python3
"""Test backend imports and startup."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("Testing imports...")

try:
    print("1. Importing config...")
    from config import settings
    print(f"   ✅ Config loaded, API URL: {settings.supabase_url[:30]}...")
    
    print("2. Importing models...")
    from models import HealthResponse
    print("   ✅ Models imported")
    
    print("3. Importing database...")
    from database import db
    print("   ✅ Database imported")
    
    print("4. Importing supabase_client...")
    from supabase_client import supabase
    print("   ✅ Supabase client imported")
    
    print("5. Importing storage...")
    from storage import storage_service
    print("   ✅ Storage service imported")
    
    print("6. Importing services...")
    from services.url_utils import URLUtils
    from services.downloader import MediaDownloader
    from services.transcription import transcription_service
    from services.ai_service import ai_service
    print("   ✅ Services imported")
    
    print("7. Importing routes...")
    from routes import ingest, jobs, items, search
    print("   ✅ Routes imported")
    
    print("\n✅ All imports successful!")
    print("\nStarting FastAPI server...")
    
    from main import app
    print("✅ FastAPI app created")
    
    import uvicorn
    print("\n🚀 Starting server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
