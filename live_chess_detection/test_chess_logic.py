"""
Test suite for chess logic utilities.

Tests the core chess logic functions and board state management.
"""

import pytest
import numpy as np
from utils.chess_logic import (
    ChessBoard, square_to_coords, coords_to_square,
    piece_symbol_to_name, validate_fen, get_piece_color,
    calculate_material_balance
)


class TestChessBoard:
    """Test ChessBoard class functionality."""
    
    def test_initialization(self):
        """Test board initialization."""
        board = ChessBoard()
        assert board.get_fen() == chess.STARTING_FEN
    
    def test_custom_fen(self):
        """Test board with custom FEN."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        board = ChessBoard(fen)
        assert board.get_fen() == fen
    
    def test_piece_at_square(self):
        """Test getting piece at square."""
        board = ChessBoard()
        
        # Test white pieces
        assert board.get_piece_at('e1') is not None  # White king
        assert board.get_piece_at('e8') is not None  # Black king
        assert board.get_piece_at('e4') is None      # Empty square
    
    def test_valid_move(self):
        """Test move validation."""
        board = ChessBoard()
        
        # Valid moves
        assert board.is_valid_move('e2e4')  # Pawn move
        assert board.is_valid_move('g1f3')  # Knight move
        
        # Invalid moves
        assert not board.is_valid_move('e2e5')  # Invalid pawn move
        assert not board.is_valid_move('e1e2')  # King move (blocked)
    
    def test_make_move(self):
        """Test making moves."""
        board = ChessBoard()
        
        # Make a valid move
        assert board.make_move('e2e4')
        assert board.get_piece_at('e4') is not None
        
        # Try invalid move
        assert not board.make_move('e2e5')
    
    def test_board_array(self):
        """Test board array conversion."""
        board = ChessBoard()
        board_array = board.get_board_array()
        
        assert board_array.shape == (8, 8)
        assert board_array[0, 4] == 'k'  # Black king
        assert board_array[7, 4] == 'K'  # White king
    
    def test_game_over(self):
        """Test game over detection."""
        board = ChessBoard()
        assert not board.is_game_over()
    
    def test_move_history(self):
        """Test move history tracking."""
        board = ChessBoard()
        board.make_move('e2e4')
        assert len(board.move_history) == 1
        assert board.move_history[0] == 'e2e4'


class TestChessUtilities:
    """Test chess utility functions."""
    
    def test_square_to_coords(self):
        """Test square to coordinates conversion."""
        assert square_to_coords('e4') == (4, 4)
        assert square_to_coords('a1') == (7, 0)
        assert square_to_coords('h8') == (0, 7)
    
    def test_coords_to_square(self):
        """Test coordinates to square conversion."""
        assert coords_to_square(4, 4) == 'e4'
        assert coords_to_square(7, 0) == 'a1'
        assert coords_to_square(0, 7) == 'h8'
    
    def test_piece_symbol_to_name(self):
        """Test piece symbol to name conversion."""
        assert piece_symbol_to_name('K') == 'white king'
        assert piece_symbol_to_name('q') == 'black queen'
        assert piece_symbol_to_name('P') == 'white pawn'
    
    def test_validate_fen(self):
        """Test FEN validation."""
        assert validate_fen(chess.STARTING_FEN)
        assert not validate_fen("invalid fen")
    
    def test_get_piece_color(self):
        """Test piece color detection."""
        assert get_piece_color('K') == 'white'
        assert get_piece_color('q') == 'black'
        assert get_piece_color('.') is None
    
    def test_calculate_material_balance(self):
        """Test material balance calculation."""
        board = ChessBoard()
        balance = calculate_material_balance(board)
        assert balance == 0  # Equal material in starting position


if __name__ == "__main__":
    pytest.main([__file__])
