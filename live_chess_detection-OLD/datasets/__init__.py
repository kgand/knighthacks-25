"""
Chess dataset loading and generation modules.

This package handles data from multiple sources:
- Synthetic generated positions
- Roboflow annotations
- Kaggle images
- YouTube tournament videos
"""

from .synthetic_generator import ChessPositionGenerator, generate_synthetic_dataset
from .multi_source_loader import MultiSourceChessDataset, WeightedChessDataLoader
from .video_extractor import VideoFrameExtractor, YouTubeChessExtractor
from .augmentations import ChessAugmentations, get_training_transforms

__all__ = [
    'ChessPositionGenerator',
    'generate_synthetic_dataset',
    'MultiSourceChessDataset',
    'WeightedChessDataLoader',
    'VideoFrameExtractor',
    'YouTubeChessExtractor',
    'ChessAugmentations',
    'get_training_transforms',
]

__version__ = '1.0.0'
