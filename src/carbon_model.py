import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, List, Tuple

class CarbonFootprintPredictor(nn.Module):
    def __init__(self, input_size: int = 4, hidden_size: int = 128):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size // 2, 1),
            nn.ReLU()  # Ensure non-negative carbon footprint predictions
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)

class CarbonModelTrainer:
    def __init__(self, model: nn.Module):
        self.model = model
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    def train_step(self, features: np.ndarray, targets: np.ndarray) -> float:
        """Perform one training step.
        
        Args:
            features: Input features array including vegetation indices, land use changes,
                     industrial activity indicators, and temporal features
            targets: Target carbon footprint values array
            
        Returns:
            Training loss for this step
        """
        x = torch.FloatTensor(features)
        y = torch.FloatTensor(targets)
        
        self.optimizer.zero_grad()
        outputs = self.model(x)
        loss = self.criterion(outputs, y)
        
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Make carbon footprint predictions.
        
        Args:
            features: Input features array including vegetation indices,
                     land use changes, and industrial activity indicators
            
        Returns:
            Predicted carbon footprint values
        """
        self.model.eval()
        with torch.no_grad():
            x = torch.FloatTensor(features)
            predictions = self.model(x)
        return predictions.numpy()