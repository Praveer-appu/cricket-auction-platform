import requests
import json

response = requests.get("http://localhost:8000/players?include_unapproved=true")
data = response.json()

print("\n" + "="*70)
print("API RESPONSE STRUCTURE")
print("="*70)
print(f"\nStatus Code: {response.status_code}")
print(f"\nResponse Keys: {list(data.keys())}")
print(f"\nFull Response Structure:")
print(json.dumps({
    "total": data.get("total"),
    "page": data.get("page"),
    "limit": data.get("limit"),
    "pages": data.get("pages"),
    "players_count": len(data.get("players", [])),
    "first_player_sample": data.get("players", [{}])[0] if data.get("players") else None
}, indent=2))

print(f"\n{'='*70}")
print("JAVASCRIPT COMPATIBILITY CHECK")
print("="*70)
print(f"\ndata.players exists: {('players' in data)}")
print(f"data.players is array: {isinstance(data.get('players'), list)}")
print(f"data.players length: {len(data.get('players', []))}")

if data.get('players'):
    print(f"\nFirst player structure:")
    first = data['players'][0]
    print(f"  _id: {first.get('_id')}")
    print(f"  name: {first.get('name')}")
    print(f"  role: {first.get('role')}")
    print(f"  category: {first.get('category')}")
    print(f"  is_approved: {first.get('is_approved')}")
    print(f"  base_price: {first.get('base_price')}")
    print(f"  status: {first.get('status')}")
