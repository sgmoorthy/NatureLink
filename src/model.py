import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, List, Tuple

class CropYieldPredictor(nn.Module):
    def __init__(self, input_size: int = 2, hidden_size: int = 64):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, 1)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)

class ModelTrainer:
    def __init__(self, model: nn.Module):
        self.model = model
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(model.parameters())
    
    def train_step(self, features: np.ndarray, targets: np.ndarray) -> float:
        """Perform one training step.
        
        Args:
            features: Input features array
            targets: Target values array
            
        Returns:
            Training loss for this step
        """
        # Convert numpy arrays to torch tensors
        x = torch.FloatTensor(features)
        y = torch.FloatTensor(targets)
        
        # Forward pass
        self.optimizer.zero_grad()
        outputs = self.model(x)
        loss = self.criterion(outputs, y)
        
        # Backward pass
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Make predictions using the trained model.
        
        Args:
            features: Input features array
            
        Returns:
            Predicted values array
        """
        self.model.eval()
        with torch.no_grad():
            x = torch.FloatTensor(features)
            predictions = self.model(x)
        return predictions.numpy()