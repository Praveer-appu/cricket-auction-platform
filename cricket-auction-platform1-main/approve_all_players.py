from pymongo import MongoClient
from datetime import datetime, timezone

client = MongoClient('mongodb://localhost:27017')
db = client['cricket_auction']

# Add is_approved field to all players that don't have it
result = db.players.update_many(
    {"is_approved": {"$exists": False}},
    {"$set": {
        "is_approved": True,
        "updated_at": datetime.now(timezone.utc)
    }}
)

# Set base prices for players without one
price_result = db.players.update_many(
    {"base_price": None},
    {"$set": {
        "base_price": 50000,
        "base_price_status": "approved",
        "updated_at": datetime.now(timezone.utc)
    }}
)

# Also approve any that are explicitly False
approve_result = db.players.update_many(
    {"is_approved": False},
    {"$set": {
        "is_approved": True,
        "updated_at": datetime.now(timezone.utc)
    }}
)

print(f"\n✅ Added is_approved field to {result.modified_count} players")
print(f"✅ Approved {approve_result.modified_count} players")
print(f"✅ Set base price for {price_result.modified_count} players")

# Show summary
total = db.players.count_documents({})
approved = db.players.count_documents({"is_approved": True})
with_price = db.players.count_documents({"base_price": {"$ne": None}})

print(f"\n📊 Summary:")
print(f"   Total players: {total}")
print(f"   Approved: {approved}")
print(f"   With base price: {with_price}")
print(f"\n🎉 All players are now visible in the admin panel!")
