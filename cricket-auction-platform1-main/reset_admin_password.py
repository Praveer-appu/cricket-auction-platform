from pymongo import MongoClient
from core.security import hash_password

# New password
NEW_PASSWORD = "Admin@123456"

client = MongoClient('mongodb://localhost:27017')
db = client['cricket_auction']

# Update admin password
result = db.users.update_one(
    {"email": "admin@cricket.com"},
    {"$set": {"password_hash": hash_password(NEW_PASSWORD)}}
)

if result.modified_count > 0:
    print("\n✅ Admin password reset successfully!")
    print(f"\nEmail: admin@cricket.com")
    print(f"New Password: {NEW_PASSWORD}")
    print("\nYou can now login with these credentials.")
else:
    print("\n❌ Failed to reset password. Admin user not found.")
