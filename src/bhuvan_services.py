from typing import Dict, Any, List
from datetime import datetime
import requests
import time
from fastapi import HTTPException
from .bhuvan_config import BhuvanConfig

class BhuvanServices:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        # Store the base URL as provided
        self.base_url = base_url.rstrip('/') if base_url else ''
        self.headers = BhuvanConfig.get_citation_header()
    
    def get_lulc_data(self, lat: float, lon: float, max_retries: int = 3) -> Dict[str, Any]:
        """Get Land Use Land Cover data for a location.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            max_retries: Maximum number of retry attempts for transient failures
            
        Returns:
            Dictionary containing LULC information
            
        Raises:
            HTTPException: If the service is unavailable after retries
        """
        if not self.api_key or not self.base_url:
            raise HTTPException(
                status_code=503,
                detail="Bhuvan API configuration is missing. Please check environment variables."
            )

        for attempt in range(max_retries):
            try:
                params = {
                    'lat': lat,
                    'lon': lon,
                    'api_key': self.api_key
                }
                response = requests.get(
                    f"{self.base_url}/lulc", 
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                # Validate response structure
                if not isinstance(data, dict):
                    raise HTTPException(
                        status_code=500,
                        detail="Invalid response format from Bhuvan API"
                    )
                return data
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=504,
                        detail="Bhuvan API request timed out. Please try again later."
                    )
            except requests.exceptions.ConnectionError:
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=503,
                        detail="Unable to connect to Bhuvan API. Service may be unavailable."
                    )
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid Bhuvan API key. Please check your configuration."
                    )
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Bhuvan API error: {str(e)}"
                )
            except Exception as e:
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Unexpected error while fetching LULC data: {str(e)}"
                    )
            
            # Wait before retrying (exponential backoff)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
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
            response = requests.get(f"{self.base_url}/weather", params=params, headers=self.headers)
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
            response = requests.get(
                f"{self.base_url}/crop-recommendations",
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
                print(f"Crop recommendations endpoint not found: {e}")
                return []
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
            response = requests.get(f"{self.base_url}/ndvi-timeseries", params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching NDVI time series: {e}")
            return []