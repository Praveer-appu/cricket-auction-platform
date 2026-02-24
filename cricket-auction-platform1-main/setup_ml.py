"""
Quick setup script for ML prediction system
Checks dependencies and trains the model
"""
import subprocess
import sys
import os

def check_dependencies():
    """Check if ML dependencies are installed"""
    try:
        import sklearn
        import pandas
        import numpy
        import joblib
        print("✅ All ML dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        return False

def install_dependencies():
    """Install ML dependencies"""
    print("\n📦 Installing ML dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "ml_requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def train_model():
    """Train the ML model"""
    print("\n🤖 Training ML model...")
    try:
        subprocess.check_call([
            sys.executable, "ml_models/train.py"
        ])
        print("✅ Model trained successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to train model: {e}")
        return False

def main():
    print("=" * 60)
    print("🏏 Cricket Auction ML Prediction Setup")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❓ Would you like to install ML dependencies? (y/n)")
        response = input().strip().lower()
        
        if response == 'y':
            if not install_dependencies():
                print("\n❌ Setup failed. Please install dependencies manually:")
                print("   pip install -r ml_requirements.txt")
                return
        else:
            print("\n⚠️ Please install dependencies manually:")
            print("   pip install -r ml_requirements.txt")
            return
    
    # Train model
    print("\n❓ Would you like to train the ML model now? (y/n)")
    response = input().strip().lower()
    
    if response == 'y':
        if train_model():
            print("\n" + "=" * 60)
            print("✅ ML PREDICTION SYSTEM READY!")
            print("=" * 60)
            print("\nYou can now:")
            print("1. Start the server: python main_new.py")
            print("2. Access ML API: http://localhost:8000/docs#/ML%20Predictions")
            print("3. Make predictions via API endpoints")
            print("\nSee ML_PREDICTION_GUIDE.md for detailed documentation")
            print("=" * 60)
        else:
            print("\n❌ Setup incomplete. Please train model manually:")
            print("   python ml_models/train.py")
    else:
        print("\n⚠️ Please train the model manually:")
        print("   python ml_models/train.py")

if __name__ == "__main__":
    main()
