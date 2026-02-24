"""
ML Predictions API Router
Provides endpoints for player price predictions using trained ML models
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
import sys
import os
import joblib
import json

from database import db
from bson import ObjectId

# Model paths
MODEL_DIR = "ml_models/saved_models"
MODEL_PATH = f"{MODEL_DIR}/price_predictor_latest.pkl"
SCALER_PATH = f"{MODEL_DIR}/scaler_latest.pkl"
ENCODER_PATH = f"{MODEL_DIR}/label_encoder_latest.pkl"
METADATA_PATH = f"{MODEL_DIR}/model_metadata.json"

# Check if models are available
ML_AVAILABLE = all([
    os.path.exists(MODEL_PATH),
    os.path.exists(SCALER_PATH),
    os.path.exists(ENCODER_PATH)
])

if not ML_AVAILABLE:
    print("⚠️ ML models not found. Run: python ml_models/train.py")

router = APIRouter(prefix="/ml", tags=["ML Predictions"])


def load_ml_model():
    """Load the trained ML model, scaler, and encoder"""
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        encoder = joblib.load(ENCODER_PATH)
        return model, scaler, encoder
    except Exception as e:
        raise Exception(f"Error loading ML model: {str(e)}")


def get_model_name():
    """Get the name of the trained model"""
    try:
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, 'r') as f:
                metadata = json.load(f)
            return metadata.get('model_name', 'unknown')
        return 'unknown'
    except:
        return 'unknown'


def make_prediction(player_data: dict):
    """Make a price prediction for a player with feature engineering"""
    import numpy as np
    
    # Load model
    model, scaler, encoder = load_ml_model()
    
    # Extract base features
    matches_played = player_data['matches_played']
    batting_average = player_data['batting_average']
    strike_rate = player_data['strike_rate']
    wickets = player_data['wickets']
    economy_rate = player_data['economy_rate']
    recent_performance_score = player_data['recent_performance_score']
    player_type = player_data['player_type']
    
    # Encode player type
    player_type_encoded = encoder.transform([player_type])[0]
    
    # Feature Engineering (matching train_improved.py)
    batting_impact = batting_average * strike_rate
    bowling_impact = wickets / (economy_rate + 1)
    experience_performance = matches_played * recent_performance_score
    
    # Normalized features
    batting_avg_norm = batting_average / 60
    strike_rate_norm = strike_rate / 200
    wickets_norm = wickets / 300
    economy_norm = 1 - (economy_rate / 15)
    
    # Composite scores
    batting_score = (batting_avg_norm + strike_rate_norm) / 2
    bowling_score = (wickets_norm + economy_norm) / 2
    overall_score = (batting_score * 0.4 + bowling_score * 0.3 + recent_performance_score / 100 * 0.3)
    
    # Experience tier (1-4)
    if matches_played <= 50:
        experience_tier = 1
    elif matches_played <= 100:
        experience_tier = 2
    elif matches_played <= 150:
        experience_tier = 3
    else:
        experience_tier = 4
    
    # Performance category (1-4)
    if recent_performance_score <= 60:
        performance_category = 1
    elif recent_performance_score <= 75:
        performance_category = 2
    elif recent_performance_score <= 85:
        performance_category = 3
    else:
        performance_category = 4
    
    # Prepare features in correct order (15 features total)
    features = [
        matches_played,
        batting_average,
        strike_rate,
        wickets,
        economy_rate,
        recent_performance_score,
        player_type_encoded,
        batting_impact,
        bowling_impact,
        experience_performance,
        batting_score,
        bowling_score,
        overall_score,
        experience_tier,
        performance_category
    ]
    
    # Scale features
    features_scaled = scaler.transform([features])
    
    # Predict
    predicted_price = model.predict(features_scaled)[0]
    
    return predicted_price


class PlayerStatsInput(BaseModel):
    """Input schema for player statistics"""
    matches_played: int = Field(..., ge=0, description="Total matches played")
    batting_average: float = Field(..., ge=0, description="Batting average")
    strike_rate: float = Field(..., ge=0, description="Strike rate")
    wickets: int = Field(..., ge=0, description="Total wickets taken")
    economy_rate: float = Field(..., ge=0, description="Economy rate")
    recent_performance_score: float = Field(..., ge=0, le=100, description="Recent performance score (0-100)")
    player_type: str = Field(..., description="Player type: Batsman, Bowler, All-Rounder, or Wicketkeeper")


class PricePredictionResponse(BaseModel):
    """Response schema for price prediction"""
    success: bool
    predicted_price: Optional[float] = None
    predicted_price_formatted: Optional[str] = None
    model_used: Optional[str] = None
    confidence_range: Optional[dict] = None
    error: Optional[str] = None


@router.post("/predict-price", response_model=PricePredictionResponse)
async def predict_player_price(stats: PlayerStatsInput):
    """
    Predict auction price for a player based on their statistics
    
    **Input Features:**
    - matches_played: Total matches played
    - batting_average: Batting average
    - strike_rate: Strike rate
    - wickets: Total wickets taken
    - economy_rate: Economy rate
    - recent_performance_score: Recent performance (0-100)
    - player_type: Batsman, Bowler, All-Rounder, or Wicketkeeper
    
    **Returns:**
    - Predicted auction price in INR
    """
    if not ML_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="ML prediction service not available. Please train the model first by running: python ml_models/train.py"
        )
    
    try:
        # Prepare input
        player_data = stats.dict()
        
        # Make prediction
        predicted_price = make_prediction(player_data)
        
        # Calculate confidence range (±15%)
        confidence_range = {
            'min': round(predicted_price * 0.85, 2),
            'max': round(predicted_price * 1.15, 2),
            'min_formatted': f"₹{predicted_price * 0.85:,.2f}",
            'max_formatted': f"₹{predicted_price * 1.15:,.2f}"
        }
        
        return PricePredictionResponse(
            success=True,
            predicted_price=round(predicted_price, 2),
            predicted_price_formatted=f"₹{predicted_price:,.2f}",
            model_used=get_model_name(),
            confidence_range=confidence_range
        )
    
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"ML Prediction Error: {error_msg}")
        return PricePredictionResponse(
            success=False,
            error=str(e)
        )


@router.get("/predict-player/{player_id}")
async def predict_existing_player_price(player_id: str):
    """
    Predict price for an existing player in the database
    Uses player's stored statistics or defaults
    """
    if not ML_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="ML prediction service not available. Run: python ml_models/train.py"
        )
    
    try:
        # Get player from database
        player = db.players.find_one({"_id": ObjectId(player_id)})
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Extract or use default statistics
        player_data = {
            'matches_played': player.get('matches_played', 50),
            'batting_average': player.get('batting_average', 25.0),
            'strike_rate': player.get('strike_rate', 120.0),
            'wickets': player.get('wickets', 10),
            'economy_rate': player.get('economy_rate', 8.0),
            'recent_performance_score': player.get('recent_performance_score', 70.0),
            'player_type': player.get('role', 'Batsman')
        }
        
        # Make prediction
        predicted_price = make_prediction(player_data)
        
        # Calculate confidence range
        confidence_range = {
            'min': round(predicted_price * 0.85, 2),
            'max': round(predicted_price * 1.15, 2),
            'min_formatted': f"₹{predicted_price * 0.85:,.2f}",
            'max_formatted': f"₹{predicted_price * 1.15:,.2f}"
        }
        
        return {
            'success': True,
            'player_id': player_id,
            'player_name': player.get('name'),
            'current_base_price': player.get('base_price', 0),
            'predicted_price': round(predicted_price, 2),
            'predicted_price_formatted': f"₹{predicted_price:,.2f}",
            'difference': round(predicted_price - player.get('base_price', 0), 2),
            'model_used': get_model_name(),
            'confidence_range': confidence_range,
            'statistics_used': player_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict-all-players")
async def predict_all_players_prices():
    """
    Predict prices for all players in the database
    Useful for bulk analysis and comparison
    """
    if not ML_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="ML prediction service not available. Run: python ml_models/train.py"
        )
    
    try:
        # Get all players
        players = list(db.players.find({}))
        
        predictions = []
        for player in players:
            player_data = {
                'matches_played': player.get('matches_played', 50),
                'batting_average': player.get('batting_average', 25.0),
                'strike_rate': player.get('strike_rate', 120.0),
                'wickets': player.get('wickets', 10),
                'economy_rate': player.get('economy_rate', 8.0),
                'recent_performance_score': player.get('recent_performance_score', 70.0),
                'player_type': player.get('role', 'Batsman')
            }
            
            predicted_price = make_prediction(player_data)
            current_base = player.get('base_price', 0)
            
            predictions.append({
                'player_id': str(player['_id']),
                'name': player.get('name'),
                'role': player.get('role'),
                'category': player.get('category'),
                'current_base_price': current_base,
                'predicted_price': round(predicted_price, 2),
                'predicted_price_formatted': f"₹{predicted_price:,.2f}",
                'difference': round(predicted_price - current_base, 2),
                'difference_percentage': round(((predicted_price - current_base) / current_base * 100) if current_base > 0 else 0, 2)
            })
        
        # Sort by predicted price (descending)
        predictions.sort(key=lambda x: x['predicted_price'], reverse=True)
        
        return {
            'success': True,
            'total_players': len(predictions),
            'predictions': predictions,
            'model_used': get_model_name(),
            'summary': {
                'avg_predicted_price': round(sum(p['predicted_price'] for p in predictions) / len(predictions), 2) if predictions else 0,
                'max_predicted_price': max((p['predicted_price'] for p in predictions), default=0),
                'min_predicted_price': min((p['predicted_price'] for p in predictions), default=0)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info")
async def get_model_info():
    """
    Get information about the loaded ML model
    """
    if not ML_AVAILABLE:
        return {
            'available': False,
            'message': 'ML models not trained yet. Run train.py to train models.'
        }
    
    try:
        import json
        model_metadata_path = 'ml_models/saved_models/model_metadata.json'
        
        if os.path.exists(model_metadata_path):
            with open(model_metadata_path, 'r') as f:
                metadata = json.load(f)
            
            return {
                'available': True,
                'model_name': metadata.get('model_name'),
                'features': metadata.get('feature_names'),
                'trained_at': metadata.get('timestamp'),
                'model_path': metadata.get('model_path')
            }
        else:
            return {
                'available': False,
                'message': 'Model metadata not found. Please train the model first.'
            }
    
    except Exception as e:
        return {
            'available': False,
            'error': str(e)
        }
