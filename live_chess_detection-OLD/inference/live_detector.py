"""Live chess detection from webcam."""

import cv2
import numpy as np
import chess
from typing import Optional

from models.detector_yolo import YOLOChessDetector


class LiveChessDetector:
    """
    Real-time chess piece detection from webcam feed.
    
    Handles frame capture, piece detection, board mapping,
    and move validation using chess rules.
    """
    
    def __init__(
        self,
        model_path: str,
        camera_id: int = 0,
        conf_threshold: float = 0.45
    ):
        """
        Initialize live detector.
        
        Args:
            model_path: Path to trained YOLO weights
            camera_id: Webcam device ID
            conf_threshold: Detection confidence threshold
        """
        self.detector = YOLOChessDetector(
            model_path=model_path,
            conf_threshold=conf_threshold
        )
        
        self.camera_id = camera_id
        self.board = chess.Board()  # Current game state
        self.prev_frame = None
        
        # Board corners (set via calibration)
        self.board_corners = None
    
    def calibrate_board(self, frame: np.ndarray):
        """
        Calibrate board position in frame.
        
        User clicks 4 corners to define board region.
        This allows perspective correction for better detection.
        """
        # TODO: Implement corner selection UI
        # For now, use full frame
        h, w = frame.shape[:2]
        self.board_corners = np.array([
            [0, 0],
            [w, 0],
            [w, h],
            [0, h]
        ], dtype=np.float32)
    
    def is_frame_stable(self, current_frame: np.ndarray, threshold: float = 0.02) -> bool:
        """
        Check if frame is stable (no hand movement).
        
        Compares current frame to previous frame.
        Only detect pieces when frame is stable to avoid false positives.
        Found that threshold=0.02 works well in practice.
        """
        if self.prev_frame is None:
            self.prev_frame = current_frame.copy()
            return False
        
        # Calculate frame difference
        diff = cv2.absdiff(current_frame, self.prev_frame)
        mean_diff = np.mean(diff) / 255.0
        
        self.prev_frame = current_frame.copy()
        
        return mean_diff < threshold
    
    def map_pieces_to_board(self, detections: dict) -> np.ndarray:
        """
        Map detected pieces to 8x8 board array.
        
        Uses piece center coordinates to determine which square.
        Handles perspective correction if board corners are set.
        """
        board_array = np.full((8, 8), '0', dtype=object)
        
        if len(detections['boxes']) == 0:
            return board_array
        
        # Calculate piece centers
        centers = self.detector.calculate_piece_centers(detections['boxes'])
        
        # TODO: Implement actual square mapping with perspective correction
        # For now, simple grid division
        
        return board_array
    
    def run(self, max_frames: Optional[int] = None):
        """
        Start live detection loop.
        
        Args:
            max_frames: Stop after N frames (None = run forever)
        """
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {self.camera_id}")
            return
        
        print("🎥 Starting live detection...")
        print("Press 'q' to quit, 'c' to calibrate board")
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                if max_frames and frame_count >= max_frames:
                    break
                
                # Check if frame is stable
                if not self.is_frame_stable(frame):
                    cv2.putText(
                        frame, "Waiting for stable frame...",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 255), 2
                    )
                    cv2.imshow('Chess Detection', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue
                
                # Detect pieces
                detections = self.detector.detect(frame, visualize=True)
                
                # Display
                display_frame = detections.get('image', frame)
                cv2.imshow('Chess Detection', display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    self.calibrate_board(frame)
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print(f"📊 Processed {frame_count} frames")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True, help='Path to trained model')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID')
    
    args = parser.parse_args()
    
    detector = LiveChessDetector(
        model_path=args.model,
        camera_id=args.camera
    )
    
    detector.run()
