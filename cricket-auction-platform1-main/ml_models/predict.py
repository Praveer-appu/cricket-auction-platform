"""
Player Price Prediction Script
Load trained model and make predictions for new players
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from train import PlayerPricePredictionModel
import pandas as pd
import json


def predict_single_player(player_data):
    """
    Predict price for a single player
    
    Args:
        player_data: dict with player features
    
    Returns:
        Predicted price
    """
    try:
        # Load model
        predictor = PlayerPricePredictionModel.load_model()
        
        # Make prediction
        predicted_price = predictor.predict(player_data)[0]
        
        return {
            'success': True,
            'predicted_price': round(predicted_price, 2),
            'predicted_price_formatted': f"₹{predicted_price:,.2f}",
            'model_used': predictor.best_model_name
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def predict_from_database():
    """
    Predict prices for all players in the database
    """
    try:
        from database import db
        
        # Load model
        predictor = PlayerPricePredictionModel.load_model()
        
        # Get all players
        players = list(db.players.find({}))
        
        predictions = []
        for player in players:
            # Extract features (use defaults if not available)
            player_data = {
                'matches_played': player.get('matches_played', 50),
                'batting_average': player.get('batting_average', 25.0),
                'strike_rate': player.get('strike_rate', 120.0),
                'wickets': player.get('wickets', 10),
                'economy_rate': player.get('economy_rate', 8.0),
                'recent_performance_score': player.get('recent_performance_score', 70.0),
                'player_type': player.get('role', 'Batsman')
            }
            
            predicted_price = predictor.predict(player_data)[0]
            
            predictions.append({
                'player_id': str(player['_id']),
                'name': player.get('name'),
                'current_base_price': player.get('base_price', 0),
                'predicted_price': round(predicted_price, 2),
                'difference': round(predicted_price - player.get('base_price', 0), 2)
            })
        
        return {
            'success': True,
            'predictions': predictions,
            'total_players': len(predictions)
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def main():
    """
    Command-line interface for predictions
    """
    print("\n🏏 Cricket Player Price Prediction")
    print("=" * 60)
    
    # Example prediction
    test_player = {
        'matches_played': 100,
        'batting_average': 45.5,
        'strike_rate': 150.0,
        'wickets': 5,
        'economy_rate': 9.0,
        'recent_performance_score': 85.0,
        'player_type': 'Batsman'
    }
    
    print("\nTest Player Stats:")
    for key, value in test_player.items():
        print(f"  {key}: {value}")
    
    result = predict_single_player(test_player)
    
    if result['success']:
        print(f"\n✅ Predicted Price: {result['predicted_price_formatted']}")
        print(f"   Model Used: {result['model_used']}")
    else:
        print(f"\n❌ Error: {result['error']}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
