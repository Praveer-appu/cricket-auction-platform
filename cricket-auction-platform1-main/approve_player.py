from pymongo import MongoClient
from datetime import datetime, timezone

client = MongoClient('mongodb://localhost:27017')
db = client['cricket_auction']

# Find the latest unapproved player
player = db.players.find_one({"is_approved": False}, sort=[('_id', -1)])

if player:
    print(f"\nFound unapproved player:")
    print(f"Name: {player.get('name')}")
    print(f"Role: {player.get('role')}")
    print(f"Category: {player.get('category')}")
    
    # Approve the player and set a default base price
    result = db.players.update_one(
        {"_id": player["_id"]},
        {"$set": {
            "is_approved": True,
            "base_price": 50000,  # Default base price
            "base_price_status": "approved",
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.modified_count > 0:
        print(f"\n✅ Player '{player.get('name')}' has been approved!")
        print(f"   Base Price set to: ₹50,000")
        print(f"\nThe player should now be visible in the admin panel.")
    else:
        print("\n❌ Failed to approve player")
else:
    print("\nNo unapproved players found!")
