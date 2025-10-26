"""
Live chess detection from webcam.

Real-time chess piece detection and board state tracking
using computer vision and deep learning models.
"""

import cv2
import numpy as np
import chess
from typing import Optional, Dict, List, Tuple
import time

from models.detector_yolo import YOLOChessDetector
from utils.chess_logic import ChessBoard
from utils.video_utils import VideoCapture, stabilize_frame, detect_motion
from utils.logger import get_global_logger


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
        conf_threshold: float = 0.45,
        board_corners: Optional[np.ndarray] = None
    ):
        """
        Initialize live detector.
        
        Args:
            model_path: Path to trained YOLO weights
            camera_id: Webcam device ID
            conf_threshold: Detection confidence threshold
            board_corners: Predefined board corners (4x2 array)
        """
        self.detector = YOLOChessDetector(
            model_path=model_path,
            conf_threshold=conf_threshold
        )
        
        self.camera_id = camera_id
        self.board = ChessBoard()  # Current game state
        self.prev_frame = None
        self.board_corners = board_corners
        self.logger = get_global_logger()
        
        # Detection parameters
        self.stability_threshold = 0.02
        self.motion_threshold = 30.0
        self.detection_interval = 5  # Detect every N frames
        
        # State tracking
        self.frame_count = 0
        self.last_detection_time = 0
        self.detection_cooldown = 1.0  # Minimum time between detections
        
        # Board mapping
        self.square_size = None
        self.board_center = None
    
    def calibrate_board(self, frame: np.ndarray) -> bool:
        """
        Calibrate board position in frame.
        
        User clicks 4 corners to define board region.
        This allows perspective correction for better detection.
        
        Args:
            frame: Current frame for calibration
            
        Returns:
            True if calibration successful
        """
        self.logger.log_info("Starting board calibration", "LiveDetector")
        
        # For now, use automatic corner detection
        # In a real implementation, this would be interactive
        corners = self._detect_board_corners(frame)
        
        if corners is not None:
            self.board_corners = corners
            self.logger.log_info(f"Board calibrated with corners: {corners}", "LiveDetector")
            return True
        else:
            self.logger.log_warning("Failed to detect board corners", "LiveDetector")
            return False
    
    def _detect_board_corners(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Automatically detect board corners.
        
        Args:
            frame: Input frame
            
        Returns:
            4x2 array of corner coordinates or None
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find largest contour (likely the board)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(largest_contour, True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True)
        
        # Check if we have 4 corners
        if len(approx) == 4:
            corners = approx.reshape(4, 2)
            return corners
        
        return None
    
    def is_frame_stable(self, current_frame: np.ndarray) -> bool:
        """
        Check if frame is stable (no hand movement).
        
        Compares current frame to previous frame.
        Only detect pieces when frame is stable to avoid false positives.
        
        Args:
            current_frame: Current frame
            
        Returns:
            True if frame is stable
        """
        if self.prev_frame is None:
            self.prev_frame = current_frame.copy()
            return False
        
        # Check for motion
        has_motion, motion_mask = detect_motion(
            current_frame, self.prev_frame, self.motion_threshold
        )
        
        # Check for stability
        is_stable, _ = stabilize_frame(
            current_frame, self.prev_frame, self.stability_threshold
        )
        
        self.prev_frame = current_frame.copy()
        
        return not has_motion and is_stable
    
    def map_pieces_to_board(self, detections: Dict) -> np.ndarray:
        """
        Map detected pieces to 8x8 board array.
        
        Uses piece center coordinates to determine which square.
        Handles perspective correction if board corners are set.
        
        Args:
            detections: Detection results from model
            
        Returns:
            8x8 board array with piece symbols
        """
        board_array = np.full((8, 8), '.', dtype=object)
        
        if len(detections['boxes']) == 0:
            return board_array
        
        # Calculate piece centers
        centers = self.detector.calculate_piece_centers(detections['boxes'])
        
        # Map centers to board squares
        for i, (center, class_id, confidence) in enumerate(zip(
            centers, detections['classes'], detections['confidences']
        )):
            if confidence < self.conf_threshold:
                continue
            
            # Convert center to board coordinates
            square = self._center_to_square(center)
            if square is not None:
                # Get piece symbol from class
                piece_symbol = self._class_to_piece_symbol(class_id)
                if piece_symbol:
                    row, col = square
                    board_array[row, col] = piece_symbol
        
        return board_array
    
    def _center_to_square(self, center: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Convert piece center to board square coordinates.
        
        Args:
            center: Piece center coordinates [x, y]
            
        Returns:
            (row, col) coordinates or None if invalid
        """
        if self.board_corners is None:
            # Simple grid division (assumes board fills most of frame)
            h, w = self.prev_frame.shape[:2]
            square_w = w / 8
            square_h = h / 8
            
            col = int(center[0] / square_w)
            row = int(center[1] / square_h)
            
            if 0 <= row < 8 and 0 <= col < 8:
                return row, col
        else:
            # Perspective-corrected mapping
            # This would require more complex geometric calculations
            # For now, use simple approach
            pass
        
        return None
    
    def _class_to_piece_symbol(self, class_id: int) -> Optional[str]:
        """
        Convert class ID to piece symbol.
        
        Args:
            class_id: Model class ID
            
        Returns:
            Piece symbol or None
        """
        piece_map = {
            0: 'K', 1: 'Q', 2: 'R', 3: 'B', 4: 'N', 5: 'P',  # White pieces
            6: 'k', 7: 'q', 8: 'r', 9: 'b', 10: 'n', 11: 'p'  # Black pieces
        }
        
        return piece_map.get(class_id)
    
    def update_board_state(self, board_array: np.ndarray) -> bool:
        """
        Update internal board state from detected pieces.
        
        Args:
            board_array: 8x8 array with piece symbols
            
        Returns:
            True if board state was updated
        """
        # Convert array to FEN
        fen = self._array_to_fen(board_array)
        
        # Validate FEN
        if not self._validate_fen(fen):
            return False
        
        # Update board
        try:
            self.board = ChessBoard(fen)
            return True
        except Exception as e:
            self.logger.log_error(e, "BoardStateUpdate")
            return False
    
    def _array_to_fen(self, board_array: np.ndarray) -> str:
        """
        Convert board array to FEN string.
        
        Args:
            board_array: 8x8 array with piece symbols
            
        Returns:
            FEN string
        """
        fen_rows = []
        
        for row in board_array:
            fen_row = ""
            empty_count = 0
            
            for piece in row:
                if piece == '.':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += piece
            
            if empty_count > 0:
                fen_row += str(empty_count)
            
            fen_rows.append(fen_row)
        
        # Join rows with '/'
        fen = '/'.join(fen_rows)
        
        # Add basic FEN components (simplified)
        fen += " w - - 0 1"
        
        return fen
    
    def _validate_fen(self, fen: str) -> bool:
        """
        Validate FEN string.
        
        Args:
            fen: FEN string to validate
            
        Returns:
            True if FEN is valid
        """
        try:
            chess.Board(fen)
            return True
        except Exception:
            return False
    
    def detect_pieces(self, frame: np.ndarray) -> Dict:
        """
        Detect pieces in current frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Detection results
        """
        start_time = time.time()
        
        # Run detection
        detections = self.detector.detect(frame, visualize=True)
        
        # Map to board
        board_array = self.map_pieces_to_board(detections)
        
        # Update board state
        self.update_board_state(board_array)
        
        processing_time = time.time() - start_time
        
        # Log detection results
        num_pieces = len(detections['boxes'])
        avg_conf = np.mean(detections['confidences']) if num_pieces > 0 else 0
        self.logger.log_detection(num_pieces, avg_conf, processing_time)
        
        return {
            'detections': detections,
            'board_array': board_array,
            'board_fen': self.board.get_fen(),
            'processing_time': processing_time
        }
    
    def run(self, max_frames: Optional[int] = None, show_video: bool = True):
        """
        Start live detection loop.
        
        Args:
            max_frames: Stop after N frames (None = run forever)
            show_video: Whether to display video window
        """
        with VideoCapture(self.camera_id) as cap:
            if not cap.is_opened():
                self.logger.log_error(Exception(f"Failed to open camera {self.camera_id}"), "LiveDetector")
                return
            
            self.logger.log_info("Starting live detection", "LiveDetector")
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
                        if show_video:
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
                    results = self.detect_pieces(frame)
                    
                    # Display results
                    if show_video:
                        display_frame = results['detections']['image']
                        
                        # Add board state info
                        cv2.putText(
                            display_frame, f"Pieces: {len(results['detections']['boxes'])}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                        )
                        
                        cv2.imshow('Chess Detection', display_frame)
                    
                    # Handle keyboard input
                    if show_video:
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q'):
                            break
                        elif key == ord('c'):
                            self.calibrate_board(frame)
            
            finally:
                if show_video:
                    cv2.destroyAllWindows()
                self.logger.log_info(f"Processed {frame_count} frames", "LiveDetector")
    
    def get_current_board(self) -> ChessBoard:
        """
        Get current board state.
        
        Returns:
            Current ChessBoard instance
        """
        return self.board
    
    def get_board_fen(self) -> str:
        """
        Get current board FEN.
        
        Returns:
            Current FEN string
        """
        return self.board.get_fen()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True, help='Path to trained model')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID')
    parser.add_argument('--conf', type=float, default=0.45, help='Confidence threshold')
    
    args = parser.parse_args()
    
    detector = LiveChessDetector(
        model_path=args.model,
        camera_id=args.camera,
        conf_threshold=args.conf
    )
    
    detector.run()
