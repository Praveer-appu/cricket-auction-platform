# Security Dashboard Information

## What is the Security Dashboard?

The Security Dashboard is an **admin-only** monitoring tool that provides real-time insights into security events, threats, and system protection status for the Cricket Auction Platform.

## Purpose

The Security Dashboard helps administrators:
- **Monitor security threats** in real-time
- **Track failed login attempts** and suspicious activities
- **Manage blocked IP addresses** (auto-blocked or manually blocked)
- **Review security events** with severity levels
- **Protect the platform** from brute force attacks and malicious users

## Features

### 1. Security Statistics
- **Total Security Events**: Count of all security incidents
- **Blocked IPs**: Number of currently blocked IP addresses
- **Failed Login Attempts**: Recent failed authentication attempts
- **Suspicious Activities**: Detected anomalies and threats
- **Active Threats**: Current ongoing security concerns

### 2. Blocked IP Management
- **View all blocked IPs** with reasons and expiration times
- **Manually block IPs** with custom duration (hours)
- **Unblock IPs** with one click
- **Auto-blocking**: System automatically blocks IPs after multiple failed login attempts

### 3. Security Events Log
- **Real-time event tracking** with timestamps
- **Severity levels**: Critical, High, Medium, Low
- **Event types**: Failed logins, suspicious activities, blocked IPs, etc.
- **IP addresses** and user agents for each event
- **Detailed descriptions** of what happened

### 4. Threat Detection
- **Brute force detection**: Automatically blocks IPs after 5 failed login attempts
- **Rate limiting**: Prevents API abuse
- **Suspicious pattern detection**: Identifies unusual behavior
- **IP reputation tracking**: Monitors repeat offenders

## How to Access

1. **Login as Admin**:
   - Email: `admin@cricket.com`
   - Password: `Admin@123456`

2. **Click "Security Dashboard"** button in the admin panel (top right, shield icon)

3. **View real-time security data**

## What Was Fixed

### Issue
The Security Dashboard was stuck on "Loading security data..." because:
- It was looking for auth token in **cookies** (`getCookie('access_token')`)
- But the application stores tokens in **localStorage**

### Solution
Updated the security dashboard JavaScript to:
- Get token from `localStorage.getItem('access_token')` instead of cookies
- Added better error handling with status code checks
- Added error messages for failed API calls

## Security Features in the Platform

### 1. Auto-Blocker
- Automatically blocks IPs after **5 failed login attempts**
- Default block duration: **24 hours**
- Tracks block reasons and expiration times
- Cleans up expired blocks automatically

### 2. Security Monitor
- Logs all security-sensitive requests (login, register, etc.)
- Tracks failed authentication attempts
- Monitors suspicious IP addresses
- Generates security events with severity levels

### 3. Rate Limiting
- Prevents API abuse
- Limits requests per IP address
- Protects against DDoS attacks

### 4. Authentication Security
- JWT tokens with short expiration (15 minutes)
- Refresh tokens (1 day)
- Password hashing with bcrypt
- Session management with Redis

### 5. PII Sanitization
- Automatically redacts sensitive information in logs
- Protects email addresses, IP addresses, MongoDB IDs
- Prevents data leaks in error messages

## API Endpoints (Admin Only)

All endpoints require admin authentication with Bearer token:

### GET /api/security/stats
Returns security statistics overview

### GET /api/security/events?limit=20
Returns recent security events

### GET /api/security/blocked-ips
Returns all currently blocked IP addresses

### POST /api/security/block-ip
Manually block an IP address
```json
{
  "ip": "192.168.1.100",
  "reason": "Suspicious activity",
  "duration_hours": 24
}
```

### POST /api/security/unblock-ip
Manually unblock an IP address
```json
{
  "ip": "192.168.1.100"
}
```

### GET /api/security/check-ip/{ip}
Check if an IP is blocked and get details

### POST /api/security/cleanup?days=90
Clean up old security events and expired blocks

## Use Cases

### 1. Monitoring Failed Logins
- See which IPs are trying to brute force accounts
- Identify patterns in failed login attempts
- Block suspicious IPs manually

### 2. Managing Blocked IPs
- Review auto-blocked IPs
- Unblock legitimate users who got blocked by mistake
- Manually block known malicious IPs

### 3. Security Auditing
- Review security events for compliance
- Track authentication attempts
- Generate security reports

### 4. Threat Response
- Quickly identify and respond to security threats
- Block attackers in real-time
- Monitor ongoing attacks

## Best Practices

1. **Check regularly**: Review the security dashboard daily during active auctions
2. **Investigate anomalies**: Look into unusual patterns or spikes in failed logins
3. **Whitelist trusted IPs**: Don't block your own admin IPs
4. **Clean up old data**: Use the cleanup endpoint to remove old events (90+ days)
5. **Monitor during auctions**: Keep an eye on security during live bidding events

## Troubleshooting

### Dashboard not loading
- Clear browser cache and localStorage
- Ensure you're logged in as admin
- Check browser console for errors (F12)
- Verify server is running

### "Unauthorized" errors
- Logout and login again as admin
- Check that your token hasn't expired
- Verify admin role in database

### No data showing
- This is normal for a fresh installation
- Data will populate as security events occur
- Try a failed login to generate test data

## Technical Details

### Data Storage
- Security events stored in MongoDB `security_events` collection
- Blocked IPs stored in MongoDB `blocked_ips` collection
- In-memory caching for fast lookups

### Performance
- Events auto-expire after 90 days
- Blocked IPs auto-expire based on duration
- Efficient indexing for fast queries

### Security
- Admin-only access (role-based)
- JWT authentication required
- All actions logged for audit trail

## Summary

The Security Dashboard is a powerful tool for monitoring and protecting your Cricket Auction Platform. It provides real-time visibility into security threats and allows quick response to attacks. Now that it's fixed to use localStorage for authentication, it should load properly when you access it as an admin.
