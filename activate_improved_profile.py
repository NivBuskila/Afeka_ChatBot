import requests
import json

def activate_improved_profile():
    print("🔄 Activating improved profile via server API...")
    
    url = "http://localhost:8000/api/rag/profiles/improved/activate"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, timeout=30)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile activated successfully:")
            print(f"   Response: {data}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.ConnectionError:
        print("❌ Connection failed - server may not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    activate_improved_profile() 