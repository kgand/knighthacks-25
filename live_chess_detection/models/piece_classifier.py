"""
Chess piece classifier for individual piece recognition.

Provides classification of individual chess pieces from
cropped images using various CNN architectures.
"""

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import cv2


class ChessPieceClassifier(nn.Module):
    """
    CNN-based chess piece classifier.
    
    Uses various backbone architectures for classifying
    individual chess pieces from cropped images.
    """
    
    def __init__(
        self,
        backbone: str = 'resnet18',
        num_classes: int = 12,  # 6 piece types * 2 colors
        pretrained: bool = True,
        dropout_rate: float = 0.5
    ):
        """
        Initialize piece classifier.
        
        Args:
            backbone: Backbone architecture ('resnet18', 'resnet50', 'efficientnet')
            num_classes: Number of piece classes
            pretrained: Whether to use pretrained weights
            dropout_rate: Dropout rate for regularization
        """
        super(ChessPieceClassifier, self).__init__()
        
        self.backbone_name = backbone
        self.num_classes = num_classes
        
        # Load backbone
        if backbone == 'resnet18':
            self.backbone = models.resnet18(pretrained=pretrained)
            num_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
        elif backbone == 'resnet50':
            self.backbone = models.resnet50(pretrained=pretrained)
            num_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
        elif backbone == 'efficientnet':
            # Use EfficientNet-B0
            from torchvision.models import efficientnet_b0
            self.backbone = efficientnet_b0(pretrained=pretrained)
            num_features = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(256, num_classes)
        )
        
        # Piece type classifier (6 classes: king, queen, rook, bishop, knight, pawn)
        self.piece_type_classifier = nn.Sequential(
            nn.Linear(num_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 6)
        )
        
        # Color classifier (2 classes: white, black)
        self.color_classifier = nn.Sequential(
            nn.Linear(num_features, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(128, 2)
        )
        
        # Class names
        self.class_names = {
            0: 'white-king', 1: 'white-queen', 2: 'white-rook',
            3: 'white-bishop', 4: 'white-knight', 5: 'white-pawn',
            6: 'black-king', 7: 'black-queen', 8: 'black-rook',
            9: 'black-bishop', 10: 'black-knight', 11: 'black-pawn'
        }
        
        self.piece_type_names = {
            0: 'king', 1: 'queen', 2: 'rook',
            3: 'bishop', 4: 'knight', 5: 'pawn'
        }
        
        self.color_names = {0: 'white', 1: 'black'}
    
    def forward(self, x):
        """
        Forward pass through the network.
        
        Args:
            x: Input tensor (batch_size, 3, height, width)
            
        Returns:
            Dictionary with predictions
        """
        # Extract features
        features = self.backbone(x)
        
        # Get predictions
        class_logits = self.classifier(features)
        piece_type_logits = self.piece_type_classifier(features)
        color_logits = self.color_classifier(features)
        
        return {
            'class_logits': class_logits,
            'piece_type_logits': piece_type_logits,
            'color_logits': color_logits
        }
    
    def predict(self, x: torch.Tensor) -> Dict:
        """
        Make predictions on input tensor.
        
        Args:
            x: Input tensor
            
        Returns:
            Dictionary with predictions
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(x)
            
            # Apply softmax to get probabilities
            class_probs = torch.softmax(outputs['class_logits'], dim=1)
            piece_type_probs = torch.softmax(outputs['piece_type_logits'], dim=1)
            color_probs = torch.softmax(outputs['color_logits'], dim=1)
            
            return {
                'class_probs': class_probs,
                'piece_type_probs': piece_type_probs,
                'color_probs': color_probs,
                'class_names': self.class_names,
                'piece_type_names': self.piece_type_names,
                'color_names': self.color_names
            }


class ChessPieceClassifierWrapper:
    """
    Wrapper for chess piece classifier with preprocessing.
    
    Provides easy-to-use interface for piece classification.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        backbone: str = 'resnet18',
        device: str = 'auto'
    ):
        """
        Initialize classifier wrapper.
        
        Args:
            model_path: Path to trained model weights
            backbone: Backbone architecture
            device: Device to use
        """
        self.device = device if device != 'auto' else ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model
        self.model = ChessPieceClassifier(backbone=backbone)
        
        # Load weights if provided
        if model_path and torch.load(model_path, map_location=self.device):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            print(f"✅ Loaded model from {model_path}")
        
        self.model.to(self.device)
        self.model.eval()
        
        # Setup preprocessing
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),  # Standard input size
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def classify_piece(
        self,
        piece_image: np.ndarray,
        return_probabilities: bool = False
    ) -> Union[str, Dict]:
        """
        Classify a single chess piece.
        
        Args:
            piece_image: Cropped piece image
            return_probabilities: Whether to return probability scores
            
        Returns:
            Class name or dictionary with detailed results
        """
        # Preprocess image
        if len(piece_image.shape) == 3 and piece_image.shape[2] == 3:
            # Convert BGR to RGB
            piece_image = cv2.cvtColor(piece_image, cv2.COLOR_BGR2RGB)
        
        # Apply transforms
        input_tensor = self.transform(piece_image).unsqueeze(0).to(self.device)
        
        # Run inference
        with torch.no_grad():
            predictions = self.model.predict(input_tensor)
        
        # Get predicted class
        class_probs = predictions['class_probs'].cpu().numpy()[0]
        predicted_class = np.argmax(class_probs)
        confidence = class_probs[predicted_class]
        
        class_name = predictions['class_names'][predicted_class]
        
        if return_probabilities:
            return {
                'class': class_name,
                'confidence': float(confidence),
                'class_probs': class_probs,
                'piece_type': predictions['piece_type_names'][np.argmax(predictions['piece_type_probs'].cpu().numpy()[0])],
                'color': predictions['color_names'][np.argmax(predictions['color_probs'].cpu().numpy()[0])]
            }
        else:
            return class_name
    
    def classify_pieces(
        self,
        piece_images: List[np.ndarray],
        return_probabilities: bool = False
    ) -> List[Union[str, Dict]]:
        """
        Classify multiple chess pieces.
        
        Args:
            piece_images: List of cropped piece images
            return_probabilities: Whether to return probability scores
            
        Returns:
            List of classification results
        """
        results = []
        for piece_image in piece_images:
            result = self.classify_piece(piece_image, return_probabilities)
            results.append(result)
        return results
    
    def get_piece_features(self, piece_image: np.ndarray) -> np.ndarray:
        """
        Extract features from piece image.
        
        Args:
            piece_image: Cropped piece image
            
        Returns:
            Feature vector
        """
        # Preprocess image
        if len(piece_image.shape) == 3 and piece_image.shape[2] == 3:
            piece_image = cv2.cvtColor(piece_image, cv2.COLOR_BGR2RGB)
        
        # Apply transforms
        input_tensor = self.transform(piece_image).unsqueeze(0).to(self.device)
        
        # Extract features
        with torch.no_grad():
            features = self.model.backbone(input_tensor)
            features = features.cpu().numpy()[0]
        
        return features


def train_piece_classifier(
    train_loader,
    val_loader,
    backbone: str = 'resnet18',
    num_epochs: int = 50,
    learning_rate: float = 0.001,
    device: str = 'auto',
    save_path: str = 'models/classifier/chess_piece_classifier.pth'
):
    """
    Train chess piece classifier.
    
    Args:
        train_loader: Training data loader
        val_loader: Validation data loader
        backbone: Backbone architecture
        num_epochs: Number of training epochs
        learning_rate: Learning rate
        device: Device to use
        save_path: Path to save trained model
        
    Returns:
        Trained model
    """
    device = device if device != 'auto' else ('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Initialize model
    model = ChessPieceClassifier(backbone=backbone)
    model.to(device)
    
    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
    
    # Training loop
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            outputs = model(data)
            
            # Calculate loss
            loss = criterion(outputs['class_logits'], target)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        scheduler.step()
        
        # Validation
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                outputs = model(data)
                
                val_loss += criterion(outputs['class_logits'], target).item()
                _, predicted = torch.max(outputs['class_logits'], 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()
        
        print(f'Epoch {epoch+1}/{num_epochs}: '
              f'Train Loss: {train_loss/len(train_loader):.4f}, '
              f'Val Loss: {val_loss/len(val_loader):.4f}, '
              f'Val Acc: {100*correct/total:.2f}%')
    
    # Save model
    torch.save(model.state_dict(), save_path)
    print(f"✅ Model saved to {save_path}")
    
    return model


if __name__ == "__main__":
    # Test classifier
    classifier = ChessPieceClassifierWrapper()
    
    # Create dummy piece image
    test_piece = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    
    # Test classification
    result = classifier.classify_piece(test_piece, return_probabilities=True)
    print(f"Classified piece: {result}")
