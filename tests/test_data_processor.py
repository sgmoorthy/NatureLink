import pytest
import numpy as np
from src.data_processor import DataProcessor

@pytest.fixture
def data_processor():
    return DataProcessor()

@pytest.fixture
def sample_raw_data():
    return {
        'ndvi': 0.5,
        'moisture': 75.0,
        'temperature': 25.0
    }

def test_process_satellite_data(data_processor, sample_raw_data):
    processed_data = data_processor.process_satellite_data(sample_raw_data)
    
    assert isinstance(processed_data, dict)
    assert 'processed_ndvi' in processed_data
    assert 'processed_moisture' in processed_data
    assert 'timestamp' in processed_data

def test_normalize_ndvi(data_processor):
    # Test normalization of different NDVI values
    assert data_processor._normalize_ndvi(-1.0) == 0.0  # Minimum value
    assert data_processor._normalize_ndvi(1.0) == 1.0   # Maximum value
    assert data_processor._normalize_ndvi(0.0) == 0.5   # Middle value

def test_normalize_moisture(data_processor):
    # Test normalization of different moisture values
    assert data_processor._normalize_moisture(0.0) == 0.0    # Minimum value
    assert data_processor._normalize_moisture(100.0) == 1.0  # Maximum value
    assert data_processor._normalize_moisture(50.0) == 0.5   # Middle value

def test_extract_features(data_processor):
    processed_data = {
        'processed_ndvi': 0.75,
        'processed_moisture': 0.6
    }
    
    features = data_processor.extract_features(processed_data)
    
    assert isinstance(features, np.ndarray)
    assert features.shape[0] == 2  # Two features: NDVI and moisture