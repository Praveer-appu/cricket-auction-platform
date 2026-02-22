from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['cricket_auction']

# Get all players
players = list(db.players.find({}).sort('_id', -1))

print(f"\n{'='*60}")
print(f"TOTAL PLAYERS IN DATABASE: {len(players)}")
print(f"{'='*60}\n")

if players:
    print("Recent players:")
    for i, player in enumerate(players[:10], 1):
        print(f"\n{i}. Player Details:")
        print(f"   ID: {player.get('_id')}")
        print(f"   Name: {player.get('name', 'N/A')}")
        print(f"   Email: {player.get('email', 'N/A')}")
        print(f"   Status: {player.get('status', 'N/A')}")
        print(f"   Role: {player.get('role', 'N/A')}")
        print(f"   Category: {player.get('category', 'N/A')}")
        print(f"   Base Price: {player.get('base_price', 'N/A')}")
        print(f"   Auction Round: {player.get('auction_round', 'N/A')}")
        print(f"   Image Path: {player.get('image_path', 'N/A')}")
else:
    print("No players found in database!")

# Check the latest player
print(f"\n{'='*60}")
print("LATEST PLAYER (just registered):")
print(f"{'='*60}")
latest = db.players.find_one(sort=[('_id', -1)])
if latest:
    for key, value in latest.items():
        print(f"{key}: {value}")
else:
    print("No players found!")
