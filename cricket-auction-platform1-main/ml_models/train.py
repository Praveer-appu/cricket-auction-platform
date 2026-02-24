"""
Cricket Player Price Prediction Model Training
Uses multiple ML algorithms to predict auction prices based on player statistics
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json
from datetime import datetime
import os

# Create directories for models and data
os.makedirs('ml_models/saved_models', exist_ok=True)
os.makedirs('ml_models/data', exist_ok=True)

class PlayerPricePredictionModel:
    """
    ML Model for predicting cricket player auction prices
    """
    
    def __init__(self):
        self.models = {
            'linear_regression': LinearRegression(),
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        }
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.best_model = None
        self.best_model_name = None
        self.feature_names = None
        
    def generate_sample_data(self, n_samples=500):
        """
        Generate synthetic training data for demonstration
        In production, replace this with real player data from your database
        """
        np.random.seed(42)
        
        # Player types
        player_types = ['Batsman', 'Bowler', 'All-Rounder', 'Wicketkeeper']
        
        data = []
        for _ in range(n_samples):
            player_type = np.random.choice(player_types)
            
            # Generate realistic statistics based on player type
            if player_type == 'Batsman':
                matches_played = np.random.randint(20, 200)
                batting_average = np.random.uniform(25, 55)
                strike_rate = np.random.uniform(120, 180)
                wickets = np.random.randint(0, 20)
                economy_rate = np.random.uniform(7, 12)
                recent_performance = np.random.uniform(60, 95)
                
            elif player_type == 'Bowler':
                matches_played = np.random.randint(20, 200)
                batting_average = np.random.uniform(10, 25)
                strike_rate = np.random.uniform(80, 130)
                wickets = np.random.randint(30, 250)
                economy_rate = np.random.uniform(6, 9)
                recent_performance = np.random.uniform(65, 95)
                
            elif player_type == 'All-Rounder':
                matches_played = np.random.randint(30, 200)
                batting_average = np.random.uniform(25, 40)
                strike_rate = np.random.uniform(120, 150)
                wickets = np.random.randint(20, 150)
                economy_rate = np.random.uniform(7, 10)
                recent_performance = np.random.uniform(70, 98)
                
            else:  # Wicketkeeper
                matches_played = np.random.randint(20, 180)
                batting_average = np.random.uniform(25, 45)
                strike_rate = np.random.uniform(110, 150)
                wickets = np.random.randint(0, 10)
                economy_rate = np.random.uniform(8, 12)
                recent_performance = np.random.uniform(60, 90)
            
            # Calculate price based on features (with some randomness)
            base_price = 50000
            
            # Price factors
            matches_factor = matches_played * 500
            batting_factor = batting_average * strike_rate * 100
            bowling_factor = wickets * 2000 - (economy_rate * 5000)
            performance_factor = recent_performance * 10000
            
            # Type multipliers
            type_multipliers = {
                'Batsman': 1.2,
                'Bowler': 1.0,
                'All-Rounder': 1.5,
                'Wicketkeeper': 1.3
            }
            
            predicted_price = (
                base_price + 
                matches_factor + 
                batting_factor + 
                bowling_factor + 
                performance_factor
            ) * type_multipliers[player_type]
            
            # Add some noise
            predicted_price *= np.random.uniform(0.8, 1.2)
            predicted_price = max(50000, min(predicted_price, 20000000))  # Cap between 50k and 2Cr
            
            data.append({
                'matches_played': matches_played,
                'batting_average': round(batting_average, 2),
                'strike_rate': round(strike_rate, 2),
                'wickets': wickets,
                'economy_rate': round(economy_rate, 2),
                'recent_performance_score': round(recent_performance, 2),
                'player_type': player_type,
                'auction_price': round(predicted_price, 2)
            })
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df, fit=True):
        """
        Prepare features for training/prediction
        """
        # Encode player type
        if fit:
            df['player_type_encoded'] = self.label_encoder.fit_transform(df['player_type'])
        else:
            df['player_type_encoded'] = self.label_encoder.transform(df['player_type'])
        
        # Select features
        feature_columns = [
            'matches_played',
            'batting_average',
            'strike_rate',
            'wickets',
            'economy_rate',
            'recent_performance_score',
            'player_type_encoded'
        ]
        
        self.feature_names = feature_columns
        X = df[feature_columns]
        
        # Scale features
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def train(self, df):
        """
        Train all models and select the best one
        """
        print("=" * 60)
        print("TRAINING PLAYER PRICE PREDICTION MODELS")
        print("=" * 60)
        
        # Prepare data
        X = self.prepare_features(df, fit=True)
        y = df['auction_price'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\nTraining set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        print(f"Features: {', '.join(self.feature_names)}")
        
        results = {}
        
        # Train each model
        for name, model in self.models.items():
            print(f"\n{'='*60}")
            print(f"Training {name.upper().replace('_', ' ')}")
            print(f"{'='*60}")
            
            # Train
            model.fit(X_train, y_train)
            
            # Predict
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Evaluate
            train_mae = mean_absolute_error(y_train, y_pred_train)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, 
                                       scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            
            results[name] = {
                'train_mae': train_mae,
                'test_mae': test_mae,
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'cv_mae': cv_mae
            }
            
            print(f"Train MAE: ₹{train_mae:,.2f}")
            print(f"Test MAE: ₹{test_mae:,.2f}")
            print(f"Train RMSE: ₹{train_rmse:,.2f}")
            print(f"Test RMSE: ₹{test_rmse:,.2f}")
            print(f"Train R²: {train_r2:.4f}")
            print(f"Test R²: {test_r2:.4f}")
            print(f"Cross-Val MAE: ₹{cv_mae:,.2f}")
        
        # Select best model based on test MAE
        best_name = min(results.keys(), key=lambda k: results[k]['test_mae'])
        self.best_model = self.models[best_name]
        self.best_model_name = best_name
        
        print(f"\n{'='*60}")
        print(f"BEST MODEL: {best_name.upper().replace('_', ' ')}")
        print(f"Test MAE: ₹{results[best_name]['test_mae']:,.2f}")
        print(f"Test R²: {results[best_name]['test_r2']:.4f}")
        print(f"{'='*60}")
        
        return results
    
    def predict(self, player_data):
        """
        Predict price for a single player or multiple players
        
        Args:
            player_data: dict or DataFrame with player features
        
        Returns:
            Predicted price(s)
        """
        if isinstance(player_data, dict):
            player_data = pd.DataFrame([player_data])
        
        X = self.prepare_features(player_data, fit=False)
        predictions = self.best_model.predict(X)
        
        return predictions
    
    def save_model(self, model_dir='ml_models/saved_models'):
        """
        Save trained model and preprocessing objects
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save model
        model_path = f"{model_dir}/price_predictor_{self.best_model_name}_{timestamp}.pkl"
        joblib.dump(self.best_model, model_path)
        
        # Save scaler
        scaler_path = f"{model_dir}/scaler_{timestamp}.pkl"
        joblib.dump(self.scaler, scaler_path)
        
        # Save label encoder
        encoder_path = f"{model_dir}/label_encoder_{timestamp}.pkl"
        joblib.dump(self.label_encoder, encoder_path)
        
        # Save metadata
        metadata = {
            'model_name': self.best_model_name,
            'feature_names': self.feature_names,
            'timestamp': timestamp,
            'model_path': model_path,
            'scaler_path': scaler_path,
            'encoder_path': encoder_path
        }
        
        metadata_path = f"{model_dir}/model_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Also save as "latest" for easy loading
        joblib.dump(self.best_model, f"{model_dir}/price_predictor_latest.pkl")
        joblib.dump(self.scaler, f"{model_dir}/scaler_latest.pkl")
        joblib.dump(self.label_encoder, f"{model_dir}/label_encoder_latest.pkl")
        
        print(f"\n✅ Model saved:")
        print(f"   Model: {model_path}")
        print(f"   Scaler: {scaler_path}")
        print(f"   Encoder: {encoder_path}")
        print(f"   Metadata: {metadata_path}")
        
        return metadata_path
    
    @staticmethod
    def load_model(model_dir='ml_models/saved_models'):
        """
        Load trained model and preprocessing objects
        """
        model = joblib.load(f"{model_dir}/price_predictor_latest.pkl")
        scaler = joblib.load(f"{model_dir}/scaler_latest.pkl")
        label_encoder = joblib.load(f"{model_dir}/label_encoder_latest.pkl")
        
        with open(f"{model_dir}/model_metadata.json", 'r') as f:
            metadata = json.load(f)
        
        predictor = PlayerPricePredictionModel()
        predictor.best_model = model
        predictor.scaler = scaler
        predictor.label_encoder = label_encoder
        predictor.feature_names = metadata['feature_names']
        predictor.best_model_name = metadata['model_name']
        
        return predictor


def main():
    """
    Main training pipeline
    """
    print("\n🏏 Cricket Player Price Prediction - Model Training")
    print("=" * 60)
    
    # Initialize model
    predictor = PlayerPricePredictionModel()
    
    # Generate sample data (replace with real data in production)
    print("\n📊 Generating sample training data...")
    df = predictor.generate_sample_data(n_samples=500)
    
    # Save sample data
    df.to_csv('ml_models/data/training_data.csv', index=False)
    print(f"✅ Sample data saved: ml_models/data/training_data.csv")
    print(f"   Total samples: {len(df)}")
    print(f"   Features: {list(df.columns)}")
    
    # Display sample statistics
    print("\n📈 Data Statistics:")
    print(df.describe())
    
    print("\n📊 Player Type Distribution:")
    print(df['player_type'].value_counts())
    
    print("\n💰 Price Range:")
    print(f"   Min: ₹{df['auction_price'].min():,.2f}")
    print(f"   Max: ₹{df['auction_price'].max():,.2f}")
    print(f"   Mean: ₹{df['auction_price'].mean():,.2f}")
    print(f"   Median: ₹{df['auction_price'].median():,.2f}")
    
    # Train models
    results = predictor.train(df)
    
    # Save model
    predictor.save_model()
    
    # Test predictions
    print("\n" + "=" * 60)
    print("TESTING PREDICTIONS")
    print("=" * 60)
    
    test_players = [
        {
            'matches_played': 100,
            'batting_average': 45.5,
            'strike_rate': 150.0,
            'wickets': 5,
            'economy_rate': 9.0,
            'recent_performance_score': 85.0,
            'player_type': 'Batsman'
        },
        {
            'matches_played': 80,
            'batting_average': 20.0,
            'strike_rate': 110.0,
            'wickets': 120,
            'economy_rate': 7.5,
            'recent_performance_score': 88.0,
            'player_type': 'Bowler'
        },
        {
            'matches_played': 120,
            'batting_average': 35.0,
            'strike_rate': 135.0,
            'wickets': 80,
            'economy_rate': 8.0,
            'recent_performance_score': 92.0,
            'player_type': 'All-Rounder'
        }
    ]
    
    for i, player in enumerate(test_players, 1):
        predicted_price = predictor.predict(player)[0]
        print(f"\nTest Player {i} ({player['player_type']}):")
        print(f"  Matches: {player['matches_played']}")
        print(f"  Batting Avg: {player['batting_average']}")
        print(f"  Strike Rate: {player['strike_rate']}")
        print(f"  Wickets: {player['wickets']}")
        print(f"  Economy: {player['economy_rate']}")
        print(f"  Recent Performance: {player['recent_performance_score']}")
        print(f"  ➡️  Predicted Price: ₹{predicted_price:,.2f}")
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Use predict.py to make predictions for new players")
    print("2. Integrate with your auction platform API")
    print("3. Replace sample data with real player statistics")
    print("=" * 60)


if __name__ == "__main__":
    main()
