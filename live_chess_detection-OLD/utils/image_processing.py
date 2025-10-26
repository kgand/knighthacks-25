"""Image processing utilities."""

import cv2
import numpy as np
from typing import Tuple, List


def crop_board(
    image: np.ndarray,
    corners: List[Tuple[int, int]]
) -> np.ndarray:
    """
    Crop board region from image.
    
    Args:
        image: Input image
        corners: 4 corner points [top-left, top-right, bottom-right, bottom-left]
        
    Returns:
        Cropped image
    """
    x_coords = [c[0] for c in corners]
    y_coords = [c[1] for c in corners]
    
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    
    return image[y_min:y_max, x_min:x_max]


def perspective_transform(
    image: np.ndarray,
    src_points: np.ndarray,
    dst_size: Tuple[int, int] = (512, 512)
) -> np.ndarray:
    """
    Apply perspective transformation to get top-down view.
    
    Essential for angled camera views. Converts trapezoidal board
    to square image for better piece detection.
    
    Reference: https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html
    """
    # Define destination points (square)
    dst_points = np.array([
        [0, 0],
        [dst_size[0], 0],
        [dst_size[0], dst_size[1]],
        [0, dst_size[1]]
    ], dtype=np.float32)
    
    # Calculate transformation matrix
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    
    # Apply transformation
    warped = cv2.warpPerspective(
        image,
        matrix,
        dst_size,
        flags=cv2.INTER_LINEAR
    )
    
    return warped


def enhance_image(image: np.ndarray) -> np.ndarray:
    """
    Enhance image for better piece detection.
    
    Applies contrast enhancement and noise reduction.
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_l = clahe.apply(l)
    
    # Merge channels
    enhanced_lab = cv2.merge([enhanced_l, a, b])
    
    # Convert back to BGR
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    # Slight denoising
    enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
    
    return enhanced
