# 🔐 Login Credentials - Cricket Auction Platform

## Admin Login

**For Admin Panel Access:**
- **URL:** http://localhost:8000/admin
- **Email:** `admin@cricket.com`
- **Password:** `Admin@123456`

**Permissions:** Full access to all features, player management, auction control, reports

---

## Team Login

**For Team Dashboard Access:**
- **URL:** http://localhost:8000 (use team login option)

### Available Teams:

#### 1. Team Virat (RCB)
- **Username:** `virat` (lowercase!)
- **Password:** `virat123`
- **Budget:** ₹100,000,000

#### 2. Royal Challengers
- **Username:** `royal`
- **Password:** `royal123`
- **Budget:** ₹5,000,000

#### 3. Super Kings
- **Username:** `kings`
- **Password:** `kings123`
- **Budget:** ₹4,500,000

#### 4. Mumbai Warriors
- **Username:** `mumbai`
- **Password:** `mumbai123`
- **Budget:** ₹6,000,000

---

## ⚠️ Important Notes

### Username Case Sensitivity
- Usernames are **case-sensitive**
- Use lowercase: `virat` ✅
- NOT: `Virat` ❌

### Login Issues?
If you get 401 Unauthorized:
1. Check username is lowercase
2. Verify password is correct
3. Make sure you're using the team login form (not admin login)

---

## User Registration

**For Players/Viewers:**
- **URL:** http://localhost:8000
- Click "Register" to create a new account
- Players are auto-approved
- Viewers can watch auctions

---

## Quick Access

| Role | URL | Username | Password |
|------|-----|----------|----------|
| **Admin** | /admin | admin@cricket.com | Admin@123456 |
| **Team 1** | / | virat | virat123 |
| **Team 2** | / | royal | royal123 |
| **Team 3** | / | kings | kings123 |
| **Team 4** | / | mumbai | mumbai123 |

---

## Testing Team Login

1. Go to http://localhost:8000
2. Look for "Team Login" option
3. Enter username: `virat`
4. Enter password: `virat123`
5. Click Login
6. You should be redirected to team dashboard

---

## Troubleshooting

### 401 Unauthorized Error
**Cause:** Wrong username or password

**Solutions:**
- Use lowercase username
- Check password is correct
- Try different team credentials

### Can't Find Team Login
**Solution:** Look for team login form on homepage or go to /team/dashboard

### Password Reset
If you need to reset a team password, run:
```bash
python reset_team_password.py
```

---

## Security Notes

- All passwords are hashed with bcrypt
- Tokens expire after 15 minutes
- Sessions are managed securely
- HTTPS recommended for production

---

**Last Updated:** February 19, 2026  
**Server:** http://localhost:8000  
**Status:** All credentials active and working
