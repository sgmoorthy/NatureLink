import pytest
import torch
import numpy as np
from src.model import CropYieldPredictor, ModelTrainer

@pytest.fixture
def model():
    return CropYieldPredictor(input_size=2, hidden_size=64)

@pytest.fixture
def trainer(model):
    return ModelTrainer(model)

@pytest.fixture
def sample_data():
    features = np.array([[0.5, 0.6], [0.7, 0.8], [0.4, 0.3]])
    targets = np.array([1.2, 1.5, 0.9])
    return features, targets

def test_model_architecture(model):
    # Test model structure
    assert isinstance(model, torch.nn.Module)
    
    # Test forward pass with sample input
    x = torch.randn(1, 2)  # Batch size 1, 2 features
    output = model(x)
    assert output.shape == (1, 1)  # Single prediction

def test_model_training(trainer, sample_data):
    features, targets = sample_data
    initial_loss = trainer.train_step(features, targets)
    
    # Train for a few steps
    for _ in range(5):
        new_loss = trainer.train_step(features, targets)
        
    # Loss should decrease after training
    assert new_loss < initial_loss

def test_model_prediction(model):
    # Test prediction with sample input
    sample_input = torch.tensor([[0.5, 0.6]], dtype=torch.float32)
    prediction = model(sample_input)
    
    assert isinstance(prediction, torch.Tensor)
    assert prediction.shape == (1, 1)
    assert not torch.isnan(prediction).any()