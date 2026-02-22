"""
Database Optimization Script
Creates indexes and optimizes queries for production performance
Run this once to optimize your database
"""
import sys
from database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_indexes():
    """Create all necessary indexes for optimal query performance"""
    
    logger.info("🚀 Starting database optimization...")
    
    # Users collection
    logger.info("Creating indexes for 'users' collection...")
    db.users.create_index("email", unique=True)
    db.users.create_index("role")
    db.users.create_index([("email", 1), ("role", 1)])
    
    # Players collection
    logger.info("Creating indexes for 'players' collection...")
    db.players.create_index("name")
    db.players.create_index("role")
    db.players.create_index("category")
    db.players.create_index("status")
    db.players.create_index("auction_round")
    db.players.create_index("base_price")
    db.players.create_index("final_price")
    db.players.create_index("final_team")
    
    # Compound indexes for common queries
    db.players.create_index([("status", 1), ("auction_round", 1)])
    db.players.create_index([("role", 1), ("status", 1)])
    db.players.create_index([("final_team", 1), ("status", 1)])
    db.players.create_index([("category", 1), ("role", 1)])
    
    # Teams collection
    logger.info("Creating indexes for 'teams' collection...")
    db.teams.create_index("name", unique=True)
    db.teams.create_index("email", unique=True)
    db.teams.create_index("total_spent")
    db.teams.create_index("remaining_purse")
    
    # Bid history collection
    logger.info("Creating indexes for 'bid_history' collection...")
    db.bid_history.create_index("player_id")
    db.bid_history.create_index("team_id")
    db.bid_history.create_index("timestamp")
    
    # Compound indexes for bid queries
    db.bid_history.create_index([("player_id", 1), ("timestamp", -1)])
    db.bid_history.create_index([("team_id", 1), ("timestamp", -1)])
    db.bid_history.create_index([("player_id", 1), ("team_id", 1)])
    
    # Auction config
    logger.info("Creating indexes for 'config' collection...")
    db.config.create_index("key", unique=True)
    
    # Chat messages (if exists)
    if "chat_messages" in db.list_collection_names():
        logger.info("Creating indexes for 'chat_messages' collection...")
        db.chat_messages.create_index("room")
        db.chat_messages.create_index("timestamp")
        db.chat_messages.create_index([("room", 1), ("timestamp", -1)])
    
    # Wishlist (if exists)
    if "wishlist" in db.list_collection_names():
        logger.info("Creating indexes for 'wishlist' collection...")
        db.wishlist.create_index("user_id")
        db.wishlist.create_index("player_id")
        db.wishlist.create_index([("user_id", 1), ("player_id", 1)], unique=True)
    
    logger.info("✅ All indexes created successfully!")


def analyze_collections():
    """Analyze collection statistics"""
    
    logger.info("\n📊 Collection Statistics:")
    logger.info("=" * 60)
    
    collections = ["users", "players", "teams", "bid_history", "config"]
    
    for coll_name in collections:
        if coll_name in db.list_collection_names():
            coll = db[coll_name]
            count = coll.count_documents({})
            indexes = coll.list_indexes()
            index_count = len(list(indexes))
            
            logger.info(f"\n{coll_name.upper()}:")
            logger.info(f"  Documents: {count:,}")
            logger.info(f"  Indexes: {index_count}")
            
            # Show index details
            for idx in coll.list_indexes():
                logger.info(f"    - {idx['name']}: {idx.get('key', {})}")


def optimize_queries():
    """Provide query optimization tips"""
    
    logger.info("\n💡 Query Optimization Tips:")
    logger.info("=" * 60)
    
    tips = [
        "1. Always use indexed fields in queries (status, role, category, etc.)",
        "2. Use projection to fetch only needed fields: .find({}, {'name': 1, 'role': 1})",
        "3. Limit results when possible: .find().limit(100)",
        "4. Use compound indexes for multi-field queries",
        "5. Avoid $where and $regex on large collections",
        "6. Use aggregation pipeline for complex queries",
        "7. Consider using .hint() to force index usage",
        "8. Monitor slow queries with profiling",
    ]
    
    for tip in tips:
        logger.info(f"  {tip}")


def show_slow_queries():
    """Show potentially slow queries and how to optimize them"""
    
    logger.info("\n⚡ Common Query Optimizations:")
    logger.info("=" * 60)
    
    optimizations = [
        {
            "slow": "db.players.find({})",
            "fast": "db.players.find({}, {'name': 1, 'role': 1, 'status': 1}).limit(50)",
            "reason": "Fetch only needed fields and limit results"
        },
        {
            "slow": "db.players.find({'status': 'available', 'role': 'Batsman'})",
            "fast": "db.players.find({'status': 'available', 'role': 'Batsman'}).hint('status_1_role_1')",
            "reason": "Use compound index hint for better performance"
        },
        {
            "slow": "db.bid_history.find({'player_id': player_id}).sort('timestamp', -1)",
            "fast": "db.bid_history.find({'player_id': player_id}).sort('timestamp', -1).limit(10)",
            "reason": "Limit results and use compound index"
        }
    ]
    
    for i, opt in enumerate(optimizations, 1):
        logger.info(f"\n  Example {i}:")
        logger.info(f"    ❌ Slow:  {opt['slow']}")
        logger.info(f"    ✅ Fast:  {opt['fast']}")
        logger.info(f"    💡 Why:   {opt['reason']}")


def main():
    """Main optimization function"""
    
    try:
        # Create indexes
        create_indexes()
        
        # Analyze collections
        analyze_collections()
        
        # Show optimization tips
        optimize_queries()
        
        # Show query examples
        show_slow_queries()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Database optimization complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error during optimization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
