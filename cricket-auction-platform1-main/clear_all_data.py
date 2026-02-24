"""
Clear all test data from database - players, teams, users, auctions
Keep only the admin account
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/cricket_auction")
client = MongoClient(MONGODB_URL)
db = client.get_database()

print("=" * 60)
print("CLEARING ALL TEST DATA")
print("=" * 60)

# Count before deletion
players_count = db.players.count_documents({})
teams_count = db.teams.count_documents({})
users_count = db.users.count_documents({"role": {"$ne": "admin"}})
auctions_count = db.auctions.count_documents({})
bids_count = db.bids.count_documents({})

print(f"\nBefore deletion:")
print(f"  Players: {players_count}")
print(f"  Teams: {teams_count}")
print(f"  Users (non-admin): {users_count}")
print(f"  Auctions: {auctions_count}")
print(f"  Bids: {bids_count}")

# Delete all players
result = db.players.delete_many({})
print(f"\n✅ Deleted {result.deleted_count} players")

# Delete all teams
result = db.teams.delete_many({})
print(f"✅ Deleted {result.deleted_count} teams")

# Delete all non-admin users
result = db.users.delete_many({"role": {"$ne": "admin"}})
print(f"✅ Deleted {result.deleted_count} non-admin users")

# Delete all auctions
result = db.auctions.delete_many({})
print(f"✅ Deleted {result.deleted_count} auctions")

# Delete all bids
result = db.bids.delete_many({})
print(f"✅ Deleted {result.deleted_count} bids")

# Check admin account
admin = db.users.find_one({"role": "admin"})
if admin:
    print(f"\n✅ Admin account preserved: {admin.get('email')}")
else:
    print("\n⚠️ WARNING: No admin account found!")

print("\n" + "=" * 60)
print("DATABASE CLEANED - Ready for fresh testing!")
print("=" * 60)
print("\nAdmin credentials:")
print("  Email: admin@cricket.com")
print("  Password: Admin@123456")
print("\nYou can now:")
print("  1. Create new teams from admin panel")
print("  2. Register new players")
print("  3. Start fresh auctions")
print("=" * 60)
