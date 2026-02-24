"""
Test ML Prediction API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_model_info():
    """Test model info endpoint"""
    print("\n" + "="*60)
    print("Testing ML Model Info Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/ml/model-info")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Model Available: {data.get('available')}")
        print(f"✅ Model Name: {data.get('model_name')}")
        print(f"✅ Features: {len(data.get('features', []))}")
        print(f"✅ Trained At: {data.get('trained_at')}")
    else:
        print(f"❌ Error: {response.text}")

def test_custom_prediction():
    """Test custom prediction endpoint"""
    print("\n" + "="*60)
    print("Testing Custom Prediction Endpoint")
    print("="*60)
    
    # Sample player stats
    player_data = {
        "matches_played": 100,
        "batting_average": 45.5,
        "strike_rate": 150.0,
        "wickets": 5,
        "economy_rate": 9.0,
        "recent_performance_score": 85.0,
        "player_type": "Batsman"
    }
    
    print(f"Input Stats: {json.dumps(player_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/ml/predict-price",
        json=player_data
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('success')}")
        print(f"✅ Predicted Price: {data.get('predicted_price_formatted')}")
        print(f"✅ Confidence Range: {data.get('confidence_range', {}).get('min_formatted')} - {data.get('confidence_range', {}).get('max_formatted')}")
        print(f"✅ Model Used: {data.get('model_used')}")
    else:
        print(f"❌ Error: {response.text}")

def test_all_players_prediction():
    """Test bulk prediction endpoint"""
    print("\n" + "="*60)
    print("Testing Bulk Prediction Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/ml/predict-all-players")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('success')}")
        print(f"✅ Total Players: {data.get('total_players')}")
        
        if data.get('predictions'):
            print(f"\nFirst 3 Predictions:")
            for pred in data['predictions'][:3]:
                print(f"  - {pred.get('name')}: {pred.get('predicted_price_formatted')}")
        
        summary = data.get('summary', {})
        print(f"\nSummary:")
        print(f"  - Avg Predicted: ₹{summary.get('avg_predicted_price', 0):,.0f}")
        print(f"  - Max Predicted: ₹{summary.get('max_predicted_price', 0):,.0f}")
        print(f"  - Min Predicted: ₹{summary.get('min_predicted_price', 0):,.0f}")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    print("\n🤖 ML PREDICTION API TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Model Info
        test_model_info()
        
        # Test 2: Custom Prediction
        test_custom_prediction()
        
        # Test 3: Bulk Predictions
        test_all_players_prediction()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
