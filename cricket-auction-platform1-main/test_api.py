import requests
import json

# Test the players API endpoint
url = "http://localhost:8000/players?include_unapproved=true"

try:
    response = requests.get(url)
    data = response.json()
    
    print(f"\n{'='*60}")
    print("TESTING /players API ENDPOINT")
    print(f"{'='*60}\n")
    
    print(f"Status Code: {response.status_code}")
    print(f"Total Players: {data.get('total', 0)}")
    print(f"Players Returned: {len(data.get('players', []))}")
    
    print(f"\n{'='*60}")
    print("FIRST 5 PLAYERS:")
    print(f"{'='*60}\n")
    
    for i, player in enumerate(data.get('players', [])[:5], 1):
        print(f"{i}. {player.get('name')}")
        print(f"   Role: {player.get('role', 'N/A')}")
        print(f"   Category: {player.get('category', 'N/A')}")
        print(f"   Approved: {player.get('is_approved', False)}")
        print(f"   Base Price: ₹{player.get('base_price', 0):,}")
        print()
    
    # Check if all are approved
    all_approved = all(p.get('is_approved', False) for p in data.get('players', []))
    print(f"{'='*60}")
    print(f"All players approved: {'✅ YES' if all_approved else '❌ NO'}")
    print(f"{'='*60}\n")
    
except Exception as e:
    print(f"Error: {e}")
