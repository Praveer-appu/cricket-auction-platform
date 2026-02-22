from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['cricket_auction']

users = list(db.users.find({}, {'email': 1, 'is_admin': 1, 'role': 1, 'name': 1}))

if users:
    print(f"\nFound {len(users)} user(s) in database:\n")
    for user in users:
        print(f"Email: {user.get('email')}")
        print(f"Name: {user.get('name', 'N/A')}")
        print(f"Admin: {user.get('is_admin', False)}")
        print(f"Role: {user.get('role', 'N/A')}")
        print("-" * 40)
else:
    print("\nNo users found in database!")
    print("\nYou need to register a new user first.")
    print("To create an admin user, register with email: admin@example.com")
