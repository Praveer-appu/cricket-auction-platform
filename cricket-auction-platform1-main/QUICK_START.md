# 🚀 Quick Start Guide

## Prerequisites Check ✅

Before starting, make sure you have:
- ✅ Python 3.11+ installed
- ✅ MongoDB running on localhost:27017
- ✅ All dependencies installed (already done!)

---

## Start the Server

### Option 1: Simple Start
```bash
cd cricket-auction-platform1-main
python main_new.py
```

### Option 2: With Auto-reload (Development)
```bash
uvicorn main_new:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
✅ Application startup complete
```

---

## Access the Application

Open your browser and go to: **http://localhost:8000**

---

## Login

### Admin Login
- **Email:** `admin@cricket.com`
- **Password:** `Admin@123456`

After login, you'll have access to:
- Admin Dashboard
- Player Management
- Team Management
- Auction Control
- Reports & Analytics

---

## Quick Navigation

| What you want to do | Where to go |
|---------------------|-------------|
| Manage players and teams | http://localhost:8000/admin |
| Start/control auction | http://localhost:8000/admin (Auction tab) |
| Watch live auction | http://localhost:8000/live |
| View team details | http://localhost:8000/team/dashboard |
| API documentation | http://localhost:8000/docs |

---

## Common Tasks

### 1. Add a New Player
1. Go to Admin Dashboard
2. Click "Players" tab
3. Fill in player details
4. Set base price
5. Click "Add Player"

### 2. Create a Team
1. Go to Admin Dashboard
2. Click "Teams" tab
3. Enter team name and budget
4. Click "Create Team"

### 3. Start an Auction
1. Go to Admin Dashboard
2. Click "Auction" tab
3. Select a player
4. Click "Start Auction"
5. Teams can now bid in real-time

### 4. View Reports
1. Go to Admin Dashboard
2. Click "Reports" tab
3. Choose report type
4. Click "Export"

---

## Troubleshooting

### Server won't start
- Check if MongoDB is running: `mongod --version`
- Check if port 8000 is free
- Check for error messages in terminal

### Can't login
- Make sure you're using the correct credentials
- Clear browser cookies
- Check if server is running

### Page not loading
- Refresh the page (Ctrl+F5)
- Check browser console for errors
- Verify server is running

### "Connection refused" error
- Server might have stopped
- Restart with: `python main_new.py`

---

## Stop the Server

Press **Ctrl+C** in the terminal where the server is running

---

## Need Help?

Check these files:
- `PROJECT_STATUS_REPORT.md` - Full project status
- `README.md` - Detailed documentation
- Server logs in terminal - Error messages

---

**That's it! You're ready to run cricket auctions! 🏏**
