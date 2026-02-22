"""
Setup database indexes for security collections.
Run this once to create indexes for optimal performance.
"""
import sys
from database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_security_indexes():
    """Create indexes for security collections."""
    
    try:
        # Security events collection
        logger.info("Creating indexes for security_events...")
        
        # Index on timestamp for time-based queries
        db.security_events.create_index([("timestamp", -1)])
        logger.info("✅ Created index: security_events.timestamp")
        
        # Index on IP for IP-based queries
        db.security_events.create_index("ip")
        logger.info("✅ Created index: security_events.ip")
        
        # Index on severity for filtering
        db.security_events.create_index("severity")
        logger.info("✅ Created index: security_events.severity")
        
        # Index on type for event type queries
        db.security_events.create_index("type")
        logger.info("✅ Created index: security_events.type")
        
        # Compound index for common queries
        db.security_events.create_index([
            ("timestamp", -1),
            ("severity", 1)
        ])
        logger.info("✅ Created compound index: security_events.timestamp+severity")
        
        # Blocked IPs collection
        logger.info("\nCreating indexes for blocked_ips...")
        
        # Unique index on IP
        db.blocked_ips.create_index("ip")
        logger.info("✅ Created index: blocked_ips.ip")
        
        # Index on expires_at for cleanup
        db.blocked_ips.create_index("expires_at")
        logger.info("✅ Created index: blocked_ips.expires_at")
        
        # Index on blocked_at for sorting
        db.blocked_ips.create_index([("blocked_at", -1)])
        logger.info("✅ Created index: blocked_ips.blocked_at")
        
        # Compound index for active blocks query
        db.blocked_ips.create_index([
            ("expires_at", 1),
            ("severity", 1)
        ])
        logger.info("✅ Created compound index: blocked_ips.expires_at+severity")
        
        logger.info("\n✅ All security indexes created successfully!")
        
        # Show collection stats
        logger.info("\n📊 Collection Statistics:")
        logger.info(f"Security events: {db.security_events.count_documents({})}")
        logger.info(f"Blocked IPs: {db.blocked_ips.count_documents({})}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")
        return False


if __name__ == "__main__":
    logger.info("🔒 Setting up security database indexes...\n")
    success = create_security_indexes()
    
    if success:
        logger.info("\n✅ Security database setup complete!")
        sys.exit(0)
    else:
        logger.error("\n❌ Security database setup failed!")
        sys.exit(1)
