"""
Chess piece detection models.

Includes:
- AlexNet-variant piece classifier
- YOLOv8 detection fine-tuning
- InceptionV3 transfer learning
"""

from .piece_classifier import PieceClassifierNet, create_piece_classifier
from .detector_yolo import YOLOChessDetector, setup_yolo_training
from .detector_inception import InceptionChessDetector, create_inception_model

__all__ = [
    'PieceClassifierNet',
    'create_piece_classifier',
    'YOLOChessDetector',
    'setup_yolo_training',
    'InceptionChessDetector',
    'create_inception_model',
]
