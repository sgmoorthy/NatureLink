import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

class BhuvanAPI:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('BHUVAN_API_KEY')
        self.base_url = os.getenv('BHUVAN_API_BASE_URL')
        
    def get_satellite_data(self, lat: float, lon: float, date: str) -> Dict[str, Any]:
        """Fetch satellite data for a specific location and date.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing satellite data
            
        Raises:
            HTTPException: If the service is unavailable or returns an error
        """
        if not self.api_key or not self.base_url:
            raise HTTPException(
                status_code=503,
                detail="Bhuvan API configuration is missing. Please check environment variables."
            )

        try:
            params = {
                'lat': lat,
                'lon': lon,
                'date': date,
                'api_key': self.api_key
            }
            response = requests.get(
                f"{self.base_url}/satellite-data",
                params=params,
                timeout=10  # Add timeout to prevent hanging
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=504,
                detail="Bhuvan API request timed out. Please try again later."
            )
        except requests.exceptions.ConnectionError:
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
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while fetching satellite data: {str(e)}"
            )
    
    def get_vegetation_indices(self, lat: float, lon: float, date: str) -> Dict[str, float]:
        """Calculate vegetation indices (NDVI, EVI) for a location.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing vegetation indices
        """
        # TODO: Implement actual calculation using satellite data
        # This is a placeholder implementation
        return {
            'ndvi': 0.5,  # Normalized Difference Vegetation Index
            'evi': 0.4    # Enhanced Vegetation Index
        }
    
    def get_soil_moisture(self, lat: float, lon: float, date: str) -> float:
        """Get soil moisture data for a location.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            date: Date in YYYY-MM-DD format
            
        Returns:
            Soil moisture value
        """
        # TODO: Implement actual soil moisture data retrieval
        # This is a placeholder implementation
        return 0.35  # 35% soil moisture