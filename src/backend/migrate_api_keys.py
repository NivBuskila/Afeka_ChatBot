import os
import asyncio
import sys
from pathlib import Path
from supabase import create_client, Client
from datetime import datetime
import dotenv

# טעינת משתני סביבה מהקובץ .env
dotenv.load_dotenv()

# אם לא עובד, נסה לטעון מהנתיב הנכון
if not os.getenv("SUPABASE_URL"):
    # טען מתיקיית הroot
    root_path = Path(__file__).parent.parent.parent
    env_file = root_path / ".env"
    if env_file.exists():
        dotenv.load_dotenv(env_file)
        print(f"✅ Loaded .env from: {env_file}")
    else:
        print(f"❌ .env not found at: {env_file}")

async def migrate_api_keys():
    """העברת מפתחות API מ-.env לדאטה בייס"""
    
    # בדיקת משתני סביבה
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    print(f"🔍 SUPABASE_URL: {supabase_url}")
    print(f"🔍 SUPABASE_KEY: {supabase_key[:20] if supabase_key else 'None'}...")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase environment variables!")
        print("Make sure SUPABASE_URL and SUPABASE_KEY are set in .env")
        return
    
    # התחברות לSupabase
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return
    
    # איסוף מפתחות מ-.env
    api_keys = []
    
    # מפתח יחיד
    main_key = os.getenv('GEMINI_API_KEY')
    if main_key:
        api_keys.append({
            "key_name": "GEMINI_API_KEY_MAIN",
            "api_key": main_key,
            "provider": "gemini",
            "is_active": True,
            "daily_limit_tokens": 1000000,
            "daily_limit_requests": 1500,
            "minute_limit_requests": 15
        })
    
    # מפתחות מרובים
    for i in range(1, 8):
        key = os.getenv(f'GEMINI_API_KEY_{i}')
        if key and key not in [k["api_key"] for k in api_keys]:  # מניעת כפילויות
            api_keys.append({
                "key_name": f"GEMINI_API_KEY_{i}",
                "api_key": key,
                "provider": "gemini",
                "is_active": True,
                "daily_limit_tokens": 1000000,
                "daily_limit_requests": 1500,
                "minute_limit_requests": 15
            })
    
    print(f"🔑 Found {len(api_keys)} unique API keys")
    
    if not api_keys:
        print("❌ No API keys found in environment variables!")
        return
    
    # בדיקת טבלה
    try:
        # בדוק אם הטבלה קיימת
        existing_keys = supabase.table("api_keys").select("key_name").execute()
        print(f"📊 Found {len(existing_keys.data)} existing keys in database")
    except Exception as e:
        print(f"❌ Error accessing api_keys table: {e}")
        print("Make sure you ran the database migration first!")
        return
    
    # העברה לדאטה בייס
    success_count = 0
    for i, key_data in enumerate(api_keys):
        try:
            # בדוק אם המפתח כבר קיים
            existing = supabase.table("api_keys")\
                .select("id")\
                .eq("api_key", key_data["api_key"])\
                .execute()
            
            if not existing.data:
                # הוסף מפתח חדש
                result = supabase.table("api_keys").insert(key_data).execute()
                print(f"✅ Added key {i+1}: {key_data['key_name']}")
                success_count += 1
            else:
                print(f"⚠️  Key {i+1} already exists: {key_data['key_name']}")
                
        except Exception as e:
            print(f"❌ Error adding key {i+1}: {e}")
    
    print(f"\n🎯 Migration completed: {success_count}/{len(api_keys)} keys added")

if __name__ == "__main__":
    print("🚀 Starting API Keys Migration...")
    asyncio.run(migrate_api_keys())
