"""
Comprehensive Project Test Script
Tests all major components of the Cricket Auction Platform
"""
import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("\n" + "="*60)
    print("1. TESTING IMPORTS")
    print("="*60)
    
    modules = [
        ('fastapi', 'FastAPI'),
        ('pymongo', 'MongoDB'),
        ('pydantic', 'Pydantic'),
        ('jose', 'JWT'),
        ('passlib', 'Password Hashing'),
        ('uvicorn', 'ASGI Server'),
    ]
    
    failed = []
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name:20} - OK")
        except ImportError as e:
            print(f"❌ {name:20} - FAILED: {e}")
            failed.append(name)
    
    return len(failed) == 0

def test_database_connection():
    """Test MongoDB connection"""
    print("\n" + "="*60)
    print("2. TESTING DATABASE CONNECTION")
    print("="*60)
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError
        
        client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ MongoDB connection - OK")
        
        # Check database
        db = client['cricket_auction']
        collections = db.list_collection_names()
        print(f"✅ Database 'cricket_auction' - OK")
        print(f"   Collections: {', '.join(collections) if collections else 'None'}")
        
        return True
    except ServerSelectionTimeoutError:
        print("❌ MongoDB connection - FAILED: Cannot connect to MongoDB")
        print("   Make sure MongoDB is running on localhost:27017")
        return False
    except Exception as e:
        print(f"❌ Database test - FAILED: {e}")
        return False

def test_file_structure():
    """Test if all required files and directories exist"""
    print("\n" + "="*60)
    print("3. TESTING FILE STRUCTURE")
    print("="*60)
    
    required_items = {
        'files': [
            'main_new.py',
            'requirements.txt',
            'Procfile',
        ],
        'directories': [
            'core',
            'models',
            'schemas',
            'routers',
            'services',
            'websocket',
            'database',
            'static',
            'templates',
            'utils',
        ]
    }
    
    all_ok = True
    
    # Check files
    for file in required_items['files']:
        if Path(file).exists():
            print(f"✅ File: {file:30} - OK")
        else:
            print(f"❌ File: {file:30} - MISSING")
            all_ok = False
    
    # Check directories
    for directory in required_items['directories']:
        if Path(directory).is_dir():
            print(f"✅ Dir:  {directory:30} - OK")
        else:
            print(f"❌ Dir:  {directory:30} - MISSING")
            all_ok = False
    
    return all_ok

def test_core_modules():
    """Test if core modules can be imported"""
    print("\n" + "="*60)
    print("4. TESTING CORE MODULES")
    print("="*60)
    
    modules = [
        'core.config',
        'core.security',
        'database.session',
        'models.models',
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module:30} - OK")
        except Exception as e:
            print(f"❌ {module:30} - FAILED: {str(e)[:50]}")
            all_ok = False
    
    return all_ok

def test_routers():
    """Test if all routers can be imported"""
    print("\n" + "="*60)
    print("5. TESTING ROUTERS")
    print("="*60)
    
    routers = [
        'routers.auth',
        'routers.players',
        'routers.teams',
        'routers.auction',
        'routers.admin',
        'routers.reports',
    ]
    
    all_ok = True
    for router in routers:
        try:
            __import__(router)
            print(f"✅ {router:30} - OK")
        except Exception as e:
            print(f"❌ {router:30} - FAILED: {str(e)[:50]}")
            all_ok = False
    
    return all_ok

def test_static_files():
    """Test if static files exist"""
    print("\n" + "="*60)
    print("6. TESTING STATIC FILES")
    print("="*60)
    
    static_files = [
        'static/skit-pro.css',
        'static/admin.js',
        'static/team_dashboard_new.js',
        'static/cinematic-effects.js',
    ]
    
    all_ok = True
    for file in static_files:
        if Path(file).exists():
            size = Path(file).stat().st_size
            print(f"✅ {file:40} - OK ({size} bytes)")
        else:
            print(f"❌ {file:40} - MISSING")
            all_ok = False
    
    return all_ok

def test_templates():
    """Test if template files exist"""
    print("\n" + "="*60)
    print("7. TESTING TEMPLATES")
    print("="*60)
    
    templates = [
        'templates/index.html',
        'templates/admin_fresh.html',
        'templates/team_dashboard_new.html',
        'templates/live_studio.html',
    ]
    
    all_ok = True
    for template in templates:
        if Path(template).exists():
            print(f"✅ {template:40} - OK")
        else:
            print(f"❌ {template:40} - MISSING")
            all_ok = False
    
    return all_ok

def test_database_data():
    """Test database data"""
    print("\n" + "="*60)
    print("8. TESTING DATABASE DATA")
    print("="*60)
    
    try:
        from pymongo import MongoClient
        
        client = MongoClient('mongodb://localhost:27017')
        db = client['cricket_auction']
        
        # Check users
        user_count = db.users.count_documents({})
        admin_count = db.users.count_documents({"is_admin": True})
        print(f"✅ Users: {user_count} total, {admin_count} admin(s)")
        
        # Check players
        player_count = db.players.count_documents({})
        print(f"✅ Players: {player_count} total")
        
        # Check teams
        team_count = db.teams.count_documents({})
        print(f"✅ Teams: {team_count} total")
        
        # Check auction config
        auction_config = db.config.find_one({"key": "auction"})
        if auction_config:
            print(f"✅ Auction config exists")
        else:
            print(f"⚠️  Auction config not found (will be created on first use)")
        
        return True
    except Exception as e:
        print(f"❌ Database data test - FAILED: {e}")
        return False

def test_admin_user():
    """Test admin user setup"""
    print("\n" + "="*60)
    print("9. TESTING ADMIN USER")
    print("="*60)
    
    try:
        from pymongo import MongoClient
        
        client = MongoClient('mongodb://localhost:27017')
        db = client['cricket_auction']
        
        admin = db.users.find_one({"email": "admin@cricket.com"})
        
        if admin:
            print(f"✅ Admin user found: {admin.get('email')}")
            print(f"   Name: {admin.get('name', 'N/A')}")
            print(f"   is_admin: {admin.get('is_admin', False)}")
            print(f"   role: {admin.get('role', 'N/A')}")
            
            if admin.get('is_admin') and admin.get('role') == 'admin':
                print("✅ Admin permissions are correct")
                return True
            else:
                print("⚠️  Admin permissions need to be fixed")
                return False
        else:
            print("❌ Admin user not found")
            return False
            
    except Exception as e:
        print(f"❌ Admin user test - FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CRICKET AUCTION PLATFORM - COMPREHENSIVE TEST")
    print("="*60)
    
    results = {
        'Imports': test_imports(),
        'Database Connection': test_database_connection(),
        'File Structure': test_file_structure(),
        'Core Modules': test_core_modules(),
        'Routers': test_routers(),
        'Static Files': test_static_files(),
        'Templates': test_templates(),
        'Database Data': test_database_data(),
        'Admin User': test_admin_user(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Project is ready to run.")
        print("\nTo start the server:")
        print("  python main_new.py")
        print("\nThen access:")
        print("  http://localhost:8000")
        print("\nAdmin credentials:")
        print("  Email: admin@cricket.com")
        print("  Password: Admin@123456")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
