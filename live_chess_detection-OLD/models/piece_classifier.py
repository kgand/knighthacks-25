"""
Chess piece classifier using AlexNet-inspired architecture.

Used for synthetic data and digital board piece recognition.
Trained on 13 classes: empty square + 12 piece types.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class PieceClassifierNet(nn.Module):
    """
    CNN for classifying chess pieces in square images.
    
    Architecture inspired by AlexNet but scaled for smaller inputs.
    Handles 64x64 pixel squares (1/8th of full board).
    """
    
    def __init__(self, input_dim: int = 64, num_classes: int = 13, dropout_rate: float = 0.5):
        super().__init__()
        
        self.input_dim = input_dim
        self.num_classes = num_classes
        
        # Feature extraction layers
        # Started with 3 conv layers, found 5 gives better accuracy
        self.features = nn.Sequential(
            # Conv block 1
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            
            # Conv block 2
            nn.Conv2d(64, 192, kernel_size=5, padding=2),
            nn.BatchNorm2d(192),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            
            # Conv block 3
            nn.Conv2d(192, 384, kernel_size=3, padding=1),
            nn.BatchNorm2d(384),
            nn.ReLU(inplace=True),
            
            # Conv block 4
            nn.Conv2d(384, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            
            # Conv block 5
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
        )
        
        # Calculate flattened size after conv layers
        # For 64x64 input: 64 -> 32 -> 15 -> 7 -> 3 after pooling
        self.flat_size = 256 * 3 * 3
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(self.flat_size, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(4096, 2048),
            nn.ReLU(inplace=True),
            nn.Linear(2048, num_classes),
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor (B, 3, H, W)
            
        Returns:
            Logits (B, num_classes)
        """
        features = self.features(x)
        flat_features = features.view(features.size(0), -1)
        logits = self.classifier(flat_features)
        return logits
    
    def predict_probabilities(self, x: torch.Tensor) -> torch.Tensor:
        """Get class probabilities using softmax."""
        logits = self.forward(x)
        return F.softmax(logits, dim=1)


def create_piece_classifier(device: str = 'cuda', pretrained_path: str = None):
    """
    Factory function to create and optionally load a trained classifier.
    
    Args:
        device: Device to load model on (cuda/rocm/cpu)
        pretrained_path: Path to checkpoint
        
    Returns:
        Initialized model
    """
    model = PieceClassifierNet()
    
    if pretrained_path:
        checkpoint = torch.load(pretrained_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"Loaded checkpoint from {pretrained_path}")
    
    # Handle ROCm (appears as 'cuda' in PyTorch)
    if device == 'rocm':
        device = 'cuda'
    
    model = model.to(device)
    model.eval()
    
    return model


if __name__ == "__main__":
    # Test model creation
    model = PieceClassifierNet()
    
    # Test forward pass
    dummy_input = torch.randn(4, 3, 64, 64)
    output = model(dummy_input)
    
    print(f"Model created successfully")
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Number of parameters: {sum(p.numel() for p in model.parameters()):,}")
