from typing import Dict, Any, List
from datetime import datetime
import requests

class BhuvanServices:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    def get_lulc_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get Land Use Land Cover data for a location.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            
        Returns:
            Dictionary containing LULC information
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'api_key': self.api_key
            }
            response = requests.get(f"{self.base_url}/lulc", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching LULC data: {e}")
            return {}
    
    def get_weather_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get weather forecast data for a location.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            
        Returns:
            Dictionary containing weather forecast
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'api_key': self.api_key
            }
            response = requests.get(f"{self.base_url}/weather", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return {}
    
    def get_crop_recommendations(self, lat: float, lon: float, soil_type: str = None) -> List[Dict[str, Any]]:
        """Get crop recommendations based on location and soil type.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            soil_type: Optional soil type information
            
        Returns:
            List of recommended crops with details
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'soil_type': soil_type,
                'api_key': self.api_key
            }
            response = requests.get(f"{self.base_url}/crop-recommendations", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching crop recommendations: {e}")
            return []
    
    def get_ndvi_timeseries(self, lat: float, lon: float, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get NDVI time series data for a location.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of NDVI values with timestamps
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'start_date': start_date,
                'end_date': end_date,
                'api_key': self.api_key
            }
            response = requests.get(f"{self.base_url}/ndvi-timeseries", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching NDVI time series: {e}")
            return []