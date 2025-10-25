"""This script provides a simple input system for testing chessboard digitization
on a single image.
"""

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

MODEL_PATH_ONNX = "data/models/Xception_last.onnx"
IMG_SIZE_ONNX = 299
PRE_INPUT_ONNX = prein_mobilenet


def main():
    """Predict the FEN for a hardcoded chessboard image."""
    image_path = os.path.join("data", "predictions", "test2.jpg")

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

            # Create and save SVG
            svg_image = chess.svg.board(board=board)
            svg_filename = "chessboard.svg"
            with open(svg_filename, "w") as f:
                f.write(svg_image)
            print(f"\nSVG image of the board saved to {os.path.abspath(svg_filename)}")

        except ValueError:
            print(
                "\nCould not generate a board from the predicted FEN (it might be invalid)."
            )


if __name__ == "__main__":
    main()
