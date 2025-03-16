import pytest
import responses
from src.bhuvan_api import BhuvanAPI

@pytest.fixture
def bhuvan_api():
    return BhuvanAPI()

@pytest.fixture
def mock_satellite_data():
    return {
        'ndvi': 0.5,
        'moisture': 75.0,
        'temperature': 25.0
    }

@responses.activate
def test_get_satellite_data(bhuvan_api, mock_satellite_data):
    # Mock the API response
    responses.add(
        responses.GET,
        f"{bhuvan_api.base_url}/satellite-data",
        json=mock_satellite_data,
        status=200
    )

    # Test the API call
    result = bhuvan_api.get_satellite_data(lat=12.9716, lon=77.5946, date='2023-01-01')
    
    assert result == mock_satellite_data
    assert len(responses.calls) == 1

@responses.activate
def test_get_satellite_data_error(bhuvan_api):
    # Mock API error response
    responses.add(
        responses.GET,
        f"{bhuvan_api.base_url}/satellite-data",
        status=404
    )

    # Test error handling
    result = bhuvan_api.get_satellite_data(lat=12.9716, lon=77.5946, date='2023-01-01')
    assert result == {}

def test_get_vegetation_indices(bhuvan_api):
    result = bhuvan_api.get_vegetation_indices(lat=12.9716, lon=77.5946, date='2023-01-01')
    
    assert isinstance(result, dict)
    assert 'ndvi' in result
    assert 'evi' in result
    assert isinstance(result['ndvi'], float)
    assert isinstance(result['evi'], float)