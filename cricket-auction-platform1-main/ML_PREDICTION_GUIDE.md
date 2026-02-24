# 🤖 ML-Based Player Price Prediction System

## Overview

This system uses Machine Learning to predict cricket player auction prices based on their performance statistics. It helps teams make smarter bidding decisions by providing data-driven price estimates.

## Features

### 🎯 Prediction Models
- **Linear Regression**: Fast, interpretable baseline model
- **Random Forest**: Ensemble model for better accuracy
- **Gradient Boosting**: Advanced model with best performance

### 📊 Input Features
1. **Matches Played**: Total career matches
2. **Batting Average**: Average runs per dismissal
3. **Strike Rate**: Runs scored per 100 balls
4. **Wickets**: Total wickets taken
5. **Economy Rate**: Runs conceded per over
6. **Recent Performance Score**: Performance rating (0-100)
7. **Player Type**: Batsman, Bowler, All-Rounder, or Wicketkeeper

### 💡 Output
- **Predicted Price**: Estimated auction value in INR
- **Confidence Range**: Min-Max range (±15%)
- **Model Used**: Which ML algorithm made the prediction

## Installation

### Step 1: Install ML Dependencies
```bash
cd cricket-auction-platform1-main
pip install -r ml_requirements.txt
```

### Step 2: Train the Model
```bash
python ml_models/train.py
```

This will:
- Generate 500 sample training records
- Train 3 different ML models
- Compare their performance
- Save the best model
- Create test predictions

**Expected Output:**
```
🏏 Cricket Player Price Prediction - Model Training
============================================================
📊 Generating sample training data...
✅ Sample data saved: ml_models/data/training_data.csv
   Total samples: 500

============================================================
TRAINING PLAYER PRICE PREDICTION MODELS
============================================================
Training set size: 400
Test set size: 100

============================================================
Training LINEAR REGRESSION
============================================================
Train MAE: ₹245,123.45
Test MAE: ₹256,789.12
Train R²: 0.8234
Test R²: 0.8156

============================================================
Training RANDOM FOREST
============================================================
Train MAE: ₹123,456.78
Test MAE: ₹145,678.90
Train R²: 0.9456
Test R²: 0.9234

============================================================
Training GRADIENT BOOSTING
============================================================
Train MAE: ₹134,567.89
Test MAE: ₹152,345.67
Train R²: 0.9345
Test R²: 0.9123

============================================================
BEST MODEL: RANDOM FOREST
Test MAE: ₹145,678.90
Test R²: 0.9234
============================================================

✅ Model saved:
   Model: ml_models/saved_models/price_predictor_random_forest_20260222_161000.pkl
   Scaler: ml_models/saved_models/scaler_20260222_161000.pkl
   Encoder: ml_models/saved_models/label_encoder_20260222_161000.pkl
   Metadata: ml_models/saved_models/model_metadata.json
```

### Step 3: Test Predictions
```bash
python ml_models/predict.py
```

## API Integration

### Enable ML Predictions in Main App

Add to `main_new.py`:
```python
# ML Predictions Router
try:
    from routers.ml_predictions import router as ml_router
    app.include_router(ml_router)
    print("✅ ML Predictions enabled")
except ImportError:
    print("⚠️ ML Predictions not available - install ml_requirements.txt")
```

### API Endpoints

#### 1. Predict Price for Custom Stats
```http
POST /ml/predict-price
Content-Type: application/json

{
  "matches_played": 100,
  "batting_average": 45.5,
  "strike_rate": 150.0,
  "wickets": 5,
  "economy_rate": 9.0,
  "recent_performance_score": 85.0,
  "player_type": "Batsman"
}
```

**Response:**
```json
{
  "success": true,
  "predicted_price": 8500000.00,
  "predicted_price_formatted": "₹85,00,000.00",
  "model_used": "random_forest",
  "confidence_range": {
    "min": 7225000.00,
    "max": 9775000.00,
    "min_formatted": "₹72,25,000.00",
    "max_formatted": "₹97,75,000.00"
  }
}
```

#### 2. Predict Price for Existing Player
```http
GET /ml/predict-player/{player_id}
```

**Response:**
```json
{
  "success": true,
  "player_id": "507f1f77bcf86cd799439011",
  "player_name": "Virat Kohli",
  "current_base_price": 5000000,
  "predicted_price": 8500000.00,
  "predicted_price_formatted": "₹85,00,000.00",
  "difference": 3500000.00,
  "model_used": "random_forest",
  "confidence_range": {
    "min": 7225000.00,
    "max": 9775000.00
  },
  "statistics_used": {
    "matches_played": 100,
    "batting_average": 45.5,
    "strike_rate": 150.0,
    "wickets": 5,
    "economy_rate": 9.0,
    "recent_performance_score": 85.0,
    "player_type": "Batsman"
  }
}
```

#### 3. Predict All Players
```http
GET /ml/predict-all-players
```

**Response:**
```json
{
  "success": true,
  "total_players": 25,
  "predictions": [
    {
      "player_id": "507f1f77bcf86cd799439011",
      "name": "Virat Kohli",
      "role": "Batsman",
      "category": "Faculty",
      "current_base_price": 5000000,
      "predicted_price": 8500000.00,
      "predicted_price_formatted": "₹85,00,000.00",
      "difference": 3500000.00,
      "difference_percentage": 70.00
    }
  ],
  "model_used": "random_forest",
  "summary": {
    "avg_predicted_price": 6500000.00,
    "max_predicted_price": 12000000.00,
    "min_predicted_price": 2500000.00
  }
}
```

#### 4. Get Model Info
```http
GET /ml/model-info
```

**Response:**
```json
{
  "available": true,
  "model_name": "random_forest",
  "features": [
    "matches_played",
    "batting_average",
    "strike_rate",
    "wickets",
    "economy_rate",
    "recent_performance_score",
    "player_type_encoded"
  ],
  "trained_at": "20260222_161000",
  "model_path": "ml_models/saved_models/price_predictor_random_forest_20260222_161000.pkl"
}
```

## Frontend Integration

### Display Predicted Price in Player Cards

Add to `team_dashboard_new.js`:
```javascript
async function loadPlayerPrediction(playerId) {
    try {
        const res = await api(`/ml/predict-player/${playerId}`);
        const data = await res.json();
        
        if (data.success) {
            return {
                predicted: data.predicted_price_formatted,
                confidence: data.confidence_range,
                current: data.current_base_price
            };
        }
    } catch (error) {
        console.error('Prediction error:', error);
        return null;
    }
}

// Update player card to show prediction
function createPlayerCard(player, isOwned) {
    // ... existing code ...
    
    // Add prediction badge
    const predictionBadge = `
        <div class="prediction-badge" style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 5px 10px; border-radius: 5px; margin-top: 5px;">
            <small style="color: #fff;">🤖 AI Predicted: Loading...</small>
        </div>
    `;
    
    // Load prediction asynchronously
    loadPlayerPrediction(player._id).then(pred => {
        if (pred) {
            document.querySelector(`#player-${player._id} .prediction-badge`).innerHTML = 
                `<small style="color: #fff;">🤖 AI Predicted: ${pred.predicted}</small>`;
        }
    });
    
    // ... rest of card HTML ...
}
```

### Add Prediction Button in Admin Panel

Add to `admin.js`:
```javascript
async function showPredictionForPlayer(playerId) {
    try {
        const res = await api(`/ml/predict-player/${playerId}`);
        const data = await res.json();
        
        if (data.success) {
            alert(`
🤖 AI Price Prediction

Player: ${data.player_name}
Current Base Price: ₹${data.current_base_price.toLocaleString()}

Predicted Price: ${data.predicted_price_formatted}
Confidence Range: ${data.confidence_range.min_formatted} - ${data.confidence_range.max_formatted}

Difference: ₹${data.difference.toLocaleString()}
Model: ${data.model_used}
            `);
        }
    } catch (error) {
        alert('Prediction failed: ' + error.message);
    }
}
```

## Using Real Player Data

### Update Player Model

Add statistics fields to `models/models.py`:
```python
class Player:
    # ... existing fields ...
    
    # ML Features
    matches_played: int = 0
    batting_average: float = 0.0
    strike_rate: float = 0.0
    wickets: int = 0
    economy_rate: float = 0.0
    recent_performance_score: float = 0.0
```

### Update Player Registration Form

Add to `user_dashboard.html`:
```html
<div class="col-md-6">
  <label class="form-label">Matches Played</label>
  <input name="matches_played" type="number" min="0" class="form-control" placeholder="e.g., 50" />
</div>

<div class="col-md-6">
  <label class="form-label">Batting Average</label>
  <input name="batting_average" type="number" step="0.01" min="0" class="form-control" placeholder="e.g., 35.5" />
</div>

<div class="col-md-6">
  <label class="form-label">Strike Rate</label>
  <input name="strike_rate" type="number" step="0.01" min="0" class="form-control" placeholder="e.g., 125.0" />
</div>

<div class="col-md-6">
  <label class="form-label">Wickets Taken</label>
  <input name="wickets" type="number" min="0" class="form-control" placeholder="e.g., 25" />
</div>

<div class="col-md-6">
  <label class="form-label">Economy Rate</label>
  <input name="economy_rate" type="number" step="0.01" min="0" class="form-control" placeholder="e.g., 7.5" />
</div>

<div class="col-md-6">
  <label class="form-label">Recent Performance (0-100)</label>
  <input name="recent_performance_score" type="number" min="0" max="100" class="form-control" placeholder="e.g., 85" />
</div>
```

### Retrain with Real Data

Once you have real player data:
```python
# In train.py, replace generate_sample_data() with:
def load_real_data():
    from database import db
    players = list(db.players.find({}))
    
    data = []
    for p in players:
        if p.get('final_bid'):  # Only use players with actual auction prices
            data.append({
                'matches_played': p.get('matches_played', 50),
                'batting_average': p.get('batting_average', 25.0),
                'strike_rate': p.get('strike_rate', 120.0),
                'wickets': p.get('wickets', 10),
                'economy_rate': p.get('economy_rate', 8.0),
                'recent_performance_score': p.get('recent_performance_score', 70.0),
                'player_type': p.get('role', 'Batsman'),
                'auction_price': p.get('final_bid')
            })
    
    return pd.DataFrame(data)
```

## Model Performance Metrics

### Understanding Metrics

- **MAE (Mean Absolute Error)**: Average prediction error in rupees
  - Lower is better
  - Example: MAE of ₹1,50,000 means predictions are off by ±₹1.5L on average

- **RMSE (Root Mean Squared Error)**: Penalizes large errors more
  - Lower is better
  - More sensitive to outliers than MAE

- **R² Score (Coefficient of Determination)**: How well the model fits the data
  - Range: 0 to 1
  - Higher is better
  - 0.9+ is excellent, 0.7-0.9 is good, <0.7 needs improvement

### Improving Model Accuracy

1. **Collect More Data**: More training samples = better predictions
2. **Add Features**: Include more relevant statistics
3. **Feature Engineering**: Create derived features (e.g., runs per match)
4. **Hyperparameter Tuning**: Optimize model parameters
5. **Regular Retraining**: Update model with new auction results

## Troubleshooting

### Model Not Loading
```bash
# Check if model files exist
ls ml_models/saved_models/

# Retrain if missing
python ml_models/train.py
```

### Import Errors
```bash
# Install ML dependencies
pip install -r ml_requirements.txt
```

### Poor Predictions
- Ensure training data is representative
- Check if player statistics are realistic
- Retrain with more data
- Try different models

### API Errors
- Verify model is trained
- Check player_type matches training data
- Ensure all required fields are provided

## Production Deployment

### 1. Train on Real Data
Replace sample data with actual player statistics and auction results.

### 2. Schedule Retraining
Set up periodic retraining (e.g., after each auction season):
```python
# cron job or scheduled task
python ml_models/train.py
```

### 3. Monitor Performance
Track prediction accuracy and retrain when accuracy drops.

### 4. A/B Testing
Compare ML predictions with actual auction prices to validate model.

## Benefits

### For Teams
- **Smarter Bidding**: Data-driven price estimates
- **Budget Planning**: Know expected costs before bidding
- **Value Detection**: Find undervalued players

### For Admins
- **Fair Pricing**: Set realistic base prices
- **Market Analysis**: Understand player valuations
- **Auction Planning**: Predict total auction value

### For Players
- **Self-Assessment**: Understand market value
- **Performance Goals**: Know what stats increase value
- **Negotiation**: Data-backed price expectations

## Future Enhancements

1. **Deep Learning**: Neural networks for complex patterns
2. **Time Series**: Predict future performance trends
3. **Ensemble Methods**: Combine multiple models
4. **Feature Importance**: Show which stats matter most
5. **Real-time Updates**: Update predictions during auction
6. **Comparison Tool**: Compare similar players
7. **What-If Analysis**: See how stat changes affect price

## Summary

The ML prediction system adds intelligence to your auction platform, helping all stakeholders make better decisions. Start with the sample data, then gradually transition to real player statistics for production-ready predictions.

**Next Steps:**
1. Install dependencies: `pip install -r ml_requirements.txt`
2. Train model: `python ml_models/train.py`
3. Test predictions: `python ml_models/predict.py`
4. Integrate API endpoints into your platform
5. Add frontend UI to display predictions
6. Collect real data and retrain for production
