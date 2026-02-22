"""
Add database indexes for better query performance.
Run this once to optimize database queries.
"""
from database import db

print("=" * 60)
print("ADDING DATABASE INDEXES FOR PERFORMANCE")
print("=" * 60)

# Players collection indexes
print("\n📊 Creating indexes on 'players' collection...")
db.players.create_index([("status", 1)])
print("  ✓ Index on 'status'")

db.players.create_index([("auction_round", 1), ("status", 1)])
print("  ✓ Compound index on 'auction_round' + 'status'")

db.players.create_index([("role", 1), ("status", 1)])
print("  ✓ Compound index on 'role' + 'status'")

db.players.create_index([("final_team", 1), ("status", 1)])
print("  ✓ Compound index on 'final_team' + 'status'")

db.players.create_index([("category", 1)])
print("  ✓ Index on 'category'")

# Teams collection indexes
print("\n📊 Creating indexes on 'teams' collection...")
db.teams.create_index([("username", 1)], unique=True)
print("  ✓ Unique index on 'username'")

# Bid history indexes
print("\n📊 Creating indexes on 'bid_history' collection...")
db.bid_history.create_index([("player_id", 1)])
print("  ✓ Index on 'player_id'")

db.bid_history.create_index([("team_id", 1)])
print("  ✓ Index on 'team_id'")

db.bid_history.create_index([("timestamp", -1)])
print("  ✓ Index on 'timestamp' (descending)")

# Users collection indexes
print("\n📊 Creating indexes on 'users' collection...")
db.users.create_index([("email", 1)], unique=True)
print("  ✓ Unique index on 'email'")

db.users.create_index([("role", 1)])
print("  ✓ Index on 'role'")

print("\n" + "=" * 60)
print("✅ ALL INDEXES CREATED SUCCESSFULLY")
print("=" * 60)
print("\nDatabase queries should now be much faster!")
print("Dashboard load time should improve significantly.")
