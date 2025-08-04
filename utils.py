import chess
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import streamlit as st

def save_game_to_pgn(board: chess.Board, game_history: List[Dict], 
                     white_player: str = "Human", black_player: str = "Chess Bot",
                     result: str = "*") -> str:
    """
    Save a game to PGN format

    Args:
        board: Final board position
        game_history: List of moves with metadata
        white_player: Name of white player
        black_player: Name of black player
        result: Game result (1-0, 0-1, 1/2-1/2, *)

    Returns:
        PGN string
    """
    pgn_lines = []

    # PGN headers
    pgn_lines.append(f'[Event "Chess Bot Game"]')
    pgn_lines.append(f'[Site "Streamlit App"]')
    pgn_lines.append(f'[Date "{datetime.now().strftime("%Y.%m.%d")}"]')
    pgn_lines.append(f'[Round "1"]')
    pgn_lines.append(f'[White "{white_player}"]')
    pgn_lines.append(f'[Black "{black_player}"]')
    pgn_lines.append(f'[Result "{result}"]')
    pgn_lines.append('')

    # Move text
    move_text = ""
    for i, move_data in enumerate(game_history):
        if i % 2 == 0:  # White move
            move_num = (i // 2) + 1
            move_text += f"{move_num}. {move_data['san']} "
        else:  # Black move
            move_text += f"{move_data['san']} "

        # Add line breaks every 8 moves for readability
        if (i + 1) % 16 == 0:
            move_text += "\n"

    move_text += result
    pgn_lines.append(move_text)

    return "\n".join(pgn_lines)

def load_config() -> Dict:
    """Load configuration from config.json"""
    default_config = {
        "default_difficulty": 4,
        "max_thinking_time": 10.0,
        "enable_opening_book": True,
        "show_thinking_info": True,
        "auto_save_games": True,
        "piece_theme": "default",
        "board_theme": "brown"
    }

    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                # Merge with defaults for missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            return default_config
    except:
        return default_config

def save_config(config: Dict):
    """Save configuration to config.json"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except:
        return False

def format_time(seconds: float) -> str:
    """Format time in seconds to human readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.1f}s"

def get_piece_unicode(piece: chess.Piece) -> str:
    """Get Unicode symbol for a chess piece"""
    symbols = {
        (chess.PAWN, chess.WHITE): '♙',
        (chess.KNIGHT, chess.WHITE): '♘',
        (chess.BISHOP, chess.WHITE): '♗',
        (chess.ROOK, chess.WHITE): '♖',
        (chess.QUEEN, chess.WHITE): '♕',
        (chess.KING, chess.WHITE): '♔',
        (chess.PAWN, chess.BLACK): '♟',
        (chess.KNIGHT, chess.BLACK): '♞',
        (chess.BISHOP, chess.BLACK): '♝',
        (chess.ROOK, chess.BLACK): '♜',
        (chess.QUEEN, chess.BLACK): '♛',
        (chess.KING, chess.BLACK): '♚',
    }
    return symbols.get((piece.piece_type, piece.color), '?')

def analyze_game_statistics(game_history: List[Dict]) -> Dict:
    """Analyze game statistics from move history"""
    if not game_history:
        return {}

    stats = {
        'total_moves': len(game_history),
        'white_moves': len([m for i, m in enumerate(game_history) if i % 2 == 0]),
        'black_moves': len([m for i, m in enumerate(game_history) if i % 2 == 1]),
        'average_thinking_time': 0,
        'longest_think': 0,
        'captures': 0,
        'checks': 0,
        'bot_moves': len([m for m in game_history if m.get('is_bot', False)])
    }

    thinking_times = [m.get('thinking_time', 0) for m in game_history if m.get('thinking_time', 0) > 0]
    if thinking_times:
        stats['average_thinking_time'] = sum(thinking_times) / len(thinking_times)
        stats['longest_think'] = max(thinking_times)

    return stats

def validate_fen(fen: str) -> bool:
    """Validate FEN string"""
    try:
        chess.Board(fen)
        return True
    except:
        return False

def square_name_to_index(square_name: str) -> Optional[int]:
    """Convert square name (e.g., 'e4') to square index"""
    try:
        return chess.parse_square(square_name)
    except:
        return None

def index_to_square_name(square_index: int) -> str:
    """Convert square index to square name"""
    return chess.square_name(square_index)

def get_board_evaluation_color(evaluation: float) -> str:
    """Get color code for evaluation display"""
    if evaluation > 1.0:
        return "green"
    elif evaluation > 0.3:
        return "lightgreen"
    elif evaluation < -1.0:
        return "red"
    elif evaluation < -0.3:
        return "lightcoral"
    else:
        return "gray"

def create_move_tree_visualization(game_history: List[Dict]) -> str:
    """Create a simple text visualization of the move tree"""
    if not game_history:
        return "No moves played yet."

    tree = ""
    for i, move_data in enumerate(game_history):
        indent = "  " * (i % 2)
        move_num = (i // 2) + 1

        if i % 2 == 0:  # White move
            tree += f"{move_num}. {move_data['san']}"
        else:  # Black move
            tree += f" {move_data['san']}\n"

        if move_data.get('is_bot'):
            tree += f" (Bot: {move_data.get('thinking_time', 0):.1f}s)"

    return tree

def export_position_as_image(board: chess.Board, filename: str = None) -> str:
    """Export current position as SVG (for display in Streamlit)"""
    if filename is None:
        filename = f"position_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg"

    svg_data = chess.svg.board(
        board=board,
        size=400,
        coordinates=True,
        lastmove=board.peek() if board.move_stack else None
    )

    return svg_data

def get_difficulty_description(depth: int) -> Tuple[str, str]:
    """Get difficulty name and description based on search depth"""
    descriptions = {
        3: ("Beginner", "Quick moves, basic evaluation"),
        4: ("Intermediate", "Balanced play, good for learning"),
        5: ("Advanced", "Strong tactical play"),
        6: ("Expert", "Deep calculation, very strong"),
        7: ("Master", "Professional level play"),
        8: ("Grandmaster", "Extremely strong, slow moves")
    }

    return descriptions.get(depth, ("Custom", f"Depth {depth}"))

def suggest_next_move(board: chess.Board) -> Optional[str]:
    """Suggest a good move for the human player (for hints)"""
    try:
        # Simple move suggestion based on basic principles
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        # Prioritize captures
        captures = [move for move in legal_moves if board.is_capture(move)]
        if captures:
            return captures[0].uci()

        # Prioritize checks
        for move in legal_moves:
            board.push(move)
            if board.is_check():
                board.pop()
                return move.uci()
            board.pop()

        # Return a random legal move
        import random
        return random.choice(legal_moves).uci()

    except:
        return None

# Streamlit utility functions
def display_thinking_animation():
    """Display a thinking animation"""
    placeholder = st.empty()
    for i in range(3):
        placeholder.text(f"Bot is thinking{'.' * ((i % 3) + 1)}")
        time.sleep(0.5)
    placeholder.empty()

def create_game_summary(board: chess.Board, game_history: List[Dict]) -> Dict:
    """Create a comprehensive game summary"""
    summary = {
        'final_position': board.fen(),
        'total_moves': len(game_history),
        'game_length': len(game_history) // 2,
        'result': board.result(),
        'is_checkmate': board.is_checkmate(),
        'is_stalemate': board.is_stalemate(),
        'is_draw': board.is_draw(),
        'timestamp': datetime.now().isoformat()
    }

    if game_history:
        summary['first_move'] = game_history[0]['san']
        summary['last_move'] = game_history[-1]['san']

        # Calculate average thinking time for bot moves
        bot_times = [m.get('thinking_time', 0) for m in game_history if m.get('is_bot')]
        if bot_times:
            summary['average_bot_thinking_time'] = sum(bot_times) / len(bot_times)

    return summary

# Testing utilities
def run_engine_performance_test():
    """Run a performance test on the chess engine"""
    from chess_engine import ChessEngine
    import time

    engine = ChessEngine()
    board = chess.Board()

    print("Running engine performance test...")

    depths_to_test = [3, 4, 5]
    results = {}

    for depth in depths_to_test:
        start_time = time.time()
        move = engine.get_best_move(board, depth=depth)
        elapsed_time = time.time() - start_time

        engine_info = engine.get_engine_info()

        results[depth] = {
            'time': elapsed_time,
            'nodes': engine_info['nodes_evaluated'],
            'nps': engine_info['nodes_evaluated'] / elapsed_time if elapsed_time > 0 else 0,
            'move': move.uci() if move else None
        }

        print(f"Depth {depth}: {elapsed_time:.2f}s, {engine_info['nodes_evaluated']} nodes, "
              f"{results[depth]['nps']:.0f} NPS, move: {move.uci() if move else 'None'}")

    return results

if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...")

    # Test config loading/saving
    config = load_config()
    print(f"Default config loaded: {config}")

    # Test FEN validation
    valid_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    invalid_fen = "invalid_fen_string"

    print(f"Valid FEN test: {validate_fen(valid_fen)}")
    print(f"Invalid FEN test: {validate_fen(invalid_fen)}")

    # Test square conversion
    print(f"e4 to index: {square_name_to_index('e4')}")
    print(f"Index 28 to name: {index_to_square_name(28)}")

    print("Utility functions test completed!")
