# "This script provides a simple input system for testing chessboard digitization
# on a single image.
# "

# `sklearn` is required for Jetson (to avoid "cannot allocate memory in
# static TLS block" error)
import sklearn
import os
import chess
import chess.svg
from keras.applications.mobilenet_v2 import (
    preprocess_input as prein_mobilenet,
)
from lc2fen.predict_board import predict_board_onnx
from make_best_move import best_move_from_fen

MODEL_PATH_ONNX = "data/models/Xception_last.onnx"
IMG_SIZE_ONNX = 299
PRE_INPUT_ONNX = prein_mobilenet


def main():
    """Predict the FEN for a hardcoded chessboard image and find the best move."""
    image_path = input("Enter path") #os.path.join("data", "predictions", "test2.jpg")

    if not os.path.exists(image_path):
        print(f"\nError: Image not found at path: {image_path}")
        return

    a1_pos = "BL"
    previous_fen = None

    print(f"\nProcessing {image_path} with a1_pos='{a1_pos}'...")
    fen, _ = predict_board_onnx(
        MODEL_PATH_ONNX,
        IMG_SIZE_ONNX,
        PRE_INPUT_ONNX,
        path=image_path,
        a1_pos=a1_pos,
        previous_fen=previous_fen,
    )

    print("\nPredicted FEN:", fen)

    if fen:
        try:
            board = chess.Board(None)  # Create an empty board
            board.set_board_fen(fen)
            print("\nDigital Chessboard:")
            print(board)

            svg_filename = "chessboard_detected_out.svg"
            svg_image = chess.svg.board(board=board)
            with open(svg_filename, "w") as f:
                f.write(svg_image)
            print(f"\nSVG image saved to {os.path.abspath(svg_filename)}")

            # --- Find best move and generate SVG ---
            engine_path = "stockfish_PC/stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2.exe"
            elo = 1500

            svg_filename = "chessboard_out.svg"

            if not os.path.exists(engine_path):
                print(f"\nChess engine not found at '{engine_path}'.")
                print(
                    "Please ensure the Stockfish executable is at the correct path."
                )
                # Generate SVG without the best move
                svg_image = chess.svg.board(board=board)
            else:
                print(f"\nFinding best move with {engine_path} at Elo {elo}...")
                full_fen = board.fen()
                best_move = best_move_from_fen(full_fen, elo, engine_path)
                print(f"Best move found: {best_move['san']} ({best_move['uci']})")

                # Create arrow for SVG
                move_uci = best_move['uci']
                tail_square = chess.SQUARE_NAMES.index(move_uci[:2])
                head_square = chess.SQUARE_NAMES.index(move_uci[2:])
                arrow = chess.svg.Arrow(tail_square, head_square, color="green")

                svg_image = chess.svg.board(board=board, arrows=[arrow])

            with open(svg_filename, "w") as f:
                f.write(svg_image)
            print(f"\nSVG image saved to {os.path.abspath(svg_filename)}")

        except ValueError:
            print(
                "\nCould not generate a board from the predicted FEN (it might be invalid)."
            )
        except Exception as e:
            print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()
