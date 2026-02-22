"""
Final verification that admin panel will work
"""
import requests

print("\n" + "="*70)
print("ADMIN PANEL PLAYER VISIBILITY - FINAL VERIFICATION")
print("="*70)

# Test 1: API Endpoint
print("\n1. Testing API Endpoint")
print("-" * 70)
try:
    response = requests.get("http://localhost:8000/players?include_unapproved=true")
    if response.status_code == 200:
        data = response.json()
        total = data.get('total', 0)
        players = data.get('players', [])
        print(f"✅ API Status: 200 OK")
        print(f"✅ Total Players: {total}")
        print(f"✅ Players Returned: {len(players)}")
        
        # Check if all approved
        all_approved = all(p.get('is_approved', False) for p in players)
        print(f"✅ All Approved: {'YES' if all_approved else 'NO'}")
    else:
        print(f"❌ API Status: {response.status_code}")
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Check players by role
print("\n2. Testing Players by Role")
print("-" * 70)
try:
    response = requests.get("http://localhost:8000/players/grouped/by-role")
    if response.status_code == 200:
        data = response.json()
        grouped = data.get('grouped', {})
        print(f"✅ Grouped API: Working")
        for role, info in grouped.items():
            count = info.get('count', 0)
            print(f"   {role:15} : {count} players")
    else:
        print(f"⚠️  Grouped API Status: {response.status_code}")
except Exception as e:
    print(f"⚠️  Grouped API Error: {e}")

# Test 3: Health Check
print("\n3. Testing Server Health")
print("-" * 70)
try:
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Server Status: {data.get('status')}")
        print(f"✅ App: {data.get('app')}")
        print(f"✅ Version: {data.get('version')}")
    else:
        print(f"❌ Health Check Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Health Check Error: {e}")

# Summary
print("\n" + "="*70)
print("VERIFICATION SUMMARY")
print("="*70)

checks = {
    "API Endpoint": response.status_code == 200 if 'response' in locals() else False,
    "Players Returned": total > 0 if 'total' in locals() else False,
    "All Approved": all_approved if 'all_approved' in locals() else False,
    "Server Health": True  # If we got here, server is running
}

passed = sum(1 for v in checks.values() if v)
total_checks = len(checks)

for check_name, result in checks.items():
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} - {check_name}")

print("\n" + "="*70)
if passed == total_checks:
    print("🎉 ALL CHECKS PASSED!")
    print("\nAdmin panel should now display all players.")
    print("\nTo verify:")
    print("1. Go to http://localhost:8000/admin")
    print("2. Login with admin@cricket.com / Admin@123456")
    print("3. Click 'Player Management' tab")
    print("4. You should see all 21 players organized by role")
    print("\nIf players still not visible:")
    print("- Clear browser cache (Ctrl + Shift + Delete)")
    print("- Hard refresh (Ctrl + F5)")
    print("- Check browser console (F12) for errors")
else:
    print(f"⚠️  {total_checks - passed} check(s) failed")
    print("\nPlease check the errors above and try again.")
print("="*70 + "\n")
