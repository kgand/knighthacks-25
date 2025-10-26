"""
YOLOv8 chess piece detector.

Fine-tunes YOLOv8 for real-time piece detection.
Handles full board images and returns piece bounding boxes.
Supports both PyTorch (.pt) and TensorFlow (.h5) model formats.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import torch
from ultralytics import YOLO

# TensorFlow will be imported lazily when needed for .h5 models
# This avoids compatibility issues when TensorFlow is not needed


class YOLOChessDetector:
    """
    Wrapper for YOLOv8 chess piece detection.
    
    Provides unified interface for training and inference.
    Handles AMD GPU compatibility automatically.
    Supports both PyTorch (.pt) and TensorFlow (.h5) models.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        model_size: str = 'yolov8s',
        conf_threshold: float = 0.45,
        device: str = 'auto'
    ):
        """
        Initialize detector.
        
        Args:
            model_path: Path to trained weights (.pt or .h5)
            model_size: Model variant (n/s/m/l/x)
            conf_threshold: Confidence threshold for detections
            device: 'auto', 'cuda', 'rocm', or 'cpu'
        """
        self.conf_threshold = conf_threshold
        self.model = None
        self.model_type = None  # 'pytorch' or 'tensorflow'
        self.class_names = {}
        
        # Handle device selection
        if device == 'auto':
            if torch.cuda.is_available():
                device = 'cuda'
            else:
                device = 'cpu'
        elif device == 'rocm':
            device = 'cuda'  # PyTorch treats ROCm as CUDA
        
        self.device = device
        
        # Load model based on file extension
        if model_path and Path(model_path).exists():
            model_path_str = str(model_path)
            
            if model_path_str.endswith('.h5'):
                # Load TensorFlow/Keras model
                self._load_h5_model(model_path_str)
            elif model_path_str.endswith('.pt'):
                # Load PyTorch YOLO model
                self._load_pt_model(model_path_str)
            else:
                raise ValueError(f"Unsupported model format: {model_path}. Use .pt or .h5")
        else:
            # Load pretrained PyTorch model
            print(f"Loading pretrained {model_size}")
            self._load_pt_model(f"{model_size}.pt")
    
    def _load_pt_model(self, model_path: str):
        """Load PyTorch YOLO model."""
        print(f"Loading PyTorch model from {model_path}")
        self.model = YOLO(model_path, task='detect')
        self.model.to(self.device)
        self.model_type = 'pytorch'
        print("✅ PyTorch model loaded successfully")
    
    def _load_h5_model(self, model_path: str):
        """Load TensorFlow/Keras .h5 model."""
        # Import TensorFlow only when needed (lazy import)
        try:
            import tensorflow as tf
            from tensorflow import keras
        except ImportError:
            raise ImportError(
                "TensorFlow is not installed. Install it with: pip install tensorflow\n"
                "Or if you have NumPy 2.x compatibility issues, try:\n"
                "  pip install 'numpy<2' tensorflow"
            )
        
        print(f"Loading TensorFlow model from {model_path}")
        
        # Set TensorFlow device
        if self.device == 'cuda':
            # Use GPU if available
            physical_devices = tf.config.list_physical_devices('GPU')
            if physical_devices:
                print(f"TensorFlow GPU available: {len(physical_devices)} device(s)")
                for device in physical_devices:
                    tf.config.experimental.set_memory_growth(device, True)
            else:
                print("TensorFlow: No GPU found, using CPU")
        
        # Load the model
        self.model = keras.models.load_model(model_path, compile=False)
        self.model_type = 'tensorflow'
        
        # Try to extract class names from model metadata
        if hasattr(self.model, 'class_names'):
            self.class_names = self.model.class_names
        else:
            # Default chess piece classes
            self.class_names = {
                0: 'white-king', 1: 'white-queen', 2: 'white-rook',
                3: 'white-bishop', 4: 'white-knight', 5: 'white-pawn',
                6: 'black-king', 7: 'black-queen', 8: 'black-rook',
                9: 'black-bishop', 10: 'black-knight', 11: 'black-pawn'
            }
        
        print("✅ TensorFlow model loaded successfully")
        print(f"   Model input shape: {self.model.input_shape}")
        print(f"   Model output shape: {self.model.output_shape}")
    
    def detect(
        self,
        image: np.ndarray,
        img_size: int = 1024,
        visualize: bool = False
    ) -> Dict:
        """
        Detect pieces in an image.
        
        Args:
            image: Input image (BGR or RGB)
            img_size: Inference image size
            visualize: Whether to return annotated image
            
        Returns:
            Dict with 'boxes', 'classes', 'confidences', and optional 'image'
        """
        if self.model_type == 'pytorch':
            return self._detect_pytorch(image, img_size, visualize)
        elif self.model_type == 'tensorflow':
            return self._detect_tensorflow(image, img_size, visualize)
        else:
            raise RuntimeError("No model loaded")
    
    def _detect_pytorch(
        self,
        image: np.ndarray,
        img_size: int,
        visualize: bool
    ) -> Dict:
        """Run detection using PyTorch YOLO model."""
        # Run inference
        results = self.model.predict(
            image,
            imgsz=img_size,
            conf=self.conf_threshold,
            verbose=False
        )[0]
        
        # Parse results
        boxes = []
        classes = []
        confidences = []
        
        for box in results.boxes:
            # Extract box coordinates [x1, y1, x2, y2]
            bbox = box.xyxy.cpu().numpy()[0]
            
            # Get class and confidence
            class_id = int(box.cls.cpu().numpy()[0])
            confidence = float(box.conf.cpu().numpy()[0])
            
            boxes.append(bbox)
            classes.append(class_id)
            confidences.append(confidence)
        
        output = {
            'boxes': np.array(boxes) if boxes else np.empty((0, 4)),
            'classes': np.array(classes) if classes else np.empty((0,)),
            'confidences': np.array(confidences) if confidences else np.empty((0,)),
            'class_names': results.names
        }
        
        if visualize:
            # Get annotated image from results
            output['image'] = results.plot()
        
        return output
    
    def _detect_tensorflow(
        self,
        image: np.ndarray,
        img_size: int,
        visualize: bool
    ) -> Dict:
        """Run detection using TensorFlow/Keras model."""
        # Preprocess image
        orig_h, orig_w = image.shape[:2]
        
        # Resize to model input size
        input_shape = self.model.input_shape[1:3]  # (height, width)
        processed = cv2.resize(image, (input_shape[1], input_shape[0]))
        
        # Normalize to [0, 1]
        processed = processed.astype(np.float32) / 255.0
        
        # Add batch dimension
        processed = np.expand_dims(processed, axis=0)
        
        # Run inference
        predictions = self.model.predict(processed, verbose=0)
        
        # Parse predictions based on output format
        # This assumes YOLO-style output: [batch, num_predictions, 5+num_classes]
        # Format: [x_center, y_center, width, height, confidence, class_scores...]
        boxes = []
        classes = []
        confidences = []
        
        if isinstance(predictions, list):
            predictions = predictions[0]  # Take first output if multiple
        
        # Squeeze batch dimension
        predictions = predictions[0] if predictions.shape[0] == 1 else predictions
        
        for pred in predictions:
            # Check if prediction has enough elements
            if len(pred) < 5:
                continue
            
            # Extract confidence (5th element)
            objectness = pred[4]
            
            if objectness < self.conf_threshold:
                continue
            
            # Extract box coordinates (first 4 elements)
            x_center, y_center, width, height = pred[:4]
            
            # Extract class scores (after first 5 elements)
            class_scores = pred[5:] if len(pred) > 5 else np.array([objectness])
            class_id = np.argmax(class_scores)
            class_conf = class_scores[class_id] if len(class_scores) > 0 else objectness
            
            # Calculate final confidence
            confidence = objectness * class_conf
            
            if confidence < self.conf_threshold:
                continue
            
            # Convert from center format to corner format
            # Scale back to original image size
            x1 = (x_center - width / 2) * orig_w / input_shape[1]
            y1 = (y_center - height / 2) * orig_h / input_shape[0]
            x2 = (x_center + width / 2) * orig_w / input_shape[1]
            y2 = (y_center + height / 2) * orig_h / input_shape[0]
            
            boxes.append([x1, y1, x2, y2])
            classes.append(int(class_id))
            confidences.append(float(confidence))
        
        output = {
            'boxes': np.array(boxes) if boxes else np.empty((0, 4)),
            'classes': np.array(classes) if classes else np.empty((0,)),
            'confidences': np.array(confidences) if confidences else np.empty((0,)),
            'class_names': self.class_names
        }
        
        if visualize:
            # Draw boxes on image
            vis_image = image.copy()
            for box, cls, conf in zip(boxes, classes, confidences):
                x1, y1, x2, y2 = map(int, box)
                color = (0, 255, 0)  # Green
                cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, 2)
                
                # Add label
                label = f"{self.class_names.get(cls, cls)}: {conf:.2f}"
                cv2.putText(vis_image, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            output['image'] = vis_image
        
        return output
    
    def detect_batch(
        self,
        images: List[np.ndarray],
        img_size: int = 1024
    ) -> List[Dict]:
        """Batch detection for multiple images."""
        results = []
        for img in images:
            result = self.detect(img, img_size=img_size)
            results.append(result)
        return results
    
    def calculate_piece_centers(self, boxes: np.ndarray) -> np.ndarray:
        """
        Calculate center points of detected pieces.
        
        For chess pieces, we use center of bottom of bbox
        since pieces are taller than their base.
        Found that using geometric center doesn't work well for mapping to squares.
        """
        if len(boxes) == 0:
            return np.empty((0, 2))
        
        centers = []
        for box in boxes:
            x1, y1, x2, y2 = box
            # Center of bottom edge
            center_x = (x1 + x2) / 2
            center_y = y2 - (y2 - y1) / 3  # 1/3 up from bottom
            centers.append([center_x, center_y])
        
        return np.array(centers)


def setup_yolo_training(
    data_yaml: str,
    model_size: str = 'yolov8s',
    epochs: int = 50,
    batch_size: int = 4,
    img_size: int = 1024,
    device: str = 'auto',
    output_dir: str = 'models/yolo/trained',
    **kwargs
):
    """
    Configure and start YOLO training.
    
    Args:
        data_yaml: Path to dataset config
        model_size: Model variant
        epochs: Training epochs
        batch_size: Batch size (adjust for GPU memory)
        img_size: Training image size
        device: Device to use
        output_dir: Where to save checkpoints
        **kwargs: Additional training arguments
        
    Returns:
        Trained model
    """
    # Handle device
    if device == 'rocm':
        device = 'cuda'
    
    # Load pretrained model
    model = YOLO(f"{model_size}.pt")
    
    # Training arguments
    # Reference: https://docs.ultralytics.com/modes/train/
    train_args = {
        'data': data_yaml,
        'epochs': epochs,
        'batch': batch_size,
        'imgsz': img_size,
        'device': device,
        'project': output_dir,
        'name': 'chess_detector',
        'patience': 10,  # Early stopping patience
        'save': True,
        'save_period': 5,  # Save every 5 epochs
        'cache': False,  # Don't cache (large dataset)
        'workers': 8,  # Data loading workers
        'optimizer': 'AdamW',
        'lr0': 0.0001,  # Initial learning rate
        'lrf': 0.01,  # Final learning rate factor
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'box': 7.5,  # Box loss gain
        'cls': 0.5,  # Class loss gain
        'dfl': 1.5,  # DFL loss gain
        'pose': 12.0,
        'kobj': 1.0,
        'label_smoothing': 0.0,
        'nbs': 64,
        'hsv_h': 0.015,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 5.0,
        'translate': 0.1,
        'scale': 0.2,
        'shear': 0.0,
        'perspective': 0.0,
        'flipud': 0.0,
        'fliplr': 0.5,
        'mosaic': 0.8,
        'mixup': 0.1,
    }
    
    # Override with any custom args
    train_args.update(kwargs)
    
    print("🏋️ Starting YOLO training...")
    print(f"Device: {device}")
    print(f"Batch size: {batch_size}")
    print(f"Image size: {img_size}")
    print(f"Epochs: {epochs}")
    
    # Train
    results = model.train(**train_args)
    
    print("✅ Training complete!")
    
    return model


if __name__ == "__main__":
    # Test detector
    detector = YOLOChessDetector(model_size='yolov8s')
    
    # Create dummy image
    test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    # Test detection
    results = detector.detect(test_img)
    print(f"Detected {len(results['boxes'])} pieces")
