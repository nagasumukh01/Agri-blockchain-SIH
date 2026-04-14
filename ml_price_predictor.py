import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import random
from datetime import datetime

class MLPricePredictor:
    def __init__(self):
        self.model = None
        self.product_encoder = LabelEncoder()
        self.quality_encoder = LabelEncoder()
        self.season_encoder = LabelEncoder()
        self.price_history = {}  # Store price history for products
        self.supported_crops = {
            'rice': {'min_price': 15, 'max_price': 25, 'base_price': 20},
            'wheat': {'min_price': 12, 'max_price': 18, 'base_price': 15},
            'corn': {'min_price': 8, 'max_price': 12, 'base_price': 10},
            'soybeans': {'min_price': 15, 'max_price': 22, 'base_price': 18},
            'vegetables': {'min_price': 20, 'max_price': 30, 'base_price': 25},
            'fruits': {'min_price': 25, 'max_price': 35, 'base_price': 30}
        }
        self.quality_grades = ['A', 'B', 'C']
        self.seasons = ['Spring', 'Summer', 'Fall', 'Winter']
        self.initialize_model()

    def initialize_model(self):
        # Create synthetic training data
        np.random.seed(42)
        n_samples = 1000

        # Generate synthetic features
        data = {
            'product': np.random.choice(['Rice', 'Wheat', 'Corn', 'Soybeans'], n_samples),
            'quality': np.random.choice(['A', 'B', 'C'], n_samples),
            'quantity': np.random.uniform(100, 1000, n_samples),
            'season': np.random.choice(['Spring', 'Summer', 'Fall', 'Winter'], n_samples),
            'market_demand': np.random.uniform(0.5, 1.5, n_samples)
        }

        # Generate synthetic prices
        base_prices = {'Rice': 20, 'Wheat': 15, 'Corn': 10, 'Soybeans': 18}
        quality_multipliers = {'A': 1.2, 'B': 1.0, 'C': 0.8}
        season_multipliers = {'Spring': 1.1, 'Summer': 1.0, 'Fall': 0.9, 'Winter': 1.2}

        prices = []
        for i in range(n_samples):
            base_price = base_prices[data['product'][i]]
            quality_mult = quality_multipliers[data['quality'][i]]
            season_mult = season_multipliers[data['season'][i]]
            quantity_effect = 1.0 - (data['quantity'][i] / 2000)  # Higher quantity gives bulk discount
            market_effect = data['market_demand'][i]
            
            price = (base_price * quality_mult * season_mult * (1 + quantity_effect) * market_effect)
            prices.append(price)

        data['price'] = prices
        self.df = pd.DataFrame(data)

        # Encode categorical variables using separate encoders
        self.df['product_encoded'] = self.product_encoder.fit_transform(self.df['product'])
        self.df['quality_encoded'] = self.quality_encoder.fit_transform(self.df['quality'])
        self.df['season_encoded'] = self.season_encoder.fit_transform(self.df['season'])

        # Train the model
        features = ['product_encoded', 'quality_encoded', 'season_encoded', 'quantity', 'market_demand']
        X = self.df[features]
        y = self.df['price']

        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)

    def predict_price(self, product, quality, quantity, season):
        if self.model is None:
            self.initialize_model()

        # Convert inputs to appropriate format and handle case sensitivity
        try:
            # Normalize product name to title case
            product_normalized = product.strip().title()
            quality_normalized = quality.strip().upper()
            season_normalized = season.strip().capitalize()
            
            product_encoded = self.product_encoder.transform([product_normalized])[0]
            quality_encoded = self.quality_encoder.transform([quality_normalized])[0]
            season_encoded = self.season_encoder.transform([season_normalized])[0]
            
            # Generate a random market demand between 0.8 and 1.2
            market_demand = random.uniform(0.8, 1.2)

            # Create feature array for prediction
            features = np.array([[
                product_encoded,
                quality_encoded,
                season_encoded,
                float(quantity),
                market_demand
            ]])

            # Make prediction
            predicted_price = self.model.predict(features)[0]
            return max(0.1, predicted_price)  # Ensure price is always positive

        except Exception as e:
            print(f"Error in price prediction: {str(e)}")
            # Fallback to base price if prediction fails
            base_prices = {'Rice': 20, 'Wheat': 15, 'Corn': 10, 'Soybeans': 18}
            return base_prices.get(product, 15)  # Default to 15 if product not found

    def get_markup_price(self, base_price, stage, product):
        """
        Calculate markup based on supply chain stage.
        Also adds stage-specific costs and updates price history.
        """
        stage_markups = {
            'farmer': {
                'markup': 1.0,      # No markup for farmer's base price
                'costs': {
                    'processing': 0.5,  # Basic processing cost per kg
                    'packaging': 0.3    # Basic packaging cost per kg
                }
            },
            'distributor': {
                'markup': 1.2,      # 20% markup
                'costs': {
                    'transport': 2.0,   # Transport cost per kg
                    'storage': 1.0,     # Storage cost per kg
                    'handling': 0.5     # Handling cost per kg
                }
            },
            'retailer': {
                'markup': 1.4,      # 40% markup
                'costs': {
                    'store_cost': 1.5,  # Store operation cost per kg
                    'marketing': 0.8,    # Marketing cost per kg
                    'packaging': 0.5     # Additional packaging cost per kg
                }
            }
        }
        
        stage_info = stage_markups.get(stage, {'markup': 1.0, 'costs': {}})
        markup = stage_info['markup']
        additional_costs = sum(stage_info['costs'].values())
        
        final_price = (base_price * markup) + additional_costs
        
        # Update price history
        if product not in self.price_history:
            self.price_history[product] = {}
        
        self.price_history[product][stage] = {
            'price': final_price,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'markup_percentage': (markup - 1) * 100,
            'additional_costs': additional_costs,
            'base_price': base_price
        }
        
        return final_price

    def get_price_history(self, product):
        """Get the price history for a product across all stages"""
        return self.price_history.get(product.lower(), {})
        
    def get_market_factors(self):
        """Get current market factors affecting prices"""
        return {
            'supply_demand': random.uniform(0.8, 1.2),
            'market_volatility': random.uniform(0.9, 1.1),
            'seasonal_impact': self._get_seasonal_impact()
        }
        
    def _get_seasonal_impact(self):
        """Calculate seasonal impact on prices"""
        current_month = datetime.now().month
        seasons = {
            'winter': [12, 1, 2],
            'spring': [3, 4, 5],
            'summer': [6, 7, 8],
            'autumn': [9, 10, 11]
        }
        
        season_multipliers = {
            'winter': 1.2,  # Higher prices in winter
            'spring': 0.9,  # Lower prices in spring
            'summer': 1.0,  # Normal prices in summer
            'autumn': 1.1   # Slightly higher in autumn
        }
        
        current_season = next(
            season for season, months in seasons.items() 
            if current_month in months
        )
        
        return season_multipliers[current_season]

    def get_price_analysis(self, product):
        """Get detailed price analysis for a product"""
        history = self.get_price_history(product)
        if not history:
            return None
            
        analysis = {
            'price_progression': [],
            'total_markup': 0,
            'total_costs': 0,
            'stage_details': {}
        }
        
        stages = ['farmer', 'distributor', 'retailer']
        initial_price = None
        
        for stage in stages:
            if stage in history:
                stage_data = history[stage]
                if not initial_price:
                    initial_price = stage_data['base_price']
                
                analysis['stage_details'][stage] = {
                    'price': stage_data['price'],
                    'markup_percentage': stage_data['markup_percentage'],
                    'additional_costs': stage_data['additional_costs'],
                    'timestamp': stage_data['timestamp']
                }
                
                analysis['total_markup'] += stage_data['markup_percentage']
                analysis['total_costs'] += stage_data['additional_costs']
                
                analysis['price_progression'].append({
                    'stage': stage,
                    'price': stage_data['price']
                })
        
        if initial_price and analysis['price_progression']:
            final_price = analysis['price_progression'][-1]['price']
            analysis['total_price_increase'] = ((final_price - initial_price) / initial_price) * 100
            
        return analysis

    def get_supported_crops(self):
        """Get list of supported crops and their price ranges"""
        return self.supported_crops

    def get_quality_grades(self):
        """Get available quality grades"""
        return self.quality_grades

    def get_seasons(self):
        """Get available seasons"""
        return self.seasons

    def get_price_factors(self):
        """Get all factors affecting price"""
        return {
            "crop_factors": {
                "supported_crops": self.get_supported_crops(),
                "quality_grades": self.get_quality_grades(),
                "seasons": self.get_seasons()
            },
            "market_factors": self.get_market_factors(),
            "supply_chain_stages": {
                "farmer": {
                    "markup": 0,
                    "costs": ["processing", "packaging"]
                },
                "distributor": {
                    "markup": 20,
                    "costs": ["transport", "storage", "handling"]
                },
                "retailer": {
                    "markup": 40,
                    "costs": ["store_cost", "marketing", "packaging"]
                }
            }
        }