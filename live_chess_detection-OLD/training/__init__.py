"""Training scripts for chess detection models."""

from .train_classifier import train_piece_classifier
from .amd_utils import setup_amd_device, get_optimal_batch_size

__all__ = [
    'train_piece_classifier',
    'setup_amd_device',
    'get_optimal_batch_size',
]
