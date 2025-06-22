import os
import asyncio
from pathlib import Path
from supabase import create_client, Client
from typing import Dict, Any, List
import dotenv

_ = dotenv.load_dotenv()

if not os.getenv("SUPABASE_URL"):
    root_path = Path(__file__).parent.parent.parent
    env_file = root_path / ".env"
    if env_file.exists():
        _ = dotenv.load_dotenv(env_file)
        print(f"Loaded .env from: {env_file}")
    else:
        print(f".env not found at: {env_file}")

async def migrate_api_keys() -> None:
    """Migrate API keys from .env to database"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_KEY: {supabase_key[:20] if supabase_key else 'None'}...")
    
    if not supabase_url or not supabase_key:
        print("Missing Supabase environment variables!")
        print("Make sure SUPABASE_URL and SUPABASE_KEY are set in .env")
        return
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("Connected to Supabase")
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}")
        return
    
    api_keys: List[Dict[str, Any]] = []
    
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
    
    for i in range(1, 8):
        key = os.getenv(f'GEMINI_API_KEY_{i}')
        if key and key not in [k["api_key"] for k in api_keys]:
            api_keys.append({
                "key_name": f"GEMINI_API_KEY_{i}",
                "api_key": key,
                "provider": "gemini",
                "is_active": True,
                "daily_limit_tokens": 1000000,
                "daily_limit_requests": 1500,
                "minute_limit_requests": 15
            })
    
    print(f"Found {len(api_keys)} unique API keys")
    
    if not api_keys:
        print("No API keys found in environment variables!")
        return
    
    try:
        existing_keys_response = supabase.table("api_keys").select("key_name").execute()
        existing_keys_data = existing_keys_response.data or []
        print(f"Found {len(existing_keys_data)} existing keys in database")
    except Exception as e:
        print(f"Error accessing api_keys table: {e}")
        print("Make sure you ran the database migration first!")
        return
    
    success_count = 0
    for i, key_data in enumerate(api_keys):
        try:
            existing_response = supabase.table("api_keys")\
                .select("id")\
                .eq("api_key", key_data["api_key"])\
                .execute()
            
            existing_data = existing_response.data or []
            if not existing_data:
                _ = supabase.table("api_keys").insert(key_data).execute()
                print(f"Added key {i+1}: {key_data['key_name']}")
                success_count += 1
            else:
                print(f"Key {i+1} already exists: {key_data['key_name']}")
                
        except Exception as e:
            print(f"Error adding key {i+1}: {e}")
    
    print(f"\nMigration completed: {success_count}/{len(api_keys)} keys added")

if __name__ == "__main__":
    print("Starting API Keys Migration...")
    asyncio.run(migrate_api_keys())