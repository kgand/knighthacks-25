"""
InceptionV3-based chess piece detector.

Transfer learning from ImageNet pretrained model.
Fine-tunes only the later layers for piece classification.
"""

import torch
import torch.nn as nn
from torchvision import models, transforms


class InceptionChessDetector(nn.Module):
    """InceptionV3 adapted for chess piece classification."""
    
    def __init__(self, num_classes: int = 13, freeze_until: str = 'Mixed_7c'):
        super().__init__()
        
        # Load pretrained InceptionV3
        # Using ImageNet weights as starting point
        self.model = models.inception_v3(pretrained=True, aux_logits=True)
        
        # Freeze layers up to specified point
        # Mixed_7c is the last inception block before pooling
        # Tested freezing at different layers - Mixed_7c gives best results
        freeze_until_found = False
        for name, param in self.model.named_parameters():
            if freeze_until in name:
                freeze_until_found = True
            if not freeze_until_found:
                param.requires_grad = False
        
        # Replace final FC layer
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, num_classes)
        
        # Also replace auxiliary classifier if present
        if self.model.aux_logits:
            num_aux_features = self.model.AuxLogits.fc.in_features
            self.model.AuxLogits.fc = nn.Linear(num_aux_features, num_classes)
    
    def forward(self, x):
        """Forward pass. Returns logits or (main_logits, aux_logits) during training."""
        return self.model(x)
    
    def predict(self, x):
        """Inference mode - returns only main output."""
        self.model.eval()
        with torch.no_grad():
            if self.training:
                return self.model(x)
            else:
                # During eval, only main output is returned
                return self.model(x)


def create_inception_model(num_classes=13, freeze_until='Mixed_7c', device='cuda'):
    """
    Create InceptionV3 model for chess piece detection.
    
    Args:
        num_classes: Number of piece classes
        freeze_until: Layer name to freeze up to
        device: Device to load model on
        
    Returns:
        Model ready for training/inference
    """
    model = InceptionChessDetector(
        num_classes=num_classes,
        freeze_until=freeze_until
    )
    
    if device == 'rocm':
        device = 'cuda'
    
    model = model.to(device)
    return model


def get_inception_transforms(training=True):
    """
    Get appropriate transforms for InceptionV3.
    
    Inception expects 299x299 input with specific normalization.
    Reference: https://pytorch.org/vision/stable/models.html
    """
    if training:
        return transforms.Compose([
            transforms.Resize(320),
            transforms.RandomCrop(299),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(
                brightness=0.2,
                contrast=0.15,
                saturation=0.15,
                hue=0.05
            ),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])
    else:
        return transforms.Compose([
            transforms.Resize(320),
            transforms.CenterCrop(299),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])


if __name__ == "__main__":
    # Test model creation
    model = create_inception_model(device='cpu')
    print(f"Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Count trainable parameters
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable parameters: {trainable:,}")
