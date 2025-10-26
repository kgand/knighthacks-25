"""Board state prediction from detected pieces."""

import numpy as np
import chess
from typing import Dict, List, Tuple


class BoardStatePredictor:
    """
    Predicts chess board state from piece detections.
    
    Maps detected pieces to squares and validates against chess rules.
    Uses probability-based move detection algorithm.
    """
    
    def __init__(self):
        self.board = chess.Board()
        self.piece_history = []  # Track piece positions over time
    
    def calculate_board_loss(
        self,
        piece_probabilities: Dict,
        board_state: np.ndarray
    ) -> float:
        """
        Calculate loss for a proposed board configuration.
        
        Lower loss = more likely configuration based on detected pieces.
        Formula: sum of -log(probability) for each square.
        
        Reference: Based on our YouTube dataset extraction algorithm.
        """
        loss = 0.0
        epsilon = 1e-8  # Avoid log(0)
        
        for rank in range(8):
            for file in range(8):
                piece_symbol = board_state[rank, file]
                square_probs = piece_probabilities.get((rank, file), {})
                prob = square_probs.get(piece_symbol, epsilon)
                loss -= np.log(prob + epsilon)
        
        return loss
    
    def find_best_legal_move(
        self,
        current_board: chess.Board,
        piece_probabilities: Dict,
        detected_board: np.ndarray
    ) -> Tuple[chess.Move, float]:
        """
        Find most likely legal move given detections.
        
        Tests all legal moves and finds one that best matches detections.
        Returns None if no move detected (position unchanged).
        """
        # Check if board state changed
        current_loss = self.calculate_board_loss(
            piece_probabilities,
            self.board_to_array(current_board)
        )
        
        best_move = None
        best_loss = current_loss
        
        # Try each legal move
        for move in current_board.legal_moves:
            test_board = current_board.copy()
            test_board.push(move)
            
            move_loss = self.calculate_board_loss(
                piece_probabilities,
                self.board_to_array(test_board)
            )
            
            if move_loss < best_loss:
                best_loss = move_loss
                best_move = move
        
        return best_move, best_loss
    
    def board_to_array(self, board: chess.Board) -> np.ndarray:
        """Convert chess.Board to numpy array."""
        arr = np.full((8, 8), '0', dtype=object)
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                arr[7 - rank, file] = piece.symbol()
        
        return arr
