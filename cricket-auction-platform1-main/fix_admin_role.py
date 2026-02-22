from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['cricket_auction']

# Update admin user to have proper role
result = db.users.update_one(
    {"email": "admin@cricket.com"},
    {"$set": {
        "is_admin": True,
        "role": "admin"
    }}
)

if result.modified_count > 0:
    print("\n✅ Admin role updated successfully!")
else:
    print("\n✅ Admin role already set correctly!")

# Verify the update
user = db.users.find_one({"email": "admin@cricket.com"}, {"email": 1, "is_admin": 1, "role": 1})
print(f"\nCurrent admin user settings:")
print(f"Email: {user.get('email')}")
print(f"is_admin: {user.get('is_admin')}")
print(f"role: {user.get('role')}")
print("\nYou can now login and access the admin panel!")
