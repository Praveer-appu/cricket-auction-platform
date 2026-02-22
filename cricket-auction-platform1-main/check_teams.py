from pymongo import MongoClient
from core.security import hash_password

client = MongoClient('mongodb://localhost:27017')
db = client['cricket_auction']

print("\n" + "="*60)
print("TEAMS IN DATABASE")
print("="*60)

teams = list(db.teams.find({}))

if teams:
    print(f"\nFound {len(teams)} team(s):\n")
    for i, team in enumerate(teams, 1):
        print(f"{i}. Team: {team.get('name')}")
        print(f"   Username: {team.get('username')}")
        print(f"   Budget: ₹{team.get('budget', 0):,}")
        print(f"   Has Password: {'Yes' if team.get('hashed_password') else 'No'}")
        print(f"   ID: {team.get('_id')}")
        print()
else:
    print("\n❌ No teams found in database!")
    print("\nCreating sample teams...")
    
    # Create 3 sample teams
    sample_teams = [
        {
            "name": "Mumbai Indians",
            "username": "mumbai",
            "hashed_password": hash_password("mumbai123"),
            "budget": 10000000,
            "remaining_purse": 10000000,
            "players": []
        },
        {
            "name": "Chennai Super Kings",
            "username": "chennai",
            "hashed_password": hash_password("chennai123"),
            "budget": 10000000,
            "remaining_purse": 10000000,
            "players": []
        },
        {
            "name": "Royal Challengers",
            "username": "rcb",
            "hashed_password": hash_password("rcb123"),
            "budget": 10000000,
            "remaining_purse": 10000000,
            "players": []
        }
    ]
    
    db.teams.insert_many(sample_teams)
    print("✅ Created 3 sample teams!")
    print("\nTeam Login Credentials:")
    print("1. Username: mumbai, Password: mumbai123")
    print("2. Username: chennai, Password: chennai123")
    print("3. Username: rcb, Password: rcb123")

print("\n" + "="*60)
print("TEAM LOGIN CREDENTIALS")
print("="*60)
print("\nIf you want to login as a team, use:")
print("- Username: mumbai, Password: mumbai123")
print("- Username: chennai, Password: chennai123")
print("- Username: rcb, Password: rcb123")
print("\nNote: 'Virat' is not a team username.")
print("="*60 + "\n")
