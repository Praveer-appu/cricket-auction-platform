# Fresh Start Guide - Clean Database Ready for Testing

## What Was Done

### 1. Database Cleanup ✅
All test data has been removed:
- **9 players** deleted
- **4 teams** deleted  
- **16 non-admin users** deleted
- **0 auctions** deleted
- **0 bids** deleted
- **2 uploaded photos** deleted

### 2. Admin Account Preserved ✅
The admin account is still available:
- **Email**: admin@cricket.com
- **Password**: Admin@123456

### 3. Auction Timer Updated ✅
Changed from 30 seconds to **90 seconds** per player
- Updated in `core/config.py`: `AUCTION_TIMER_SECONDS = 90`
- Updated in `routers/admin.py` to use the config value

## Current State

### Database
- **Empty** - No players, teams, or users (except admin)
- **Ready** for fresh data entry

### Server
- **Running** on http://localhost:8000
- **Auction timer**: 90 seconds per player
- **Photo upload**: Mandatory, max 500KB

## How to Start Testing

### Step 1: Login as Admin
1. Go to http://localhost:8000
2. Click "Admin Login"
3. Email: `admin@cricket.com`
4. Password: `Admin@123456`

### Step 2: Create Teams
From the admin panel:
1. Go to "Team Management" tab
2. Click "Add New Team"
3. Fill in team details:
   - Team name
   - Username (for login)
   - Password
   - Budget (e.g., ₹10,000,000)
4. Repeat for all teams you want to create

### Step 3: Register Players
You can register players in two ways:

**Option A: As a User (Recommended)**
1. Logout from admin
2. Click "User Login" → "Register here"
3. Create a user account
4. Login and click "Register as a Player"
5. Fill in player details:
   - Full name
   - Role (Batsman/Bowler/All-Rounder/Wicketkeeper)
   - Category (Faculty/Student/Alumni)
   - Age, batting style, bowling style
   - **Photo (MANDATORY, max 500KB)**
   - Bio/achievements
6. Submit - player is auto-approved

**Option B: From Admin Panel**
1. Login as admin
2. Go to "Player Management" tab
3. Click "Add Player"
4. Fill in details and upload photo

### Step 4: Start Auction
1. Login as admin
2. Go to "Live Auction" tab
3. Click "Set Next Player"
4. Select a player from the list
5. Click "Start Auction"
6. **Timer will run for 90 seconds**

### Step 5: Teams Bid
1. Login as team (use credentials you created)
2. Go to "Browse Players" tab to see available players
3. When admin starts auction, you'll see the live player
4. Enter bid amount and click "Place Bid"
5. You have 90 seconds to bid before auto-close

## Important Notes

### Photo Upload Requirements
- **Mandatory** for all player registrations
- **Maximum size**: 500KB
- **Formats**: JPG, PNG, WebP
- **Validation**: Both client-side and server-side
- **Storage**: Local (development) or Cloudinary (production)

### Auction Timer
- **Duration**: 90 seconds per player
- **Auto-close**: Auction automatically closes when timer expires
- **Reset**: Timer resets to 90 seconds on each new bid
- **Display**: Shows countdown on both admin and team dashboards

### Team Dashboard
- **Protocol**: Uses HTTP for localhost, HTTPS for production
- **Auto-refresh**: Updates every 3 seconds
- **Real-time**: WebSocket connection for live updates
- **Cache**: Clear browser cache (Ctrl+Shift+Delete) if issues occur

## Cleanup Scripts

If you need to clean up again in the future:

### Clear All Data
```bash
python clear_all_data.py
```
Removes all players, teams, users (except admin), auctions, and bids.

### Clear Uploaded Photos
```bash
python clear_uploaded_photos.py
```
Removes all uploaded player photos from `static/uploads/players/`.

## Testing Checklist

- [ ] Admin can login
- [ ] Admin can create teams
- [ ] Users can register
- [ ] Users can register as players with photos
- [ ] Teams can login
- [ ] Teams can see available players
- [ ] Admin can start auction
- [ ] Timer shows 90 seconds
- [ ] Teams can place bids
- [ ] Timer resets on new bid
- [ ] Auction auto-closes after 90 seconds
- [ ] Player photos display correctly
- [ ] Team dashboard loads properly

## Troubleshooting

### Teams can't see players
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Check that players are registered and approved

### Timer not showing 90 seconds
- Server was restarted with new config
- Should show 90 seconds on next auction start

### Photos not uploading
- Check file size is under 500KB
- Check file format is JPG/PNG/WebP
- For production, configure Cloudinary environment variables

## Server Status

✅ Server running on http://0.0.0.0:8000
✅ Database cleaned and ready
✅ Auction timer set to 90 seconds
✅ Photo upload configured (mandatory, 500KB max)

Ready for testing!
