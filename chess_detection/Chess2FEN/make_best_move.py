import argparse
import chess
import chess.engine
import sys
from pathlib import Path

def best_move_from_fen(fen: str, elo: int, engine_path: str, movetime_ms: int = 1500):
    # Load board
    board = chess.Board(fen)

    # Launch engine with Elo limit
    # UCI_LimitStrength=True tells the engine to target the given Elo (UCI_Elo)
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    engine.configure({
        "UCI_LimitStrength": True,
        "UCI_Elo": elo
    })

    try:
        # Think for a fixed time; you can also use depth=N instead of time
        result = engine.play(board, chess.engine.Limit(time=movetime_ms / 1000.0))
        move = result.move

        # Also get a quick evaluation at the configured strength (optional)
        info = engine.analyse(board, chess.engine.Limit(time=movetime_ms / 1000.0))
        score = info.get("score")

        # Present move in UCI and SAN
        san = board.san(move)
        return {
            "uci": move.uci(),
            "san": san,
            "score": str(score) if score is not None else None
        }
    finally:
        engine.quit()

def main():
    p = argparse.ArgumentParser(description="Get best move from FEN at a target Elo using Stockfish.")
    p.add_argument("--fen", required=True, help="FEN string")
    p.add_argument("--elo", required=True, type=int, help="Target Elo (e.g., 1200…2800)")
    p.add_argument("--engine", required=True, help="Path to Stockfish binary (e.g., stockfish.exe)")
    p.add_argument("--movetime", type=int, default=1500, help="Thinking time in ms (default: 1500)")
    args = p.parse_args()

    engine_path = Path(args.engine)
    if not engine_path.exists():
        print(f"Engine not found at: {engine_path}", file=sys.stderr)
        sys.exit(2)

    out = best_move_from_fen(args.fen, args.elo, str(engine_path), args.movetime)
    print(f"Best move (UCI): {out['uci']}")
    print(f"Best move (SAN): {out['san']}")
    if out["score"] is not None:
        print(f"Score: {out['score']}")

if __name__ == "__main__":
    main()
