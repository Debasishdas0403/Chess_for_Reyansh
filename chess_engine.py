import chess
import chess.engine
import random
import time
from typing import Optional, Tuple, Dict, List
from evaluation import PositionEvaluator

class ChessEngine:
    """
    Intelligent Chess Engine using Minimax algorithm with Alpha-Beta pruning
    """

    def __init__(self, use_opening_book: bool = True):
        self.evaluator = PositionEvaluator()
        self.use_opening_book = use_opening_book
        self.transposition_table = {}
        self.nodes_evaluated = 0
        self.max_time = 10.0  # Maximum thinking time in seconds

        # Simple opening book
        self.opening_moves = {
            chess.STARTING_FEN: ["e2e4", "d2d4", "g1f3", "c2c4"],
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1": ["e7e5", "c7c5", "e7e6"],
            "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1": ["d7d5", "g8f6", "c7c5"],
        }

    def get_best_move(self, board: chess.Board, depth: int = 4) -> Optional[chess.Move]:
        """
        Get the best move for the current position using minimax with alpha-beta pruning

        Args:
            board: Current chess board position
            depth: Search depth (higher = stronger but slower)

        Returns:
            Best move found, or None if no moves available
        """
        if board.is_game_over():
            return None

        # Check opening book first
        if self.use_opening_book and board.fen() in self.opening_moves:
            opening_moves_uci = self.opening_moves[board.fen()]
            legal_opening_moves = []

            for move_uci in opening_moves_uci:
                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:
                        legal_opening_moves.append(move)
                except:
                    continue

            if legal_opening_moves:
                return random.choice(legal_opening_moves)

        # Reset counters
        self.nodes_evaluated = 0
        self.transposition_table.clear()

        start_time = time.time()
        best_move = None
        best_value = float('-inf') if board.turn else float('inf')

        # Iterative deepening for better move ordering and time management
        for current_depth in range(1, depth + 1):
            if time.time() - start_time > self.max_time:
                break

            try:
                move, value = self._minimax_root(board, current_depth, start_time)
                if move:  # Only update if we found a move
                    best_move = move
                    best_value = value
            except TimeoutError:
                break

        return best_move

    def _minimax_root(self, board: chess.Board, depth: int, start_time: float) -> Tuple[Optional[chess.Move], float]:
        """
        Root minimax function that returns the best move and its evaluation
        """
        best_move = None
        best_value = float('-inf') if board.turn else float('inf')

        # Get and order moves for better alpha-beta pruning
        moves = self._order_moves(board, list(board.legal_moves))

        alpha = float('-inf')
        beta = float('inf')

        for move in moves:
            if time.time() - start_time > self.max_time:
                raise TimeoutError("Time limit exceeded")

            board.push(move)

            if board.turn:  # Next turn is white (maximizing)
                value = self._minimax(board, depth - 1, alpha, beta, True, start_time)
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, value)
            else:  # Next turn is black (minimizing)
                value = self._minimax(board, depth - 1, alpha, beta, False, start_time)
                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, value)

            board.pop()

            # Alpha-beta pruning at root
            if beta <= alpha:
                break

        return best_move, best_value

    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                maximizing: bool, start_time: float) -> float:
        """
        Minimax algorithm with alpha-beta pruning

        Args:
            board: Current board position
            depth: Remaining search depth
            alpha: Alpha value for alpha-beta pruning
            beta: Beta value for alpha-beta pruning
            maximizing: True if maximizing player (white), False if minimizing (black)
            start_time: Start time for timeout management

        Returns:
            Evaluation score of the position
        """
        # Check timeout
        if time.time() - start_time > self.max_time:
            raise TimeoutError("Time limit exceeded")

        self.nodes_evaluated += 1

        # Check transposition table
        board_hash = hash(board.fen())
        if board_hash in self.transposition_table:
            stored_depth, stored_value = self.transposition_table[board_hash]
            if stored_depth >= depth:
                return stored_value

        # Base cases
        if depth == 0 or board.is_game_over():
            evaluation = self.evaluator.evaluate_position(board)
            self.transposition_table[board_hash] = (depth, evaluation)
            return evaluation

        # Get legal moves and order them for better pruning
        moves = self._order_moves(board, list(board.legal_moves))

        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                if time.time() - start_time > self.max_time:
                    raise TimeoutError("Time limit exceeded")

                board.push(move)
                eval_score = self._minimax(board, depth - 1, alpha, beta, False, start_time)
                board.pop()

                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)

                if beta <= alpha:
                    break  # Alpha-beta pruning

            self.transposition_table[board_hash] = (depth, max_eval)
            return max_eval

        else:
            min_eval = float('inf')
            for move in moves:
                if time.time() - start_time > self.max_time:
                    raise TimeoutError("Time limit exceeded")

                board.push(move)
                eval_score = self._minimax(board, depth - 1, alpha, beta, True, start_time)
                board.pop()

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)

                if beta <= alpha:
                    break  # Alpha-beta pruning

            self.transposition_table[board_hash] = (depth, min_eval)
            return min_eval

    def _order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        """
        Order moves for better alpha-beta pruning efficiency
        Priority: Captures > Checks > Castle > Others
        """
        def move_priority(move):
            score = 0

            # Captures (highest priority)
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                moving_piece = board.piece_at(move.from_square)
                if captured_piece and moving_piece:
                    # MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
                    score += (self.evaluator.piece_values[captured_piece.piece_type] * 10 - 
                             self.evaluator.piece_values[moving_piece.piece_type])

            # Checks
            board.push(move)
            if board.is_check():
                score += 50
            board.pop()

            # Castling
            if board.is_castling(move):
                score += 30

            # Promotions
            if move.promotion:
                score += 100

            # Center control (small bonus)
            center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
            if move.to_square in center_squares:
                score += 10

            return -score  # Negative because we want highest score first

        return sorted(moves, key=move_priority)

    def get_engine_info(self) -> Dict:
        """Get information about the engine's last search"""
        return {
            'nodes_evaluated': self.nodes_evaluated,
            'transposition_entries': len(self.transposition_table)
        }

    def set_time_limit(self, seconds: float):
        """Set maximum thinking time"""
        self.max_time = seconds

    def clear_transposition_table(self):
        """Clear the transposition table"""
        self.transposition_table.clear()

# Example usage and testing
if __name__ == "__main__":
    # Test the engine
    engine = ChessEngine()
    board = chess.Board()

    print("Testing Chess Engine...")
    print(f"Starting position: {board.fen()}")

    # Make a few moves to test
    for move_num in range(5):
        if board.is_game_over():
            break

        print(f"
Move {move_num + 1}:")
        print(f"Turn: {'White' if board.turn else 'Black'}")

        start_time = time.time()
        best_move = engine.get_best_move(board, depth=4)
        search_time = time.time() - start_time

        if best_move:
            board.push(best_move)
            engine_info = engine.get_engine_info()

            print(f"Best move: {best_move.uci()} ({board.san(best_move)})")
            print(f"Search time: {search_time:.2f}s")
            print(f"Nodes evaluated: {engine_info['nodes_evaluated']}")
            print(f"Position: {board.fen()}")
        else:
            print("No move found!")
            break

    print("
Test completed!")
