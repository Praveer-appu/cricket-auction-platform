# 🚀 Cricket Auction Platform - Access Guide

## ✅ Server Status: RUNNING

**Server URL**: http://localhost:8000  
**Status**: ✅ Online  
**ML Predictions**: ✅ Enabled  
**Process ID**: 22968

---

## 🌐 Access URLs

### 1. Home Page (Landing Page)
```
http://localhost:8000
```
- Beautiful landing page with features
- Login/Register options
- Role selection (Admin/Team/Player)

### 2. Admin Panel
```
http://localhost:8000/admin
```
**Login Credentials:**
- Email: `admin@cricket.com`
- Password: `Admin@123456`

**Features:**
- ✅ Auction Control (Start/Stop/Timer)
- ✅ Player Management with ML Predictions
- ✅ Team Management
- ✅ Live Auction Monitor
- ✅ Analytics & Reports
- ✅ Security Dashboard

### 3. Team Dashboard
```
http://localhost:8000/team-dashboard
```
**Note:** You need to create team accounts first

**Features:**
- ✅ Browse Players with ML Predictions
- ✅ Live Bidding
- ✅ My Squad Management
- ✅ Budget Tracking
- ✅ Statistics & Charts
- ✅ Team Chat
- ✅ Player Wishlist

### 4. User Dashboard (Player Registration)
```
http://localhost:8000/user-dashboard
```
**Features:**
- ✅ Player Registration
- ✅ Photo Upload (mandatory, max 500KB)
- ✅ Manual Base Price Entry
- ✅ Profile Management

---

## 🎯 Quick Start Guide

### Step 1: Access the Platform
1. Open your browser
2. Go to: http://localhost:8000
3. You'll see the landing page

### Step 2: Login as Admin
1. Click "Admin Login" or go to http://localhost:8000/admin
2. Enter credentials:
   - Email: `admin@cricket.com`
   - Password: `Admin@123456`
3. You're now in the Admin Control Room!

### Step 3: Create Teams
1. In Admin Panel, go to "Team Management" tab
2. Click "Add New Team"
3. Fill in team details:
   - Team Name (e.g., "Royal Challengers")
   - Username (e.g., "royal")
   - Password (e.g., "royal123")
   - Budget (e.g., 100,00,000)
4. Click "Create Team"
5. Repeat for more teams

### Step 4: Register Players
1. Open new browser tab
2. Go to: http://localhost:8000
3. Click "Player Registration"
4. Fill in player details:
   - Name
   - Age
   - Role (Batsman/Bowler/All-Rounder/Wicketkeeper)
   - Category (Faculty/Student/Alumni)
   - Base Price (manual entry, min ₹10,000)
   - Photo (mandatory, max 500KB)
   - Bio/Achievements
5. Click "Register"
6. Player is auto-approved!

### Step 5: View ML Predictions
1. Login as Admin
2. Go to "Player Management" tab
3. You'll see ML prediction badges on player cards:
   - "🤖 AI: ₹XX,XX,XXX"
4. These predictions help you set fair base prices

### Step 6: Start Auction
1. In Admin Panel, go to "Auction Control" tab
2. Select a player from dropdown
3. Click "Set Live Player"
4. 90-second timer starts automatically
5. Teams can now bid!

### Step 7: Team Bidding
1. Login as a team (use credentials you created)
2. Go to Team Dashboard
3. You'll see the live player
4. Enter bid amount
5. Click "Place Bid"
6. Watch real-time updates!

---

## 🤖 ML Predictions Features

### Where to See ML Predictions

#### 1. Team Dashboard
- **Location**: Browse Players tab
- **Display**: Player cards show "🤖 AI: ₹XX,XX,XXX"
- **Details**: Click player card to see full prediction modal with:
  - Predicted price
  - Confidence range (min-max)
  - Difference vs base price
  - Model name

#### 2. Admin Panel
- **Location**: Player Management tab
- **Display**: ML badges on all player cards
- **Purpose**: Helps set fair base prices

### How ML Predictions Work
1. System analyzes player statistics:
   - Matches played
   - Batting average
   - Strike rate
   - Wickets
   - Economy rate
   - Recent performance
   - Player type

2. Random Forest model predicts auction price

3. Shows prediction with ±15% confidence range

4. Color-coded indicators:
   - 📈 Green: Predicted > Base (good value)
   - 📉 Red: Predicted < Base (overpriced)

---

## 📊 Test ML Predictions

### Via Browser
1. Login as team or admin
2. Look for player cards
3. ML badges should show "🤖 AI: Loading..."
4. Then update to "🤖 AI: ₹XX,XX,XXX"

### Via API
```bash
# Test prediction
python test_ml_simple.py

# Expected output:
# Success: true
# Predicted Price: ₹19,63,093
# Confidence Range: ₹16,68,629 - ₹22,57,557
```

### Via Browser Console
1. Open browser (F12)
2. Go to Console tab
3. Type:
```javascript
fetch('http://localhost:8000/ml/model-info')
  .then(r => r.json())
  .then(d => console.log(d))
```
4. Should show model info

---

## 🎨 UI Features

### Landing Page
- Modern gradient design
- Feature cards with icons
- Smooth animations
- Responsive layout

### Admin Panel
- Dark theme with gold accents
- Real-time statistics
- Live auction monitor
- Player cards with ML predictions
- Team management
- Analytics charts

### Team Dashboard
- Team overview with budget tracking
- Live auction panel
- Player browsing with filters
- My squad management
- Statistics and charts
- Team chat
- Player wishlist
- Comparison tools

---

## 🔧 Configuration

### Auction Settings
- **Timer**: 90 seconds per player
- **Photo Upload**: Mandatory, max 500KB
- **Base Price**: Manual entry by player
- **Auto-Approval**: Enabled

### ML Settings
- **Model**: Random Forest
- **Accuracy**: 75.31%
- **Confidence**: ±15%
- **Training Data**: 500 sample players

---

## 🐛 Troubleshooting

### ML Predictions Not Showing
1. Clear browser cache: Ctrl+Shift+Delete
2. Hard refresh: Ctrl+F5
3. Check console for errors (F12)
4. Verify server shows "✅ ML Predictions API enabled"

### Can't Login
1. Check credentials are correct
2. Admin: admin@cricket.com / Admin@123456
3. Teams: Use credentials you created
4. Clear cookies and try again

### Player Not Visible
1. Check player is approved (auto-approval enabled)
2. Refresh the page
3. Check filters are not hiding player

### Bidding Not Working
1. Ensure auction is live (player selected)
2. Check you have sufficient budget
3. Verify bid amount is higher than current bid
4. Check WebSocket connection (should auto-reconnect)

---

## 📱 Browser Compatibility

### Recommended Browsers
- ✅ Chrome/Edge (Latest)
- ✅ Firefox (Latest)
- ✅ Safari (Latest)

### Mobile Support
- ✅ Responsive design
- ✅ Touch-friendly
- ✅ Optimized layouts

---

## 🎯 Key Features Summary

### For Admin
- ✅ Complete auction control
- ✅ Player management with ML predictions
- ✅ Team management
- ✅ Live monitoring
- ✅ Analytics and reports
- ✅ Security dashboard

### For Teams
- ✅ Browse players with ML predictions
- ✅ Real-time bidding
- ✅ Budget tracking
- ✅ Squad management
- ✅ Statistics
- ✅ Team chat
- ✅ Wishlist

### For Players
- ✅ Easy registration
- ✅ Photo upload
- ✅ Profile management
- ✅ Auto-approval

---

## 📞 Quick Commands

### Start Server
```bash
cd cricket-auction-platform1-main
python main_new.py
```

### Test ML
```bash
python test_ml_simple.py
```

### Retrain Model
```bash
python ml_models/train.py
```

### Clear Data
```bash
python clear_all_data.py
```

---

## 🎉 You're All Set!

Everything is running and ready to use:

1. ✅ Server: http://localhost:8000
2. ✅ ML Predictions: Working
3. ✅ Admin Panel: Ready
4. ✅ Team Dashboard: Ready
5. ✅ Player Registration: Ready

**Start by logging in as admin and creating some teams!**

---

**Server Status**: 🟢 ONLINE  
**ML Status**: 🟢 ENABLED  
**Last Updated**: February 22, 2026, 5:11 PM
