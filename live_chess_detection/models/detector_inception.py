"""
InceptionV3-based chess piece detector.

Alternative architecture for piece detection using InceptionV3
as backbone with custom classification head.
"""

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2


class InceptionChessDetector(nn.Module):
    """
    InceptionV3-based chess piece detector.
    
    Uses InceptionV3 as backbone with custom detection head
    for chess piece detection and classification.
    """
    
    def __init__(
        self,
        num_classes: int = 12,  # 6 piece types * 2 colors
        pretrained: bool = True,
        dropout_rate: float = 0.5
    ):
        """
        Initialize InceptionV3 detector.
        
        Args:
            num_classes: Number of piece classes
            pretrained: Whether to use pretrained weights
            dropout_rate: Dropout rate for regularization
        """
        super(InceptionChessDetector, self).__init__()
        
        # Load pretrained InceptionV3
        self.backbone = models.inception_v3(pretrained=pretrained, aux_logits=False)
        
        # Get number of input features
        num_features = self.backbone.fc.in_features
        
        # Replace classifier with detection head
        self.backbone.fc = nn.Identity()  # Remove original classifier
        
        # Detection head
        self.detection_head = nn.Sequential(
            nn.Linear(num_features, 1024),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(1024, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, num_classes)
        )
        
        # Bounding box regression head
        self.bbox_head = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 4)  # x, y, width, height
        )
        
        # Confidence head
        self.confidence_head = nn.Sequential(
            nn.Linear(num_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
        
        self.num_classes = num_classes
        self.class_names = {
            0: 'white-king', 1: 'white-queen', 2: 'white-rook',
            3: 'white-bishop', 4: 'white-knight', 5: 'white-pawn',
            6: 'black-king', 7: 'black-queen', 8: 'black-rook',
            9: 'black-bishop', 10: 'black-knight', 11: 'black-pawn'
        }
    
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
        class_logits = self.detection_head(features)
        bbox_regression = self.bbox_head(features)
        confidence = self.confidence_head(features)
        
        return {
            'class_logits': class_logits,
            'bbox_regression': bbox_regression,
            'confidence': confidence
        }
    
    def predict(self, x: torch.Tensor, threshold: float = 0.5) -> Dict:
        """
        Make predictions on input tensor.
        
        Args:
            x: Input tensor
            threshold: Confidence threshold
            
        Returns:
            Dictionary with predictions
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(x)
            
            # Apply softmax to class logits
            class_probs = torch.softmax(outputs['class_logits'], dim=1)
            confidence = outputs['confidence']
            
            # Filter by confidence threshold
            valid_indices = confidence.squeeze() > threshold
            
            if valid_indices.sum() > 0:
                return {
                    'class_probs': class_probs[valid_indices],
                    'bbox_regression': outputs['bbox_regression'][valid_indices],
                    'confidence': confidence[valid_indices],
                    'class_names': self.class_names
                }
            else:
                return {
                    'class_probs': torch.empty(0, self.num_classes),
                    'bbox_regression': torch.empty(0, 4),
                    'confidence': torch.empty(0, 1),
                    'class_names': self.class_names
                }


class InceptionChessDetectorWrapper:
    """
    Wrapper for InceptionV3 detector with preprocessing and postprocessing.
    
    Provides easy-to-use interface similar to YOLO detector.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        conf_threshold: float = 0.45,
        device: str = 'auto'
    ):
        """
        Initialize detector wrapper.
        
        Args:
            model_path: Path to trained model weights
            conf_threshold: Confidence threshold
            device: Device to use
        """
        self.conf_threshold = conf_threshold
        self.device = device if device != 'auto' else ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model
        self.model = InceptionChessDetector()
        
        # Load weights if provided
        if model_path and torch.load(model_path, map_location=self.device):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            print(f"✅ Loaded model from {model_path}")
        
        self.model.to(self.device)
        self.model.eval()
        
        # Setup preprocessing
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((299, 299)),  # InceptionV3 input size
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def detect(
        self,
        image: np.ndarray,
        img_size: int = 299,
        visualize: bool = False
    ) -> Dict:
        """
        Detect pieces in image.
        
        Args:
            image: Input image
            img_size: Image size (ignored for InceptionV3)
            visualize: Whether to return annotated image
            
        Returns:
            Detection results
        """
        # Preprocess image
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply transforms
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Run inference
        with torch.no_grad():
            predictions = self.model.predict(input_tensor, self.conf_threshold)
        
        # Convert to numpy arrays
        class_probs = predictions['class_probs'].cpu().numpy()
        bbox_regression = predictions['bbox_regression'].cpu().numpy()
        confidence = predictions['confidence'].cpu().numpy()
        
        # Parse results
        boxes = []
        classes = []
        confidences = []
        
        for i in range(len(class_probs)):
            # Get class with highest probability
            class_id = np.argmax(class_probs[i])
            class_conf = class_probs[i][class_id]
            
            # Get bounding box (convert from regression to absolute coordinates)
            bbox = bbox_regression[i]
            x, y, w, h = bbox
            
            # Convert to corner format
            x1 = max(0, x - w/2)
            y1 = max(0, y - h/2)
            x2 = min(image.shape[1], x + w/2)
            y2 = min(image.shape[0], y + h/2)
            
            boxes.append([x1, y1, x2, y2])
            classes.append(class_id)
            confidences.append(float(class_conf))
        
        output = {
            'boxes': np.array(boxes) if boxes else np.empty((0, 4)),
            'classes': np.array(classes) if classes else np.empty((0,)),
            'confidences': np.array(confidences) if confidences else np.empty((0,)),
            'class_names': predictions['class_names']
        }
        
        if visualize:
            # Draw boxes on image
            vis_image = image.copy()
            for box, cls, conf in zip(boxes, classes, confidences):
                x1, y1, x2, y2 = map(int, box)
                color = (0, 255, 0)  # Green
                cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, 2)
                
                # Add label
                label = f"{predictions['class_names'].get(cls, cls)}: {conf:.2f}"
                cv2.putText(vis_image, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            output['image'] = vis_image
        
        return output
    
    def calculate_piece_centers(self, boxes: np.ndarray) -> np.ndarray:
        """
        Calculate center points of detected pieces.
        
        Args:
            boxes: Bounding boxes array
            
        Returns:
            Center points array
        """
        if len(boxes) == 0:
            return np.empty((0, 2))
        
        centers = []
        for box in boxes:
            x1, y1, x2, y2 = box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            centers.append([center_x, center_y])
        
        return np.array(centers)


def train_inception_detector(
    train_loader,
    val_loader,
    num_epochs: int = 50,
    learning_rate: float = 0.001,
    device: str = 'auto',
    save_path: str = 'models/inception/chess_detector.pth'
):
    """
    Train InceptionV3 detector.
    
    Args:
        train_loader: Training data loader
        val_loader: Validation data loader
        num_epochs: Number of training epochs
        learning_rate: Learning rate
        device: Device to use
        save_path: Path to save trained model
        
    Returns:
        Trained model
    """
    device = device if device != 'auto' else ('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Initialize model
    model = InceptionChessDetector()
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
            
            # Calculate loss (simplified - would need proper loss function for detection)
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
    # Test detector
    detector = InceptionChessDetectorWrapper()
    
    # Create dummy image
    test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    # Test detection
    results = detector.detect(test_img)
    print(f"Detected {len(results['boxes'])} pieces")
