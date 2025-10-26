"""Chess move validation logic."""

import chess
from typing import Optional


class ChessMoveValidator:
    """
    Validates detected moves against chess rules.
    
    Prevents illegal moves and handles special cases
    (castling, en passant, promotion).
    """
    
    def __init__(self):
        self.board = chess.Board()
        self.move_history = []
    
    def is_legal_move(self, move: chess.Move) -> bool:
        """Check if move is legal in current position."""
        return move in self.board.legal_moves
    
    def apply_move(self, move: chess.Move) -> bool:
        """
        Apply move if legal.
        
        Returns:
            True if move applied, False otherwise
        """
        if self.is_legal_move(move):
            self.board.push(move)
            self.move_history.append(move)
            return True
        return False
    
    def undo_last_move(self) -> Optional[chess.Move]:
        """Undo last move. Returns undone move or None."""
        if len(self.move_history) > 0:
            self.board.pop()
            return self.move_history.pop()
        return None
    
    def get_fen(self) -> str:
        """Get current position in FEN notation."""
        return self.board.fen()
    
    def reset(self):
        """Reset board to starting position."""
        self.board = chess.Board()
        self.move_history = []
