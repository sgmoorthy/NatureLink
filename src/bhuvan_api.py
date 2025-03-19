from typing import List, Dict, Any
import requests
from .bhuvan_config import BhuvanConfig

class BhuvanAPIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)

class BhuvanAPI:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/') if base_url else ''
        self.headers = BhuvanConfig.get_citation_header()

    def get_crop_recommendations(self, lat: float, lon: float, soil_type: str = None) -> List[Dict[str, Any]]:
        """Get crop recommendations based on location and soil type.
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            soil_type: Optional soil type information
            
        Returns:
            List of recommended crops with details
            
        Raises:
            BhuvanAPIError: If there's an error accessing the API
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'soil_type': soil_type,
                'api_key': self.api_key
            }
            response = requests.get(
                f"{self.base_url}/data/crop-recommendations",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, list):
                raise BhuvanAPIError(
                    status_code=500,
                    detail="Invalid response format from crop recommendations endpoint"
                )
                
            return data
            
        except requests.exceptions.Timeout:
            raise BhuvanAPIError(
                status_code=504,
                detail="Crop recommendations request timed out"
            )
        except requests.exceptions.ConnectionError:
            raise BhuvanAPIError(
                status_code=503,
                detail="Unable to connect to Bhuvan API"
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise BhuvanAPIError(
                    status_code=404,
                    detail="Crop recommendations endpoint not found"
                )
            raise BhuvanAPIError(
                status_code=e.response.status_code,
                detail=f"Error fetching crop recommendations: {str(e)}"
            )
        except Exception as e:
            raise BhuvanAPIError(
                status_code=500,
                detail=f"Unexpected error fetching crop recommendations: {str(e)}"
            )