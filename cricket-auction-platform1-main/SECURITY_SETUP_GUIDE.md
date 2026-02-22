# Security Setup Guide - Quick Start

## 🚀 Deployment Status
✅ Code deployed to Railway
✅ Security features active

## 📋 Post-Deployment Steps

### Step 1: Create Database Indexes (IMPORTANT)
Run this command once to optimize security queries:

```bash
# SSH into Railway or run locally with Railway MongoDB URL
python setup_security_indexes.py
```

Or via Railway CLI:
```bash
railway run python setup_security_indexes.py
```

This creates indexes for:
- `security_events` collection
- `blocked_ips` collection

**Why?** Without indexes, security queries will be slow.

### Step 2: Access Security Dashboard
Once Railway finishes deploying (2-3 minutes):

1. Login as admin: `rakeshn9380@gmail.com`
2. Visit: `https://cricket-auction-platform1-production.up.railway.app/security/dashboard`
3. You should see the security monitoring dashboard

### Step 3: Test Security Features

#### Test 1: View Dashboard
- Should show 0 events initially
- Should show 0 blocked IPs
- Dashboard auto-refreshes every 30 seconds

#### Test 2: Simulate Attack (Optional)
Try a SQL injection to test detection:
```bash
curl "https://cricket-auction-platform1-production.up.railway.app/api/players?name=admin' OR 1=1--"
```

Expected result:
- Request blocked with 403
- IP blocked for 72 hours
- Event appears in security dashboard

#### Test 3: Check Logs
Look for security messages in Railway logs:
- `✅ PII sanitization enabled`
- `✅ Integrated security middleware enabled`
- `✅ Security monitoring started`
- `✅ Auto-blocker initialized with X blocked IPs`

## 🎯 What's Now Active

### Automatic Protection
- ✅ SQL injection detection & blocking
- ✅ XSS attack detection & blocking
- ✅ Path traversal detection & blocking
- ✅ Brute force protection (5 failed logins = 1hr block)
- ✅ PII sanitization in all logs

### Monitoring
- ✅ Real-time security event logging
- ✅ Failed login tracking
- ✅ Suspicious IP detection
- ✅ Attack pattern recognition

### Management
- ✅ Security dashboard for admins
- ✅ Manual IP blocking/unblocking
- ✅ Security statistics & reports
- ✅ Automatic cleanup (90-day retention)

## 📊 Using the Security Dashboard

### View Statistics
- Total events (last 24 hours)
- Critical events count
- Active blocked IPs
- Suspicious IPs

### Manage Blocked IPs
1. See all blocked IPs in table
2. View block reason & expiry
3. Click "Unblock" to manually unblock
4. Blocks expire automatically

### Monitor Events
- See recent security events
- Filter by severity
- View attack details
- Track attacking IPs

## 🔧 Maintenance

### Daily Tasks
- Check security dashboard
- Review critical events
- Verify no legitimate IPs blocked

### Weekly Tasks
- Review attack patterns
- Check blocked IP list
- Monitor security statistics

### Monthly Tasks
- Review security logs
- Update security rules if needed
- Check database size (security_events)

## 🚨 If Something Goes Wrong

### Dashboard Not Loading
1. Check you're logged in as admin
2. Check Railway deployment succeeded
3. Check browser console for errors

### Legitimate IP Blocked
1. Go to security dashboard
2. Find IP in blocked IPs table
3. Click "Unblock" button
4. IP immediately unblocked

### Too Many Events
If you see too many false positives:
1. Check event details in dashboard
2. Adjust detection patterns if needed
3. Contact developer for tuning

## 📞 Support

### Check Logs
```bash
railway logs
```

Look for:
- Security event messages (🚨)
- Block notifications (🚫)
- Error messages (❌)

### API Endpoints
All security endpoints require admin auth:
- `GET /api/security/stats` - Statistics
- `GET /api/security/events` - Recent events
- `GET /api/security/blocked-ips` - Blocked IPs
- `POST /api/security/block-ip` - Block IP
- `POST /api/security/unblock-ip` - Unblock IP

## ✅ Verification Checklist

After deployment, verify:
- [ ] Railway deployment successful
- [ ] Database indexes created
- [ ] Security dashboard accessible
- [ ] PII sanitization working (check logs)
- [ ] No errors in Railway logs
- [ ] Dashboard shows statistics
- [ ] Auto-refresh working

## 🎉 You're Protected!

Your platform now has enterprise-grade security protecting against:
- SQL injection attacks
- XSS attacks
- Brute force attacks
- Path traversal attacks
- Data leaks

All automatic, all monitored, all manageable through the dashboard!
