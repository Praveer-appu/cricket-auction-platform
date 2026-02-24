import requests
import json

# Test prediction
url = "http://localhost:8000/ml/predict-price"
data = {
    "matches_played": 100,
    "batting_average": 45.5,
    "strike_rate": 150.0,
    "wickets": 5,
    "economy_rate": 9.0,
    "recent_performance_score": 85.0,
    "player_type": "Batsman"
}

print("Testing ML Prediction...")
print(f"Input: {json.dumps(data, indent=2)}")

response = requests.post(url, json=data)
print(f"\nStatus: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
