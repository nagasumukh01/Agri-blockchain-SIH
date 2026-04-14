import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

from weather import WeatherService
from ml_price_predictor import MLPricePredictor

class PriceModel:
    def __init__(self):
        self.predictor = MLPricePredictor()
        self.weather_service = WeatherService()

    def calculate_price(self, crop_name, quality, location, quantity, city=None, stage='farmer', prev_price=None):
        """
        Calculate the price for agricultural produce based on various factors.
        
        Args:
            crop_name (str): Name of the crop
            quality (str): Quality grade of the produce (A, B, C)
            location (str): Location/season of the transaction
            quantity (float): Quantity in kg
            city (str): City name for weather data
            stage (str): Supply chain stage (farmer/distributor/retailer)
            prev_price (float): Previous stage's price (optional)
        
        Returns:
            tuple: (price_per_kg, pricing_details)
        """
        # Get weather impact if city is provided
        weather_multiplier = 1.0
        weather_data = None
        if city:
            weather_data = self.weather_service.get_weather(city)
            weather_multiplier = self.weather_service.calculate_weather_impact(weather_data)

        # Get base price from ML model
        # Map location to season for ML model
        season_map = {
            'rural': 'Spring',
            'urban': 'Summer', 
            'suburban': 'Fall'
        }
        season = season_map.get(location.lower(), 'Summer')  # Default to Summer
        
        base_price = self.predictor.predict_price(
            crop_name.lower(), 
            quality, 
            quantity,
            season
        )
        
        # Get market factors
        market_factors = self.predictor.get_market_factors()
        
        # Apply market factors to base price
        base_price = base_price * market_factors['supply_demand'] * market_factors['seasonal_impact']
        
        # Apply stage-based markup and get final price
        final_price = self.predictor.get_markup_price(base_price, stage, crop_name.lower())
        
        # Apply weather multiplier
        final_price = final_price * weather_multiplier
        
        # Get price analysis
        price_analysis = self.predictor.get_price_analysis(crop_name.lower())
        
        # Create detailed pricing info
        pricing_info = {
            "base_price": round(base_price, 2),
            "weather_multiplier": round(weather_multiplier, 2),
            "weather_data": weather_data,
            "market_factors": {
                k: round(v, 2) for k, v in market_factors.items()
            },
            "final_price": round(final_price, 2),
            "stage": stage,
            "price_analysis": price_analysis
        }
        
        return round(final_price, 2), pricing_info
        
    def _calculate_markup(self, price_history, current_price, stage):
        """Calculate markup from previous stage"""
        stages = ['farmer', 'distributor', 'retailer']
        current_idx = stages.index(stage)
        
        if current_idx == 0:  # Farmer stage
            return {
                "markup_percentage": 0,
                "markup_amount": 0,
                "previous_price": None
            }
            
        prev_stage = stages[current_idx - 1]
        prev_price = price_history.get(prev_stage)
        
        if prev_price:
            markup_amount = current_price - prev_price
            markup_percentage = (markup_amount / prev_price) * 100
            return {
                "markup_percentage": round(markup_percentage, 2),
                "markup_amount": round(markup_amount, 2),
                "previous_price": round(prev_price, 2)
            }
        
        return {
            "markup_percentage": None,
            "markup_amount": None,
            "previous_price": None
        }

    def get_price_factors(self):
        """
        Get the current pricing factors for transparency.
        
        Returns:
            dict: Current pricing factors and their values
        """
        return {
            "supported_crops": self.predictor.get_supported_crops(),
            "quality_multipliers": {
                'A': 1.2,
                'B': 1.0,
                'C': 0.8
            },
            "location_factors": {
                'urban': 1.1,
                'suburban': 1.0,
                'rural': 0.9
            },
            "quantity_discounts": {
                ">1000kg": "10% discount",
                ">500kg": "5% discount",
                "≤500kg": "no discount"
            }
        }
