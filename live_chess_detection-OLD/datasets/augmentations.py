"""Data augmentation pipelines for chess images."""

import random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import torch
from torchvision import transforms


class ChessAugmentations:
    """
    Augmentation pipeline specifically designed for chess images.
    
    Balances realism with data diversity. Avoids transformations
    that would make piece recognition unrealistic.
    """
    
    @staticmethod
    def random_brightness(img: Image.Image, factor_range: tuple = (0.8, 1.2)) -> Image.Image:
        """Random brightness adjustment."""
        factor = random.uniform(*factor_range)
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    
    @staticmethod
    def random_contrast(img: Image.Image, factor_range: tuple = (0.85, 1.15)) -> Image.Image:
        """Random contrast adjustment."""
        factor = random.uniform(*factor_range)
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)
    
    @staticmethod
    def random_blur(img: Image.Image, sigma_range: tuple = (0, 2)) -> Image.Image:
        """Random Gaussian blur."""
        sigma = random.uniform(*sigma_range)
        return img.filter(ImageFilter.GaussianBlur(radius=sigma))
    
    @staticmethod
    def random_rotation(img: Image.Image, degrees: float = 10) -> Image.Image:
        """Random rotation within degrees range."""
        angle = random.uniform(-degrees, degrees)
        return img.rotate(angle, resample=Image.BICUBIC, fillcolor=(255, 255, 255))


def get_training_transforms(input_size: int = 640, augment: bool = True):
    """
    Get training transforms for chess images.
    
    Args:
        input_size: Target image size
        augment: Whether to apply augmentations
        
    Returns:
        torchvision transforms
    """
    if augment:
        return transforms.Compose([
            transforms.Resize(int(input_size * 1.1)),
            transforms.RandomCrop(input_size),
            transforms.RandomHorizontalFlip(p=0.5),
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
            transforms.Resize(input_size),
            transforms.CenterCrop(input_size),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])


def get_validation_transforms(input_size: int = 640):
    """Get validation/test transforms (no augmentation)."""
    return get_training_transforms(input_size=input_size, augment=False)
