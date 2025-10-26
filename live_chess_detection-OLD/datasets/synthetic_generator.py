"""
Synthetic chess position generator using Chess.com API.

Generates training images by rendering chess positions from real games
with various board styles and piece sets. This provides clean ground truth
labels for initial model training.
"""

import io
import json
import os
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

import chess
import chess.pgn
import chess.svg
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter
from tqdm import tqdm


@dataclass
class BoardTheme:
    """Visual theme for chess board rendering."""
    light_square: Tuple[int, int, int]
    dark_square: Tuple[int, int, int]
    name: str


@dataclass
class GameMetadata:
    """Metadata for a chess game from Chess.com."""
    white_player: str
    black_player: str
    pgn_text: str
    event: str


class ChessPositionGenerator:
    """
    Generates synthetic chess position images from PGN games.
    
    Uses multiple board themes and piece styles to create variety.
    Applies random augmentations to simulate real-world conditions.
    """
    
    # Color schemes based on popular chess sites
    # Format: (light_R, light_G, light_B, dark_R, dark_G, dark_B)
    BOARD_THEMES = [
        BoardTheme((240, 217, 181), (181, 136, 99), "classic"),
        BoardTheme((238, 238, 210), (118, 150, 86), "green"),
        BoardTheme((222, 227, 230), (140, 162, 173), "blue"),
        BoardTheme((255, 228, 196), (139, 69, 19), "tan"),
        BoardTheme((245, 245, 245), (50, 50, 50), "contrast"),
        BoardTheme((235, 209, 166), (165, 117, 81), "wood"),
    ]
    
    def __init__(
        self,
        output_dir: str,
        img_dimensions: int = 512,
        piece_directories: Optional[List[str]] = None
    ):
        """
        Initialize the generator.
        
        Args:
            output_dir: Where to save generated images
            img_dimensions: Size of output images (square)
            piece_directories: Paths to piece image sets
        """
        self.output_path = Path(output_dir)
        self.img_size = img_dimensions
        self.square_dim = img_dimensions // 8
        
        # Set up piece image paths
        # Default to multiple styles if not specified
        if piece_directories is None:
            base_path = Path("data/piece_images")
            piece_directories = [
                str(base_path / "chesscom"),
                str(base_path / "wikipedia"),
            ]
        
        self.piece_styles = piece_directories
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create output directory structure."""
        splits = ["train", "validation", "test"]
        for split in splits:
            split_path = self.output_path / split
            (split_path / "images").mkdir(parents=True, exist_ok=True)
            (split_path / "labels").mkdir(parents=True, exist_ok=True)
    
    def render_position(
        self,
        board: chess.Board,
        theme: Optional[BoardTheme] = None,
        piece_style: Optional[str] = None,
        perspective: str = "white"
    ) -> Image.Image:
        """
        Render a chess position as an image.
        
        Args:
            board: Current board position
            theme: Color scheme (random if None)
            piece_style: Path to pieces (random if None)
            perspective: "white" or "black" view
            
        Returns:
            PIL Image of the board position
        """
        # Select random theme/style if not specified
        if theme is None:
            theme = random.choice(self.BOARD_THEMES)
        if piece_style is None:
            piece_style = random.choice(self.piece_styles)
        
        # Create blank canvas
        canvas = Image.new("RGB", (self.img_size, self.img_size), "white")
        draw_context = ImageDraw.Draw(canvas)
        
        # Draw board squares
        for rank in range(8):
            for file in range(8):
                # Calculate square position
                x_pos = file * self.square_dim
                y_pos = rank * self.square_dim
                x_end = x_pos + self.square_dim
                y_end = y_pos + self.square_dim
                
                # Determine color (alternating pattern)
                is_light = (rank + file) % 2 == 0
                color = theme.light_square if is_light else theme.dark_square
                
                # Draw square
                draw_context.rectangle([x_pos, y_pos, x_end, y_end], fill=color)
        
        # Get board representation
        board_str = str(board)
        rows = board_str.split('\n')
        
        # Flip board if black perspective
        if perspective == "black":
            rows = rows[::-1]
            rows = [row[::-1].replace(' ', '') for row in rows]
        else:
            rows = [row.replace(' ', '') for row in rows]
        
        # Place pieces on board
        for rank_idx, rank_pieces in enumerate(rows):
            for file_idx, piece_char in enumerate(rank_pieces):
                if piece_char == '.':
                    continue  # Empty square
                
                # Load piece image
                piece_path = Path(piece_style) / f"{piece_char}.png"
                if not piece_path.exists():
                    continue
                
                piece_img = Image.open(piece_path)
                piece_img = piece_img.resize(
                    (self.square_dim, self.square_dim),
                    Image.LANCZOS
                )
                
                # Calculate position
                x = file_idx * self.square_dim
                y = rank_idx * self.square_dim
                
                # Paste with alpha channel if available
                if piece_img.mode == 'RGBA':
                    canvas.paste(piece_img, (x, y), piece_img)
                else:
                    canvas.paste(piece_img, (x, y))
        
        return canvas
    
    def apply_augmentations(self, img: Image.Image) -> Image.Image:
        """
        Apply random augmentations to simulate real conditions.
        
        Includes blur, brightness/contrast adjustments.
        Keeps augmentations subtle to maintain data quality.
        """
        # Random Gaussian blur (simulates camera focus issues)
        # Tested values: 0-3, found 0-2 works best
        blur_amount = random.uniform(0, 2)
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_amount))
        
        # Small brightness variation
        # Helps model handle different lighting
        brightness_factor = random.uniform(0.85, 1.15)
        enhancer = Image.Enhance.Brightness(img)
        img = enhancer.enhance(brightness_factor)
        
        # Contrast adjustment
        contrast_factor = random.uniform(0.9, 1.1)
        enhancer = Image.Enhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)
        
        return img
    
    def board_to_array(self, board: chess.Board) -> np.ndarray:
        """
        Convert board to numpy array of piece symbols.
        
        Uses chess library's internal square indexing.
        Returns 8x8 array matching visual layout.
        """
        # Square indices in chess library order
        square_order = [
            56, 57, 58, 59, 60, 61, 62, 63,  # Rank 8
            48, 49, 50, 51, 52, 53, 54, 55,  # Rank 7
            40, 41, 42, 43, 44, 45, 46, 47,
            32, 33, 34, 35, 36, 37, 38, 39,
            24, 25, 26, 27, 28, 29, 30, 31,
            16, 17, 18, 19, 20, 21, 22, 23,
            8, 9, 10, 11, 12, 13, 14, 15,
            0, 1, 2, 3, 4, 5, 6, 7,  # Rank 1
        ]
        
        piece_map = board.piece_map()
        piece_chars = []
        
        for square_idx in square_order:
            piece = piece_map.get(square_idx)
            if piece is None:
                piece_chars.append('0')  # Empty square
            else:
                piece_chars.append(piece.symbol())
        
        return np.array(piece_chars).reshape(8, 8)
    
    def process_game(
        self,
        game_meta: GameMetadata,
        split: str,
        sequence_id: int
    ) -> int:
        """
        Generate images for all positions in a game.
        
        Args:
            game_meta: Game metadata including PGN
            split: train/validation/test
            sequence_id: Starting ID for naming files
            
        Returns:
            Number of images generated
        """
        # Parse PGN
        pgn_io = io.StringIO(game_meta.pgn_text)
        game = chess.pgn.read_game(pgn_io)
        
        if game is None:
            return 0
        
        board = game.board()
        images_created = 0
        
        # Output paths
        img_dir = self.output_path / split / "images"
        label_dir = self.output_path / split / "labels"
        
        # Generate image for starting position
        position_img = self.render_position(board)
        position_img = self.apply_augmentations(position_img)
        
        # Save image
        filename = f"{game_meta.white_player}_{game_meta.black_player}_{sequence_id:04d}"
        img_path = img_dir / f"{filename}.png"
        position_img.save(img_path, "PNG")
        
        # Save label (board state as CSV)
        board_array = self.board_to_array(board)
        label_path = label_dir / f"{filename}.csv"
        np.savetxt(label_path, board_array, delimiter=",", fmt="%s")
        
        images_created += 1
        
        # Process all moves
        for move in game.mainline_moves():
            board.push(move)
            sequence_id += 1
            
            # Render new position
            position_img = self.render_position(board)
            position_img = self.apply_augmentations(position_img)
            
            # Save
            filename = f"{game_meta.white_player}_{game_meta.black_player}_{sequence_id:04d}"
            img_path = img_dir / f"{filename}.png"
            position_img.save(img_path, "PNG")
            
            board_array = self.board_to_array(board)
            label_path = label_dir / f"{filename}.csv"
            np.savetxt(label_path, board_array, delimiter=",", fmt="%s")
            
            images_created += 1
        
        return images_created


class ChessComAPIClient:
    """
    Client for Chess.com public API.
    
    Reference: https://www.chess.com/news/view/published-data-api
    """
    
    BASE_URL = "https://api.chess.com/pub"
    
    # User-agent to identify our application
    HEADERS = {
        "User-Agent": "ChessVisionLive/1.0 (Training data generation)"
    }
    
    @classmethod
    def fetch_tournament_rounds(cls, tournament_url: str) -> List[str]:
        """Get all round URLs from a tournament."""
        response = requests.get(tournament_url, headers=cls.HEADERS)
        
        if response.status_code != 200:
            print(f"Failed to fetch tournament: {response.status_code}")
            return []
        
        data = response.json()
        return data.get("rounds", [])
    
    @classmethod
    def fetch_round_games(cls, round_url: str) -> List[Dict]:
        """Get all games from a tournament round."""
        response = requests.get(round_url, headers=cls.HEADERS)
        
        if response.status_code != 200:
            print(f"Failed to fetch round: {response.status_code}")
            return []
        
        data = response.json()
        
        # Some rounds have groups instead of games directly
        if "groups" in data:
            all_games = []
            for group_url in data["groups"]:
                group_games = cls.fetch_round_games(group_url)
                all_games.extend(group_games)
            return all_games
        
        return data.get("games", [])
    
    @classmethod
    def parse_game_data(cls, game_json: Dict) -> GameMetadata:
        """Extract relevant data from game JSON."""
        return GameMetadata(
            white_player=game_json["white"]["username"],
            black_player=game_json["black"]["username"],
            pgn_text=game_json["pgn"],
            event=game_json.get("tournament", "unknown")
        )


def generate_synthetic_dataset(
    output_dir: str,
    tournament_urls: List[str],
    max_games: int = 500,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15
):
    """
    Main function to generate synthetic dataset.
    
    Downloads games from Chess.com tournaments and renders positions.
    Splits data into train/validation/test sets.
    
    Args:
        output_dir: Where to save dataset
        tournament_urls: List of Chess.com tournament URLs
        max_games: Maximum games to process
        train_ratio: Fraction for training (rest split between val/test)
        val_ratio: Fraction for validation
    """
    print("🎲 Starting synthetic dataset generation")
    print(f"Output directory: {output_dir}")
    
    # Fetch all games from tournaments
    print("\n📥 Downloading games from Chess.com...")
    all_games = []
    
    for tournament_url in tqdm(tournament_urls, desc="Tournaments"):
        rounds = ChessComAPIClient.fetch_tournament_rounds(tournament_url)
        for round_url in rounds:
            games = ChessComAPIClient.fetch_round_games(round_url)
            all_games.extend(games)
    
    print(f"Total games downloaded: {len(all_games)}")
    
    # Filter for standard chess (not Chess960, etc.)
    # Blitz games are good balance of quality and variety
    valid_games = [
        g for g in all_games
        if g.get("rules") == "chess" and g.get("time_class") == "blitz"
    ]
    
    print(f"Valid standard chess games: {len(valid_games)}")
    
    # Sample if we have too many
    if len(valid_games) > max_games:
        valid_games = random.sample(valid_games, max_games)
        print(f"Sampled down to: {max_games} games")
    
    # Split into train/val/test
    random.shuffle(valid_games)
    num_train = int(len(valid_games) * train_ratio)
    num_val = int(len(valid_games) * val_ratio)
    
    train_games = valid_games[:num_train]
    val_games = valid_games[num_train:num_train + num_val]
    test_games = valid_games[num_train + num_val:]
    
    print(f"\nSplit: {len(train_games)} train, {len(val_games)} val, {len(test_games)} test")
    
    # Initialize generator
    generator = ChessPositionGenerator(output_dir)
    
    # Save class mapping
    class_map = {
        "0": 0, "B": 1, "K": 2, "N": 3, "P": 4, "Q": 5, "R": 6,
        "b": 7, "k": 8, "n": 9, "p": 10, "q": 11, "r": 12
    }
    
    map_path = Path(output_dir) / "class_mapping.json"
    with open(map_path, 'w') as f:
        json.dump({
            "class2id": class_map,
            "id2class": {v: k for k, v in class_map.items()}
        }, f, indent=2)
    
    # Process games
    print("\n🎨 Rendering positions...")
    
    def process_split(games, split_name):
        total_images = 0
        seq_id = 0
        
        for game_json in tqdm(games, desc=f"{split_name} split"):
            game_meta = ChessComAPIClient.parse_game_data(game_json)
            num_imgs = generator.process_game(game_meta, split_name, seq_id)
            total_images += num_imgs
            seq_id += num_imgs
        
        return total_images
    
    train_count = process_split(train_games, "train")
    val_count = process_split(val_games, "validation")
    test_count = process_split(test_games, "test")
    
    print(f"\n✅ Generation complete!")
    print(f"   Train: {train_count} images")
    print(f"   Val: {val_count} images")
    print(f"   Test: {test_count} images")
    print(f"   Total: {train_count + val_count + test_count} images")


if __name__ == "__main__":
    # Titled Tuesday tournaments from Chess.com
    # These are weekly events with strong players
    TOURNAMENT_URLS = [
        "https://api.chess.com/pub/tournament/titled-tuesday-blitz-2023-11-07",
        "https://api.chess.com/pub/tournament/titled-tuesday-blitz-2023-11-14",
        "https://api.chess.com/pub/tournament/titled-tuesday-blitz-2023-11-21",
    ]
    
    generate_synthetic_dataset(
        output_dir="data/synthetic",
        tournament_urls=TOURNAMENT_URLS,
        max_games=500,
        train_ratio=0.7,
        val_ratio=0.15
    )
