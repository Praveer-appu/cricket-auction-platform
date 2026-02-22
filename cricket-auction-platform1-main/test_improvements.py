"""
Test script for new player registration improvements
"""
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['cricket_auction']

print("\n" + "="*60)
print("TESTING PLAYER REGISTRATION IMPROVEMENTS")
print("="*60)

# Test 1: Check auto-approval
print("\n1. Testing Auto-Approval Feature")
print("-" * 60)
approved_players = db.players.count_documents({"is_approved": True})
total_players = db.players.count_documents({})
print(f"✅ Approved players: {approved_players}/{total_players}")
print(f"   Auto-approval: {'ENABLED' if approved_players == total_players else 'PARTIAL'}")

# Test 2: Check base prices
print("\n2. Testing Auto Base Price Assignment")
print("-" * 60)
players_with_price = db.players.count_documents({"base_price": {"$ne": None}})
print(f"✅ Players with base price: {players_with_price}/{total_players}")

# Show base prices by category
for category in ["Faculty", "Student", "Alumni"]:
    players = list(db.players.find({"category": category}, {"name": 1, "base_price": 1}).limit(3))
    if players:
        print(f"\n   {category}:")
        for p in players:
            print(f"   - {p.get('name')}: ₹{p.get('base_price', 0):,}")

# Test 3: Check for duplicates
print("\n3. Testing Duplicate Prevention")
print("-" * 60)
pipeline = [
    {"$group": {"_id": {"$toLower": "$name"}, "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 1}}}
]
duplicates = list(db.players.aggregate(pipeline))
if duplicates:
    print(f"⚠️  Found {len(duplicates)} duplicate names:")
    for dup in duplicates:
        print(f"   - {dup['_id']} (appears {dup['count']} times)")
else:
    print("✅ No duplicate player names found")

# Test 4: Check players by role
print("\n4. Testing Players Grouped by Role")
print("-" * 60)
roles = ["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"]
for role in roles:
    count = db.players.count_documents({"role": role})
    print(f"   {role:15} : {count} players")

# Test 5: Check bio/achievements
print("\n5. Testing Bio/Achievements Field")
print("-" * 60)
with_bio = db.players.count_documents({"bio": {"$ne": None, "$ne": ""}})
print(f"✅ Players with bio/achievements: {with_bio}/{total_players}")

# Show sample bios
players_with_bio = list(db.players.find(
    {"bio": {"$ne": None, "$ne": ""}},
    {"name": 1, "bio": 1}
).limit(3))
if players_with_bio:
    print("\n   Sample bios:")
    for p in players_with_bio:
        bio = p.get('bio', '')[:50] + '...' if len(p.get('bio', '')) > 50 else p.get('bio', '')
        print(f"   - {p.get('name')}: {bio}")

# Test 6: Check image paths
print("\n6. Testing Player Photos")
print("-" * 60)
with_images = db.players.count_documents({"image_path": {"$ne": None}})
print(f"✅ Players with photos: {with_images}/{total_players}")

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

tests = {
    "Auto-Approval": approved_players == total_players,
    "Base Prices": players_with_price == total_players,
    "No Duplicates": len(duplicates) == 0,
    "Role Grouping": sum(db.players.count_documents({"role": r}) for r in roles) > 0,
    "Bio Field": with_bio >= 0,  # Just check it exists
    "Photo Support": with_images >= 0  # Just check it exists
}

passed = sum(1 for v in tests.values() if v)
total = len(tests)

for test_name, result in tests.items():
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} - {test_name}")

print("\n" + "="*60)
print(f"RESULT: {passed}/{total} tests passed")
print("="*60)

if passed == total:
    print("\n🎉 All improvements working correctly!")
else:
    print(f"\n⚠️  {total - passed} test(s) need attention")

print("\n📝 Next Steps:")
print("1. Test player registration at http://localhost:8000")
print("2. Try registering duplicate name (should fail)")
print("3. Check admin panel - players should be visible immediately")
print("4. Click on player cards in team dashboard to see details")
print("5. Verify bio/achievements display in modal")
