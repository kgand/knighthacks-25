"""
Chess move validation and analysis.

Validates detected moves against chess rules and provides
move analysis and suggestions.
"""

import chess
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from utils.chess_logic import ChessBoard, validate_fen, get_piece_color
from utils.logger import get_global_logger


class MoveValidator:
    """
    Validates chess moves and analyzes board positions.
    
    Provides move validation, position analysis, and
    move suggestion functionality.
    """
    
    def __init__(self):
        """Initialize move validator."""
        self.logger = get_global_logger()
        self.board = ChessBoard()
        
        # Move validation parameters
        self.max_move_distance = 2  # Maximum squares a piece can move
        self.min_confidence = 0.7   # Minimum confidence for move validation
    
    def validate_move(
        self,
        move_uci: str,
        board_fen: str,
        confidence: float = 1.0
    ) -> Dict:
        """
        Validate a chess move.
        
        Args:
            move_uci: Move in UCI format (e.g., 'e2e4')
            board_fen: Current board FEN
            confidence: Move confidence score
            
        Returns:
            Validation results
        """
        try:
            # Load board state
            self.board = ChessBoard(board_fen)
            
            # Check if move is legal
            is_legal = self.board.is_valid_move(move_uci)
            
            if not is_legal:
                return {
                    'valid': False,
                    'reason': 'Illegal move',
                    'suggestions': self._get_move_suggestions()
                }
            
            # Check move confidence
            if confidence < self.min_confidence:
                return {
                    'valid': False,
                    'reason': f'Low confidence: {confidence:.3f}',
                    'suggestions': self._get_move_suggestions()
                }
            
            # Check for special conditions
            special_conditions = self._check_special_conditions(move_uci)
            
            return {
                'valid': True,
                'move': move_uci,
                'confidence': confidence,
                'special_conditions': special_conditions,
                'board_after': self._get_board_after_move(move_uci)
            }
            
        except Exception as e:
            self.logger.log_error(e, "MoveValidation")
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}',
                'suggestions': []
            }
    
    def _check_special_conditions(self, move_uci: str) -> Dict:
        """
        Check for special move conditions.
        
        Args:
            move_uci: Move in UCI format
            
        Returns:
            Dictionary with special conditions
        """
        conditions = {
            'is_castling': False,
            'is_en_passant': False,
            'is_promotion': False,
            'is_capture': False,
            'is_check': False,
            'is_checkmate': False
        }
        
        try:
            move = chess.Move.from_uci(move_uci)
            
            # Check for castling
            if self.board.is_castling(move):
                conditions['is_castling'] = True
            
            # Check for en passant
            if self.board.is_en_passant(move):
                conditions['is_en_passant'] = True
            
            # Check for promotion
            if move.promotion:
                conditions['is_promotion'] = True
            
            # Check for capture
            if self.board.is_capture(move):
                conditions['is_capture'] = True
            
            # Make move and check for check/checkmate
            self.board.push(move)
            if self.board.is_check():
                conditions['is_check'] = True
            if self.board.is_checkmate():
                conditions['is_checkmate'] = True
            self.board.pop()
            
        except Exception as e:
            self.logger.log_warning(f"Error checking special conditions: {e}", "MoveValidator")
        
        return conditions
    
    def _get_board_after_move(self, move_uci: str) -> str:
        """
        Get board state after move.
        
        Args:
            move_uci: Move in UCI format
            
        Returns:
            FEN string after move
        """
        try:
            move = chess.Move.from_uci(move_uci)
            self.board.push(move)
            fen = self.board.fen()
            self.board.pop()
            return fen
        except Exception:
            return self.board.fen()
    
    def _get_move_suggestions(self) -> List[str]:
        """
        Get legal move suggestions.
        
        Returns:
            List of legal moves in UCI format
        """
        legal_moves = list(self.board.legal_moves)
        return [move.uci() for move in legal_moves[:10]]  # Return first 10 moves
    
    def analyze_position(self, board_fen: str) -> Dict:
        """
        Analyze current board position.
        
        Args:
            board_fen: Board FEN string
            
        Returns:
            Position analysis
        """
        try:
            self.board = ChessBoard(board_fen)
            
            analysis = {
                'is_check': self.board.is_check(),
                'is_checkmate': self.board.is_checkmate(),
                'is_stalemate': self.board.is_stalemate(),
                'is_game_over': self.board.is_game_over(),
                'legal_moves': len(list(self.board.legal_moves)),
                'material_balance': self._calculate_material_balance(),
                'position_evaluation': self._evaluate_position()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.log_error(e, "PositionAnalysis")
            return {
                'error': str(e),
                'is_game_over': False,
                'legal_moves': 0
            }
    
    def _calculate_material_balance(self) -> int:
        """
        Calculate material balance.
        
        Returns:
            Material balance (positive = white advantage)
        """
        piece_values = {
            'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0,
            'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': 0
        }
        
        balance = 0
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                balance += piece_values.get(piece.symbol(), 0)
        
        return balance
    
    def _evaluate_position(self) -> str:
        """
        Evaluate position strength.
        
        Returns:
            Position evaluation string
        """
        material_balance = self._calculate_material_balance()
        
        if material_balance > 3:
            return "White has significant advantage"
        elif material_balance > 1:
            return "White has slight advantage"
        elif material_balance < -3:
            return "Black has significant advantage"
        elif material_balance < -1:
            return "Black has slight advantage"
        else:
            return "Position is roughly equal"
    
    def detect_move_from_boards(
        self,
        previous_board: np.ndarray,
        current_board: np.ndarray
    ) -> Optional[str]:
        """
        Detect move from board state changes.
        
        Args:
            previous_board: Previous board array
            current_board: Current board array
            
        Returns:
            Detected move in UCI format or None
        """
        # Find differences between boards
        differences = []
        
        for row in range(8):
            for col in range(8):
                prev_piece = previous_board[row, col]
                curr_piece = current_board[row, col]
                
                if prev_piece != curr_piece:
                    differences.append({
                        'square': (row, col),
                        'from': prev_piece,
                        'to': curr_piece
                    })
        
        if len(differences) == 0:
            return None
        
        # Simple move detection logic
        # This would require more sophisticated analysis
        if len(differences) == 2:
            # Likely a move
            from_square = None
            to_square = None
            
            for diff in differences:
                if diff['from'] != '.' and diff['to'] == '.':
                    from_square = self._coords_to_square(diff['square'])
                elif diff['from'] == '.' and diff['to'] != '.':
                    to_square = self._coords_to_square(diff['square'])
            
            if from_square and to_square:
                return f"{from_square}{to_square}"
        
        return None
    
    def _coords_to_square(self, coords: Tuple[int, int]) -> str:
        """
        Convert coordinates to square notation.
        
        Args:
            coords: (row, col) coordinates
            
        Returns:
            Square notation (e.g., 'e4')
        """
        row, col = coords
        square_index = (7 - row) * 8 + col
        return chess.square_name(square_index)
    
    def get_best_moves(self, board_fen: str, depth: int = 3) -> List[Dict]:
        """
        Get best moves for current position.
        
        Args:
            board_fen: Board FEN string
            depth: Search depth
            
        Returns:
            List of best moves with evaluations
        """
        try:
            self.board = ChessBoard(board_fen)
            legal_moves = list(self.board.legal_moves)
            
            # Simple evaluation (would use engine in real implementation)
            best_moves = []
            
            for move in legal_moves[:10]:  # Limit to first 10 moves
                # Make move
                self.board.push(move)
                
                # Evaluate position
                evaluation = self._evaluate_position()
                
                # Undo move
                self.board.pop()
                
                best_moves.append({
                    'move': move.uci(),
                    'evaluation': evaluation,
                    'is_capture': self.board.is_capture(move),
                    'is_check': self.board.gives_check(move)
                })
            
            # Sort by evaluation (simplified)
            best_moves.sort(key=lambda x: x['evaluation'], reverse=True)
            
            return best_moves[:5]  # Return top 5 moves
            
        except Exception as e:
            self.logger.log_error(e, "BestMoves")
            return []
    
    def validate_board_state(self, board_fen: str) -> Dict:
        """
        Validate board state for legality.
        
        Args:
            board_fen: Board FEN string
            
        Returns:
            Validation results
        """
        try:
            self.board = ChessBoard(board_fen)
            
            # Check for basic validity
            is_valid = True
            errors = []
            
            # Check for multiple kings
            white_kings = sum(1 for square in chess.SQUARES 
                            if self.board.piece_at(square) == chess.Piece(chess.KING, chess.WHITE))
            black_kings = sum(1 for square in chess.SQUARES 
                            if self.board.piece_at(square) == chess.Piece(chess.KING, chess.BLACK))
            
            if white_kings != 1:
                is_valid = False
                errors.append(f"Invalid number of white kings: {white_kings}")
            
            if black_kings != 1:
                is_valid = False
                errors.append(f"Invalid number of black kings: {black_kings}")
            
            # Check for impossible piece counts
            piece_counts = self._count_pieces()
            for piece, count in piece_counts.items():
                if count > 8:  # Maximum pieces per type
                    is_valid = False
                    errors.append(f"Too many {piece} pieces: {count}")
            
            return {
                'valid': is_valid,
                'errors': errors,
                'board': self.board
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Invalid FEN: {str(e)}"],
                'board': None
            }
    
    def _count_pieces(self) -> Dict[str, int]:
        """
        Count pieces on board.
        
        Returns:
            Dictionary with piece counts
        """
        counts = {}
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                symbol = piece.symbol()
                counts[symbol] = counts.get(symbol, 0) + 1
        
        return counts


if __name__ == "__main__":
    # Test move validator
    validator = MoveValidator()
    
    # Test move validation
    result = validator.validate_move('e2e4', chess.STARTING_FEN)
    print(f"Move validation result: {result}")
    
    # Test position analysis
    analysis = validator.analyze_position(chess.STARTING_FEN)
    print(f"Position analysis: {analysis}")
