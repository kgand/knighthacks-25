"""
Test suite for model implementations.

Tests the YOLO detector, Inception detector, and piece classifier.
"""

import pytest
import numpy as np
import torch
from models.detector_yolo import YOLOChessDetector
from models.detector_inception import InceptionChessDetectorWrapper
from models.piece_classifier import ChessPieceClassifierWrapper


class TestYOLODetector:
    """Test YOLO detector functionality."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = YOLOChessDetector(model_size='yolov8s')
        assert detector.model is not None
        assert detector.model_type == 'pytorch'
    
    def test_detection(self):
        """Test piece detection."""
        detector = YOLOChessDetector(model_size='yolov8s')
        
        # Create dummy image
        test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # Run detection
        results = detector.detect(test_img)
        
        assert 'boxes' in results
        assert 'classes' in results
        assert 'confidences' in results
        assert 'class_names' in results
        
        assert isinstance(results['boxes'], np.ndarray)
        assert isinstance(results['classes'], np.ndarray)
        assert isinstance(results['confidences'], np.ndarray)
    
    def test_piece_centers(self):
        """Test piece center calculation."""
        detector = YOLOChessDetector(model_size='yolov8s')
        
        # Test with empty boxes
        centers = detector.calculate_piece_centers(np.array([]))
        assert len(centers) == 0
        
        # Test with dummy boxes
        boxes = np.array([[100, 100, 200, 200], [300, 300, 400, 400]])
        centers = detector.calculate_piece_centers(boxes)
        assert len(centers) == 2
        assert centers.shape[1] == 2  # x, y coordinates


class TestInceptionDetector:
    """Test Inception detector functionality."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = InceptionChessDetectorWrapper()
        assert detector.model is not None
        assert detector.device is not None
    
    def test_detection(self):
        """Test piece detection."""
        detector = InceptionChessDetectorWrapper()
        
        # Create dummy image
        test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # Run detection
        results = detector.detect(test_img)
        
        assert 'boxes' in results
        assert 'classes' in results
        assert 'confidences' in results
        assert 'class_names' in results
        
        assert isinstance(results['boxes'], np.ndarray)
        assert isinstance(results['classes'], np.ndarray)
        assert isinstance(results['confidences'], np.ndarray)
    
    def test_piece_centers(self):
        """Test piece center calculation."""
        detector = InceptionChessDetectorWrapper()
        
        # Test with empty boxes
        centers = detector.calculate_piece_centers(np.array([]))
        assert len(centers) == 0
        
        # Test with dummy boxes
        boxes = np.array([[100, 100, 200, 200], [300, 300, 400, 400]])
        centers = detector.calculate_piece_centers(boxes)
        assert len(centers) == 2
        assert centers.shape[1] == 2  # x, y coordinates


class TestPieceClassifier:
    """Test piece classifier functionality."""
    
    def test_initialization(self):
        """Test classifier initialization."""
        classifier = ChessPieceClassifierWrapper()
        assert classifier.model is not None
        assert classifier.device is not None
    
    def test_classify_piece(self):
        """Test piece classification."""
        classifier = ChessPieceClassifierWrapper()
        
        # Create dummy piece image
        piece_img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        
        # Test classification
        result = classifier.classify_piece(piece_img)
        assert isinstance(result, str)
        
        # Test with probabilities
        result_with_probs = classifier.classify_piece(piece_img, return_probabilities=True)
        assert isinstance(result_with_probs, dict)
        assert 'class' in result_with_probs
        assert 'confidence' in result_with_probs
    
    def test_classify_pieces(self):
        """Test batch piece classification."""
        classifier = ChessPieceClassifierWrapper()
        
        # Create dummy piece images
        piece_imgs = [
            np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
            for _ in range(3)
        ]
        
        # Test batch classification
        results = classifier.classify_pieces(piece_imgs)
        assert len(results) == 3
        assert all(isinstance(result, str) for result in results)
    
    def test_get_piece_features(self):
        """Test feature extraction."""
        classifier = ChessPieceClassifierWrapper()
        
        # Create dummy piece image
        piece_img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        
        # Test feature extraction
        features = classifier.get_piece_features(piece_img)
        assert isinstance(features, np.ndarray)
        assert len(features.shape) == 1  # 1D feature vector


class TestModelIntegration:
    """Test model integration and compatibility."""
    
    def test_model_compatibility(self):
        """Test that models can work together."""
        # Test YOLO detector
        yolo_detector = YOLOChessDetector(model_size='yolov8s')
        
        # Test Inception detector
        inception_detector = InceptionChessDetectorWrapper()
        
        # Test piece classifier
        piece_classifier = ChessPieceClassifierWrapper()
        
        # All should initialize without errors
        assert yolo_detector.model is not None
        assert inception_detector.model is not None
        assert piece_classifier.model is not None
    
    def test_detection_consistency(self):
        """Test that detectors produce consistent results."""
        yolo_detector = YOLOChessDetector(model_size='yolov8s')
        inception_detector = InceptionChessDetectorWrapper()
        
        # Create dummy image
        test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # Run detection with both models
        yolo_results = yolo_detector.detect(test_img)
        inception_results = inception_detector.detect(test_img)
        
        # Both should return valid results
        assert 'boxes' in yolo_results
        assert 'boxes' in inception_results
        
        # Results should have consistent structure
        assert isinstance(yolo_results['boxes'], np.ndarray)
        assert isinstance(inception_results['boxes'], np.ndarray)


if __name__ == "__main__":
    pytest.main([__file__])
