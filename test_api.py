import os
import requests
from dotenv import load_dotenv
from src.bhuvan_api import BhuvanAPI, BhuvanAPIError

# Load environment variables
load_dotenv()

def main():
    try:
        # Initialize the API
        api = BhuvanAPI()
        
        # Test area of interest ID
        aoi_id = 'sgmoorthy51'
        output_dir = 'output'
        
        # Download and save DEM data
        output_path = api.save_dem_data(aoi_id, output_dir, 'geoid')
        print(f'Successfully downloaded DEM data. File saved to: {output_path}')
        
    except BhuvanAPIError as be:
        print(f'Bhuvan API error (status {be.status_code}): {be.detail}')
    except ValueError as ve:
        print(f'Configuration error: {ve}')
    except requests.RequestException as re:
        print(f'API request failed: {re}')
    except Exception as e:
        print(f'Unexpected error: {e}')

if __name__ == '__main__':
    main()