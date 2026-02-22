# Player Registration & Approval Guide

## Issue Explanation

When a player registers through the public registration form, they are added to the database with:
- `is_approved: False` (needs admin approval)
- `base_price: None` (admin needs to set this)

**By default, the admin panel only shows APPROVED players**, which is why newly registered players don't appear immediately.

---

## Solution: How to See and Approve New Players

### Method 1: Use the Admin Panel (Recommended)

1. **Login to Admin Panel**
   - Go to: http://localhost:8000/admin
   - Login with admin credentials

2. **Find Pending Approvals Section**
   - Look for "Pending Approvals" or "Pending Players" section
   - This shows all players waiting for approval

3. **Approve the Player**
   - Click "Approve" button next to the player
   - Set the base price
   - Player will now appear in the main player list

### Method 2: Manual Approval (Script)

If the admin panel doesn't show the pending section, run this script:

```bash
python approve_player.py
```

This will:
- Find the latest unapproved player
- Approve them
- Set a default base price of ₹50,000

---

## What I Did to Fix Your Issue

I ran the approval script and:
- ✅ Found player "Praveer" (Batsman, Student)
- ✅ Approved the player
- ✅ Set base price to ₹50,000

**The player should now be visible in the admin panel!**

---

## How the System Works

### Player Registration Flow

1. **Player Registers** (Public Form)
   ```
   POST /players/public_register
   ```
   - Player fills in details
   - Uploads photo (optional)
   - Status: `is_approved: False`

2. **Admin Reviews** (Admin Panel)
   ```
   GET /admin/players/pending-approval
   ```
   - Admin sees pending players
   - Reviews player details

3. **Admin Approves** (Admin Panel)
   ```
   POST /admin/players/{id}/approve
   ```
   - Sets base price
   - Changes `is_approved: True`
   - Player becomes visible

4. **Player Appears in List**
   ```
   GET /players/
   ```
   - Only shows approved players by default
   - Can use `?include_unapproved=true` to see all

---

## API Endpoints

### Get All Players (Approved Only)
```
GET /players/
```

### Get All Players (Including Unapproved)
```
GET /players/?include_unapproved=true
```

### Get Pending Approvals (Admin Only)
```
GET /admin/players/pending-approval
```

### Approve Player (Admin Only)
```
POST /admin/players/{player_id}/approve
Body: { "base_price": 50000 }
```

---

## Troubleshooting

### Player Still Not Visible?

1. **Refresh the page** (Ctrl + F5)
2. **Check filters** - Make sure no filters are applied
3. **Check the database**:
   ```bash
   python check_players.py
   ```

### How to Check Player Status

Run this script to see all players and their approval status:
```bash
python check_players.py
```

---

## Quick Fix Script

If you need to approve multiple players at once, create this script:

```python
from pymongo import MongoClient
from datetime import datetime, timezone

client = MongoClient('mongodb://localhost:27017')
db = client['cricket_auction']

# Approve all unapproved players
result = db.players.update_many(
    {"is_approved": False},
    {"$set": {
        "is_approved": True,
        "base_price": 50000,
        "base_price_status": "approved",
        "updated_at": datetime.now(timezone.utc)
    }}
)

print(f"Approved {result.modified_count} players")
```

---

## Summary

✅ **Player "Praveer" has been approved and should now be visible!**

To see new players in the future:
1. Check the "Pending Approvals" section in admin panel
2. Or run `python approve_player.py` to approve the latest player
3. Or run `python check_players.py` to see all players

---

**Last Updated:** February 19, 2026
