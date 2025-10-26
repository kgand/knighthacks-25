"""Chess-related utility functions."""

import chess
import chess.svg
import numpy as np
from typing import Tuple


def fen_to_board(fen: str) -> chess.Board:
    """Convert FEN string to Board object."""
    return chess.Board(fen)


def board_to_fen(board: chess.Board) -> str:
    """Convert Board to FEN string."""
    return board.fen()


def render_board(
    board: chess.Board,
    size: int = 400,
    colors: Tuple = None
) -> str:
    """
    Render board as SVG.
    
    Args:
        board: Board to render
        size: Image size in pixels
        colors: (light_square, dark_square) colors
        
    Returns:
        SVG string
    """
    if colors is None:
        colors = {
            'square light': '#f0d9b5',
            'square dark': '#b58863'
        }
    else:
        colors = {
            'square light': colors[0],
            'square dark': colors[1]
        }
    
    return chess.svg.board(board=board, size=size, colors=colors)


def square_to_coords(square: chess.Square) -> Tuple[int, int]:
    """Convert chess square to (rank, file) coordinates."""
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    return (rank, file)


def coords_to_square(rank: int, file: int) -> chess.Square:
    """Convert (rank, file) to chess square."""
    return chess.square(file, rank)
