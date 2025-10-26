"""
Board state prediction and validation.

Predicts chess board state from detected pieces and validates
the resulting position for legality.
"""

import numpy as np
import chess
from typing import Dict, List, Optional, Tuple, Union
from utils.chess_logic import ChessBoard, validate_fen, get_piece_color
from utils.logger import get_global_logger


class BoardPredictor:
    """
    Predicts chess board state from detected pieces.
    
    Handles piece detection results and converts them to
    valid chess board positions.
    """
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize board predictor.
        
        Args:
            confidence_threshold: Minimum confidence for piece detection
        """
        self.confidence_threshold = confidence_threshold
        self.logger = get_global_logger()
        
        # Piece class mapping
        self.piece_classes = {
            0: 'K', 1: 'Q', 2: 'R', 3: 'B', 4: 'N', 5: 'P',  # White
            6: 'k', 7: 'q', 8: 'r', 9: 'b', 10: 'n', 11: 'p'  # Black
        }
        
        # Expected piece counts for standard position
        self.expected_counts = {
            'K': 1, 'Q': 1, 'R': 2, 'B': 2, 'N': 2, 'P': 8,  # White
            'k': 1, 'q': 1, 'r': 2, 'b': 2, 'n': 2, 'p': 8   # Black
        }
    
    def predict_board_state(
        self,
        detections: Dict,
        board_corners: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Predict board state from piece detections.
        
        Args:
            detections: Detection results from model
            board_corners: Board corner coordinates for perspective correction
            
        Returns:
            Dictionary with predicted board state
        """
        if len(detections['boxes']) == 0:
            return self._create_empty_board()
        
        # Extract piece information
        pieces = self._extract_piece_info(detections)
        
        # Map pieces to board squares
        board_array = self._map_pieces_to_squares(pieces, board_corners)
        
        # Validate and correct board state
        corrected_board = self._validate_and_correct_board(board_array)
        
        # Convert to FEN
        fen = self._board_array_to_fen(corrected_board)
        
        # Validate FEN
        if not validate_fen(fen):
            self.logger.log_warning("Invalid FEN generated", "BoardPredictor")
            return self._create_empty_board()
        
        return {
            'board_array': corrected_board,
            'fen': fen,
            'pieces_detected': len(pieces),
            'confidence': self._calculate_board_confidence(pieces)
        }
    
    def _extract_piece_info(self, detections: Dict) -> List[Dict]:
        """
        Extract piece information from detections.
        
        Args:
            detections: Detection results
            
        Returns:
            List of piece dictionaries
        """
        pieces = []
        
        for i in range(len(detections['boxes'])):
            if detections['confidences'][i] < self.confidence_threshold:
                continue
            
            box = detections['boxes'][i]
            class_id = detections['classes'][i]
            confidence = detections['confidences'][i]
            
            # Calculate piece center
            x1, y1, x2, y2 = box
            center_x = (x1 + x2) / 2
            center_y = (y2 - (y2 - y1) / 3)  # 1/3 up from bottom
            
            piece = {
                'class_id': class_id,
                'piece_symbol': self.piece_classes.get(class_id, '?'),
                'confidence': confidence,
                'center': (center_x, center_y),
                'bbox': box
            }
            
            pieces.append(piece)
        
        return pieces
    
    def _map_pieces_to_squares(
        self,
        pieces: List[Dict],
        board_corners: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Map pieces to board squares.
        
        Args:
            pieces: List of detected pieces
            board_corners: Board corner coordinates
            
        Returns:
            8x8 board array
        """
        board_array = np.full((8, 8), '.', dtype=object)
        
        if board_corners is not None:
            # Perspective-corrected mapping
            board_array = self._map_with_perspective(pieces, board_corners)
        else:
            # Simple grid mapping
            board_array = self._map_simple_grid(pieces)
        
        return board_array
    
    def _map_simple_grid(self, pieces: List[Dict]) -> np.ndarray:
        """
        Simple grid-based piece mapping.
        
        Args:
            pieces: List of detected pieces
            
        Returns:
            8x8 board array
        """
        board_array = np.full((8, 8), '.', dtype=object)
        
        # Assume board fills most of the frame
        # This is a simplified approach
        for piece in pieces:
            center_x, center_y = piece['center']
            
            # Simple grid division
            col = int(center_x / 100)  # Adjust based on frame size
            row = int(center_y / 100)
            
            if 0 <= row < 8 and 0 <= col < 8:
                board_array[row, col] = piece['piece_symbol']
        
        return board_array
    
    def _map_with_perspective(
        self,
        pieces: List[Dict],
        board_corners: np.ndarray
    ) -> np.ndarray:
        """
        Perspective-corrected piece mapping.
        
        Args:
            pieces: List of detected pieces
            board_corners: Board corner coordinates
            
        Returns:
            8x8 board array
        """
        board_array = np.full((8, 8), '.', dtype=object)
        
        # Calculate perspective transform
        # This would require more complex geometric calculations
        # For now, use simplified approach
        
        for piece in pieces:
            center_x, center_y = piece['center']
            
            # Map to board coordinates using perspective correction
            # This is a placeholder - real implementation would use
            # proper perspective transformation
            col = int(center_x / 100)
            row = int(center_y / 100)
            
            if 0 <= row < 8 and 0 <= col < 8:
                board_array[row, col] = piece['piece_symbol']
        
        return board_array
    
    def _validate_and_correct_board(self, board_array: np.ndarray) -> np.ndarray:
        """
        Validate and correct board state.
        
        Args:
            board_array: 8x8 board array
            
        Returns:
            Corrected board array
        """
        corrected_board = board_array.copy()
        
        # Check for duplicate pieces on same square
        for row in range(8):
            for col in range(8):
                if corrected_board[row, col] != '.':
                    # Check if there are multiple pieces on this square
                    # This would require more sophisticated logic
                    pass
        
        # Check for impossible piece counts
        piece_counts = self._count_pieces(corrected_board)
        for piece, count in piece_counts.items():
            if count > self.expected_counts.get(piece, 0):
                self.logger.log_warning(f"Too many {piece} pieces detected: {count}", "BoardPredictor")
        
        return corrected_board
    
    def _count_pieces(self, board_array: np.ndarray) -> Dict[str, int]:
        """
        Count pieces on board.
        
        Args:
            board_array: 8x8 board array
            
        Returns:
            Dictionary with piece counts
        """
        counts = {}
        for row in range(8):
            for col in range(8):
                piece = board_array[row, col]
                if piece != '.':
                    counts[piece] = counts.get(piece, 0) + 1
        
        return counts
    
    def _board_array_to_fen(self, board_array: np.ndarray) -> str:
        """
        Convert board array to FEN string.
        
        Args:
            board_array: 8x8 board array
            
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
        
        # Add basic FEN components
        fen += " w - - 0 1"
        
        return fen
    
    def _calculate_board_confidence(self, pieces: List[Dict]) -> float:
        """
        Calculate overall board confidence.
        
        Args:
            pieces: List of detected pieces
            
        Returns:
            Average confidence score
        """
        if not pieces:
            return 0.0
        
        confidences = [piece['confidence'] for piece in pieces]
        return np.mean(confidences)
    
    def _create_empty_board(self) -> Dict:
        """
        Create empty board state.
        
        Returns:
            Empty board dictionary
        """
        return {
            'board_array': np.full((8, 8), '.', dtype=object),
            'fen': '8/8/8/8/8/8/8/8 w - - 0 1',
            'pieces_detected': 0,
            'confidence': 0.0
        }
    
    def compare_boards(
        self,
        board1: np.ndarray,
        board2: np.ndarray
    ) -> Dict:
        """
        Compare two board states.
        
        Args:
            board1: First board array
            board2: Second board array
            
        Returns:
            Comparison results
        """
        differences = []
        
        for row in range(8):
            for col in range(8):
                piece1 = board1[row, col]
                piece2 = board2[row, col]
                
                if piece1 != piece2:
                    differences.append({
                        'square': (row, col),
                        'from': piece1,
                        'to': piece2
                    })
        
        return {
            'differences': differences,
            'num_differences': len(differences),
            'is_same': len(differences) == 0
        }
    
    def detect_moves(
        self,
        previous_board: np.ndarray,
        current_board: np.ndarray
    ) -> List[Dict]:
        """
        Detect moves between board states.
        
        Args:
            previous_board: Previous board state
            current_board: Current board state
            
        Returns:
            List of detected moves
        """
        comparison = self.compare_boards(previous_board, current_board)
        moves = []
        
        if comparison['num_differences'] == 0:
            return moves
        
        # Simple move detection
        # This would require more sophisticated logic for real implementation
        for diff in comparison['differences']:
            square = diff['square']
            from_piece = diff['from']
            to_piece = diff['to']
            
            if from_piece != '.' and to_piece == '.':
                # Piece was removed
                moves.append({
                    'type': 'capture',
                    'from': square,
                    'to': None,
                    'piece': from_piece
                })
            elif from_piece == '.' and to_piece != '.':
                # Piece was added
                moves.append({
                    'type': 'place',
                    'from': None,
                    'to': square,
                    'piece': to_piece
                })
            elif from_piece != '.' and to_piece != '.':
                # Piece moved
                moves.append({
                    'type': 'move',
                    'from': square,
                    'to': square,
                    'piece': to_piece
                })
        
        return moves


if __name__ == "__main__":
    # Test board predictor
    predictor = BoardPredictor()
    
    # Create dummy detections
    detections = {
        'boxes': np.array([[100, 100, 200, 200], [300, 300, 400, 400]]),
        'classes': np.array([0, 6]),  # White king, black king
        'confidences': np.array([0.9, 0.8])
    }
    
    # Predict board state
    result = predictor.predict_board_state(detections)
    print(f"Predicted board state: {result['fen']}")
    print(f"Confidence: {result['confidence']:.3f}")
