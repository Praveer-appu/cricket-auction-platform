# Next-Level Security Recommendations

## Current Security Status ✅
You already have excellent security foundations:
- JWT authentication with token blacklisting
- Rate limiting (100 req/min general, 10 bids/min, 10 auth attempts/5min)
- CSRF protection
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- Request validation (SQL injection, XSS prevention)
- Audit logging for sensitive endpoints
- WebSocket authentication
- IP whitelist capability for admin

## Next-Level Enhancements

### 1. Database Security 🔒

#### A. MongoDB Connection Security
**Current**: Basic connection string
**Upgrade**: Add connection encryption and authentication

```python
# core/database_security.py
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
import ssl

def get_secure_mongo_client():
    """Create MongoDB client with enhanced security."""
    return MongoClient(
        settings.MONGODB_URL,
        tls=True,  # Force TLS/SSL
        tlsAllowInvalidCertificates=False,
        authSource='admin',
        authMechanism='SCRAM-SHA-256',
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000
    )
```

#### B. Field-Level Encryption for Sensitive Data
Encrypt sensitive fields like email, phone numbers:

```python
# core/encryption.py
from cryptography.fernet import Fernet
import os

class FieldEncryption:
    def __init__(self):
        key = os.getenv("ENCRYPTION_KEY")  # Store in Railway env
        if not key:
            key = Fernet.generate_key()
            print(f"Generated key: {key.decode()}")
        self.cipher = Fernet(key if isinstance(key, bytes) else key.encode())
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive field."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        """Decrypt sensitive field."""
        return self.cipher.decrypt(encrypted.encode()).decode()

# Usage in models
field_encryptor = FieldEncryption()

# When saving user
user_data["email_encrypted"] = field_encryptor.encrypt(email)

# When reading
email = field_encryptor.decrypt(user_data["email_encrypted"])
```

### 2. Advanced Authentication 🔐

#### A. Multi-Factor Authentication (MFA/2FA)
Add TOTP-based 2FA for admin accounts:

```python
# core/mfa.py
import pyotp
import qrcode
from io import BytesIO
import base64

class MFAManager:
    @staticmethod
    def generate_secret(user_email: str) -> str:
        """Generate TOTP secret for user."""
        return pyotp.random_base32()
    
    @staticmethod
    def get_qr_code(user_email: str, secret: str) -> str:
        """Generate QR code for authenticator app."""
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=user_email,
            issuer_name="Cricket Auction Platform"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

# Add to user model
# mfa_secret: Optional[str] = None
# mfa_enabled: bool = False

# In login endpoint
if user.get("mfa_enabled"):
    # Require MFA token
    mfa_token = request_data.get("mfa_token")
    if not MFAManager.verify_token(user["mfa_secret"], mfa_token):
        raise HTTPException(401, "Invalid MFA token")
```

#### B. Passwordless Authentication (Magic Links)
For team members who don't need passwords:

```python
# core/magic_link.py
import secrets
from datetime import datetime, timedelta, timezone

class MagicLinkAuth:
    @staticmethod
    def generate_magic_link(email: str) -> str:
        """Generate one-time magic link."""
        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # Store in Redis or MongoDB
        db.magic_links.insert_one({
            "token": token,
            "email": email,
            "expires": expires,
            "used": False
        })
        
        return f"https://your-domain.com/auth/magic?token={token}"
    
    @staticmethod
    async def verify_magic_link(token: str) -> Optional[str]:
        """Verify and consume magic link."""
        link = db.magic_links.find_one({
            "token": token,
            "used": False,
            "expires": {"$gt": datetime.now(timezone.utc)}
        })
        
        if not link:
            return None
        
        # Mark as used
        db.magic_links.update_one(
            {"token": token},
            {"$set": {"used": True}}
        )
        
        return link["email"]
```

### 3. Advanced Rate Limiting 🚦

#### A. Adaptive Rate Limiting
Adjust limits based on user behavior:

```python
# core/adaptive_rate_limiter.py
class AdaptiveRateLimiter:
    def __init__(self):
        self.user_reputation = {}  # {user_id: score}
    
    def get_limit_for_user(self, user_id: str) -> int:
        """Get dynamic rate limit based on reputation."""
        reputation = self.user_reputation.get(user_id, 50)
        
        if reputation > 90:
            return 200  # Trusted user
        elif reputation > 70:
            return 150  # Good user
        elif reputation > 50:
            return 100  # Normal user
        else:
            return 50   # Suspicious user
    
    def update_reputation(self, user_id: str, action: str):
        """Update user reputation based on actions."""
        current = self.user_reputation.get(user_id, 50)
        
        if action == "successful_bid":
            current = min(100, current + 1)
        elif action == "failed_auth":
            current = max(0, current - 10)
        elif action == "suspicious_pattern":
            current = max(0, current - 20)
        
        self.user_reputation[user_id] = current
```

#### B. Distributed Rate Limiting with Redis
For multi-instance deployments:

```python
# core/redis_rate_limiter.py
import redis
from datetime import timedelta

class RedisRateLimiter:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def check_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int
    ) -> bool:
        """Check rate limit using Redis."""
        current = self.redis.incr(key)
        
        if current == 1:
            # First request, set expiry
            self.redis.expire(key, window_seconds)
        
        if current > limit:
            ttl = self.redis.ttl(key)
            raise HTTPException(
                429,
                f"Rate limit exceeded. Retry after {ttl} seconds"
            )
        
        return True
```

### 4. Security Monitoring & Alerts 📊

#### A. Real-time Security Monitoring
```python
# core/security_monitor.py
from datetime import datetime, timezone
import logging

class SecurityMonitor:
    def __init__(self):
        self.alerts = []
        self.suspicious_ips = set()
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        details: dict
    ):
        """Log security event."""
        event = {
            "timestamp": datetime.now(timezone.utc),
            "type": event_type,
            "severity": severity,
            "details": details
        }
        
        # Store in database
        db.security_events.insert_one(event)
        
        # Alert if critical
        if severity == "critical":
            self.send_alert(event)
    
    def detect_brute_force(self, ip: str, failed_attempts: int):
        """Detect brute force attacks."""
        if failed_attempts > 5:
            self.log_security_event(
                "brute_force_detected",
                "high",
                {"ip": ip, "attempts": failed_attempts}
            )
            self.suspicious_ips.add(ip)
    
    def detect_sql_injection(self, request_data: str):
        """Detect SQL injection attempts."""
        sql_patterns = [
            "UNION SELECT", "DROP TABLE", "'; --",
            "OR 1=1", "EXEC(", "xp_cmdshell"
        ]
        
        for pattern in sql_patterns:
            if pattern.lower() in request_data.lower():
                self.log_security_event(
                    "sql_injection_attempt",
                    "critical",
                    {"pattern": pattern, "data": request_data[:100]}
                )
                return True
        return False
    
    def send_alert(self, event: dict):
        """Send alert to admin (email, Slack, etc.)."""
        # Implement email/Slack notification
        logger.critical(f"SECURITY ALERT: {event}")

security_monitor = SecurityMonitor()
```

#### B. Automated IP Blocking
```python
# core/auto_blocker.py
class AutoBlocker:
    def __init__(self):
        self.blocked_ips = set()
        self.ip_violations = {}  # {ip: count}
    
    def record_violation(self, ip: str, violation_type: str):
        """Record security violation."""
        self.ip_violations[ip] = self.ip_violations.get(ip, 0) + 1
        
        # Auto-block after 3 violations
        if self.ip_violations[ip] >= 3:
            self.block_ip(ip, reason=violation_type)
    
    def block_ip(self, ip: str, reason: str, duration_hours: int = 24):
        """Block IP address."""
        self.blocked_ips.add(ip)
        
        db.blocked_ips.insert_one({
            "ip": ip,
            "reason": reason,
            "blocked_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=duration_hours)
        })
        
        logger.warning(f"Blocked IP {ip} for {reason}")
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is blocked."""
        if ip in self.blocked_ips:
            return True
        
        # Check database
        block = db.blocked_ips.find_one({
            "ip": ip,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })
        
        return block is not None

auto_blocker = AutoBlocker()
```

### 5. API Security 🛡️

#### A. API Key Management for External Integrations
```python
# core/api_keys.py
import secrets
import hashlib

class APIKeyManager:
    @staticmethod
    def generate_api_key() -> tuple[str, str]:
        """Generate API key and hash."""
        key = f"crick_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, key_hash
    
    @staticmethod
    def validate_api_key(provided_key: str) -> Optional[dict]:
        """Validate API key."""
        key_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        
        api_key = db.api_keys.find_one({
            "key_hash": key_hash,
            "is_active": True,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })
        
        if api_key:
            # Update last used
            db.api_keys.update_one(
                {"_id": api_key["_id"]},
                {"$set": {"last_used": datetime.now(timezone.utc)}}
            )
        
        return api_key

# Middleware for API key auth
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/v1/"):
        api_key = request.headers.get("X-API-Key")
        if not api_key or not APIKeyManager.validate_api_key(api_key):
            return JSONResponse({"detail": "Invalid API key"}, 401)
    return await call_next(request)
```

#### B. Request Signing for Critical Operations
```python
# core/request_signing.py
import hmac
import hashlib

class RequestSigner:
    @staticmethod
    def sign_request(data: dict, secret: str) -> str:
        """Sign request data."""
        message = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(data: dict, signature: str, secret: str) -> bool:
        """Verify request signature."""
        expected = RequestSigner.sign_request(data, secret)
        return hmac.compare_digest(expected, signature)

# Use for critical operations like bids
@router.post("/auction/bid")
async def place_bid(request: Request, bid_data: dict):
    signature = request.headers.get("X-Signature")
    if not RequestSigner.verify_signature(bid_data, signature, settings.BID_SECRET):
        raise HTTPException(403, "Invalid signature")
    # Process bid...
```

### 6. Data Protection 🔐

#### A. Automatic PII Redaction in Logs
```python
# core/log_sanitizer.py
import re

class LogSanitizer:
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{10}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'password': r'password["\']?\s*[:=]\s*["\']?([^"\'}\s]+)'
    }
    
    @staticmethod
    def sanitize(message: str) -> str:
        """Remove PII from log messages."""
        for pii_type, pattern in LogSanitizer.PII_PATTERNS.items():
            message = re.sub(pattern, f'[REDACTED_{pii_type.upper()}]', message)
        return message

# Custom logging handler
class SanitizedLogger(logging.Handler):
    def emit(self, record):
        record.msg = LogSanitizer.sanitize(str(record.msg))
        super().emit(record)
```

#### B. Data Retention Policy
```python
# core/data_retention.py
from datetime import datetime, timedelta, timezone

class DataRetentionManager:
    @staticmethod
    async def cleanup_old_data():
        """Remove old data per retention policy."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
        
        # Delete old audit logs (keep 90 days)
        result = db.security_events.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        logger.info(f"Deleted {result.deleted_count} old security events")
        
        # Anonymize old bid history (keep 1 year)
        old_cutoff = datetime.now(timezone.utc) - timedelta(days=365)
        db.bid_history.update_many(
            {"timestamp": {"$lt": old_cutoff}},
            {"$unset": {"ip_address": "", "user_agent": ""}}
        )
```

### 7. Compliance & Auditing 📋

#### A. GDPR Compliance Tools
```python
# core/gdpr.py
class GDPRCompliance:
    @staticmethod
    async def export_user_data(user_id: str) -> dict:
        """Export all user data (GDPR right to access)."""
        user = db.users.find_one({"_id": ObjectId(user_id)})
        bids = list(db.bid_history.find({"user_id": user_id}))
        
        return {
            "user_profile": user,
            "bid_history": bids,
            "exported_at": datetime.now(timezone.utc)
        }
    
    @staticmethod
    async def delete_user_data(user_id: str):
        """Delete all user data (GDPR right to erasure)."""
        # Anonymize instead of delete (for audit trail)
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "email": f"deleted_{user_id}@deleted.com",
                "name": "Deleted User",
                "deleted_at": datetime.now(timezone.utc)
            }}
        )
        
        db.bid_history.update_many(
            {"user_id": user_id},
            {"$unset": {"ip_address": "", "user_agent": ""}}
        )
```

## Implementation Priority

### High Priority (Implement First)
1. ✅ Field-level encryption for sensitive data
2. ✅ Security monitoring & alerts
3. ✅ Automated IP blocking
4. ✅ PII redaction in logs

### Medium Priority
5. ✅ MFA for admin accounts
6. ✅ Adaptive rate limiting
7. ✅ Request signing for bids
8. ✅ Data retention policy

### Low Priority (Nice to Have)
9. ✅ Magic link authentication
10. ✅ API key management
11. ✅ GDPR compliance tools

## Quick Wins (Easy to Implement)

1. **Add Security Headers Version**
   - Already done! ✅

2. **Enable HSTS Preload**
   ```python
   response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
   ```

3. **Add Subresource Integrity (SRI)**
   ```html
   <script src="https://cdn.jsdelivr.net/..." 
           integrity="sha384-..." 
           crossorigin="anonymous"></script>
   ```

4. **Implement Security.txt**
   ```
   # static/.well-known/security.txt
   Contact: mailto:security@yourdomain.com
   Expires: 2027-12-31T23:59:59.000Z
   Preferred-Languages: en
   ```

## Monitoring Dashboard

Create a security dashboard showing:
- Failed login attempts (last 24h)
- Rate limit violations
- Blocked IPs
- Security events by severity
- Active sessions count
- Suspicious patterns detected

Would you like me to implement any of these? I recommend starting with:
1. Security monitoring & alerts
2. Automated IP blocking
3. Field-level encryption for emails
