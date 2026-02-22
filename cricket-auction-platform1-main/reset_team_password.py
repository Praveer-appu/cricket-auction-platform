from pymongo import MongoClient
from core.security import hash_password

client = MongoClient('mongodb://localhost:27017')
db = client['cricket_auction']

# Reset password for team with username 'virat'
NEW_PASSWORD = "virat123"

result = db.teams.update_one(
    {"username": "virat"},
    {"$set": {"hashed_password": hash_password(NEW_PASSWORD)}}
)

if result.modified_count > 0:
    print("\n✅ Password reset successfully!")
    print(f"\nTeam Login Credentials:")
    print(f"   Username: virat")
    print(f"   Password: {NEW_PASSWORD}")
    print(f"\n⚠️  Note: Username is case-sensitive. Use lowercase 'virat', not 'Virat'")
else:
    print("\n❌ Team with username 'virat' not found or password already set")

# Also update other teams to have usernames and passwords
print("\n" + "="*60)
print("Updating all teams with usernames and passwords...")
print("="*60)

teams_to_update = [
    {"name": "Royal Challengers", "username": "royal", "password": "royal123"},
    {"name": "Super Kings", "username": "kings", "password": "kings123"},
    {"name": "Mumbai Warriors", "username": "mumbai", "password": "mumbai123"}
]

for team_data in teams_to_update:
    result = db.teams.update_one(
        {"name": team_data["name"]},
        {"$set": {
            "username": team_data["username"],
            "hashed_password": hash_password(team_data["password"])
        }}
    )
    if result.modified_count > 0:
        print(f"✅ Updated {team_data['name']}: username={team_data['username']}, password={team_data['password']}")

print("\n" + "="*60)
print("ALL TEAM LOGIN CREDENTIALS")
print("="*60)
print("\n1. Username: virat, Password: virat123")
print("2. Username: royal, Password: royal123")
print("3. Username: kings, Password: kings123")
print("4. Username: mumbai, Password: mumbai123")
print("\n⚠️  Remember: Usernames are case-sensitive!")
print("="*60 + "\n")
