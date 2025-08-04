import chess
import chess.polyglot
from typing import Dict, List, Tuple

class PositionEvaluator:
    """
    Chess position evaluation using material balance, piece-square tables,
    and positional factors
    """

    def __init__(self):
        # Piece values in centipawns (hundredths of a pawn)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000  # King safety is handled separately
        }

        # Piece-Square Tables (PST) - values for white pieces
        # Black pieces use flipped tables
        self.pst = self._initialize_piece_square_tables()

        # Endgame piece values (slightly different)
        self.endgame_piece_values = {
            chess.PAWN: 120,
            chess.KNIGHT: 300,
            chess.BISHOP: 320,
            chess.ROOK: 520,
            chess.QUEEN: 880,
            chess.KING: 20000
        }

    def evaluate_position(self, board: chess.Board) -> float:
        """
        Evaluate the current position from white's perspective
        Positive values favor white, negative values favor black

        Args:
            board: Chess board to evaluate

        Returns:
            Evaluation score in centipawns
        """
        if board.is_checkmate():
            # Checkmate is heavily penalized/rewarded
            return -29999 if board.turn else 29999

        if board.is_stalemate() or board.is_insufficient_material():
            return 0  # Draw

        # Check for fifty-move rule or threefold repetition
        if board.can_claim_fifty_moves() or board.can_claim_threefold_repetition():
            return 0

        score = 0

        # Determine game phase (opening/middlegame vs endgame)
        is_endgame = self._is_endgame(board)
        piece_values = self.endgame_piece_values if is_endgame else self.piece_values

        # Material balance and piece-square tables
        score += self._evaluate_material_and_position(board, piece_values, is_endgame)

        # Positional factors
        score += self._evaluate_king_safety(board, is_endgame)
        score += self._evaluate_pawn_structure(board)
        score += self._evaluate_piece_mobility(board)
        score += self._evaluate_center_control(board)

        # Small bonuses/penalties
        if not is_endgame:
            score += self._evaluate_development(board)
            score += self._evaluate_castling_rights(board)

        return score / 100.0  # Convert to pawns

    def _evaluate_material_and_position(self, board: chess.Board, 
                                      piece_values: Dict, is_endgame: bool) -> int:
        """Evaluate material balance and piece positioning"""
        score = 0

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Material value
                material_value = piece_values[piece.piece_type]

                # Piece-square table value
                pst_value = self._get_pst_value(piece, square, is_endgame)

                if piece.color == chess.WHITE:
                    score += material_value + pst_value
                else:
                    score -= material_value + pst_value

        return score

    def _evaluate_king_safety(self, board: chess.Board, is_endgame: bool) -> int:
        """Evaluate king safety"""
        score = 0

        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)

        if not is_endgame:
            # Penalize exposed kings in middlegame
            score += self._calculate_king_safety(board, white_king, chess.WHITE)
            score -= self._calculate_king_safety(board, black_king, chess.BLACK)
        else:
            # In endgame, kings should be active
            score += self._calculate_king_activity(board, white_king)
            score -= self._calculate_king_activity(board, black_king)

        return score

    def _evaluate_pawn_structure(self, board: chess.Board) -> int:
        """Evaluate pawn structure"""
        score = 0

        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)

        # Doubled pawns penalty
        score -= self._count_doubled_pawns(white_pawns) * 15
        score += self._count_doubled_pawns(black_pawns) * 15

        # Isolated pawns penalty
        score -= self._count_isolated_pawns(board, chess.WHITE) * 20
        score += self._count_isolated_pawns(board, chess.BLACK) * 20

        # Passed pawns bonus
        score += self._count_passed_pawns(board, chess.WHITE) * 30
        score -= self._count_passed_pawns(board, chess.BLACK) * 30

        return score

    def _evaluate_piece_mobility(self, board: chess.Board) -> int:
        """Evaluate piece mobility"""
        score = 0

        # Count legal moves (rough mobility measure)
        current_turn = board.turn

        # White mobility
        if current_turn == chess.WHITE:
            white_mobility = len(list(board.legal_moves))
        else:
            board.turn = chess.WHITE
            white_mobility = len(list(board.legal_moves))
            board.turn = chess.BLACK

        # Black mobility
        if current_turn == chess.BLACK:
            black_mobility = len(list(board.legal_moves))
        else:
            board.turn = chess.BLACK
            black_mobility = len(list(board.legal_moves))
            board.turn = chess.WHITE

        # Restore original turn
        board.turn = current_turn

        score += (white_mobility - black_mobility) * 2

        return score

    def _evaluate_center_control(self, board: chess.Board) -> int:
        """Evaluate center control"""
        score = 0
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        extended_center = [chess.C3, chess.C4, chess.C5, chess.C6,
                          chess.D3, chess.D6, chess.E3, chess.E6,
                          chess.F3, chess.F4, chess.F5, chess.F6]

        for square in center_squares:
            piece = board.piece_at(square)
            if piece:
                value = 10 if piece.piece_type == chess.PAWN else 5
                score += value if piece.color == chess.WHITE else -value

        for square in extended_center:
            piece = board.piece_at(square)
            if piece:
                value = 5 if piece.piece_type == chess.PAWN else 2
                score += value if piece.color == chess.WHITE else -value

        return score

    def _evaluate_development(self, board: chess.Board) -> int:
        """Evaluate piece development in opening/middlegame"""
        score = 0

        # Penalize unmoved pieces
        if board.piece_at(chess.G1) and board.piece_at(chess.G1).piece_type == chess.KNIGHT:
            score -= 10  # Knight still on g1
        if board.piece_at(chess.B1) and board.piece_at(chess.B1).piece_type == chess.KNIGHT:
            score -= 10  # Knight still on b1
        if board.piece_at(chess.G8) and board.piece_at(chess.G8).piece_type == chess.KNIGHT:
            score += 10  # Black knight still on g8
        if board.piece_at(chess.B8) and board.piece_at(chess.B8).piece_type == chess.KNIGHT:
            score += 10  # Black knight still on b8

        return score

    def _evaluate_castling_rights(self, board: chess.Board) -> int:
        """Evaluate castling rights"""
        score = 0

        if board.has_castling_rights(chess.WHITE):
            if board.has_kingside_castling_rights(chess.WHITE):
                score += 15
            if board.has_queenside_castling_rights(chess.WHITE):
                score += 10

        if board.has_castling_rights(chess.BLACK):
            if board.has_kingside_castling_rights(chess.BLACK):
                score -= 15
            if board.has_queenside_castling_rights(chess.BLACK):
                score -= 10

        return score

    def _is_endgame(self, board: chess.Board) -> bool:
        """Determine if position is in endgame phase"""
        # Simple endgame detection: few pieces remaining
        piece_count = len(board.piece_map())
        return piece_count <= 12  # Including kings

    def _get_pst_value(self, piece: chess.Piece, square: int, is_endgame: bool) -> int:
        """Get piece-square table value for a piece on a square"""
        piece_type = piece.piece_type
        color = piece.color

        if piece_type not in self.pst:
            return 0

        table_key = 'endgame' if is_endgame and piece_type == chess.KING else 'middlegame'
        if table_key not in self.pst[piece_type]:
            table_key = 'middlegame'

        pst = self.pst[piece_type][table_key]

        # Flip square for black pieces
        if color == chess.BLACK:
            square = chess.square_mirror(square)

        return pst[square]

    def _calculate_king_safety(self, board: chess.Board, king_square: int, color: chess.Color) -> int:
        """Calculate king safety score"""
        safety_score = 0

        # Pawn shield bonus
        if color == chess.WHITE:
            shield_squares = [king_square + 8, king_square + 7, king_square + 9]
        else:
            shield_squares = [king_square - 8, king_square - 7, king_square - 9]

        for square in shield_squares:
            if 0 <= square <= 63:
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                    safety_score += 10

        return safety_score

    def _calculate_king_activity(self, board: chess.Board, king_square: int) -> int:
        """Calculate king activity in endgame"""
        # Center proximity bonus in endgame
        center_distance = min(
            abs(chess.square_file(king_square) - 3.5),
            abs(chess.square_rank(king_square) - 3.5)
        )
        return int((4 - center_distance) * 5)

    def _count_doubled_pawns(self, pawns: chess.SquareSet) -> int:
        """Count doubled pawns"""
        files = [0] * 8
        for square in pawns:
            files[chess.square_file(square)] += 1

        return sum(max(0, count - 1) for count in files)

    def _count_isolated_pawns(self, board: chess.Board, color: chess.Color) -> int:
        """Count isolated pawns"""
        pawns = board.pieces(chess.PAWN, color)
        isolated_count = 0

        for square in pawns:
            file = chess.square_file(square)
            has_neighbor = False

            # Check adjacent files for friendly pawns
            for adj_file in [file - 1, file + 1]:
                if 0 <= adj_file <= 7:
                    file_pawns = pawns & chess.BB_FILES[adj_file]
                    if file_pawns:
                        has_neighbor = True
                        break

            if not has_neighbor:
                isolated_count += 1

        return isolated_count

    def _count_passed_pawns(self, board: chess.Board, color: chess.Color) -> int:
        """Count passed pawns"""
        pawns = board.pieces(chess.PAWN, color)
        opponent_pawns = board.pieces(chess.PAWN, not color)
        passed_count = 0

        for square in pawns:
            file = chess.square_file(square)
            rank = chess.square_rank(square)

            is_passed = True

            # Check if opponent has pawns that can block or capture
            for opp_square in opponent_pawns:
                opp_file = chess.square_file(opp_square)
                opp_rank = chess.square_rank(opp_square)

                # Check files that can interfere with this pawn
                if abs(opp_file - file) <= 1:
                    if color == chess.WHITE and opp_rank > rank:
                        is_passed = False
                        break
                    elif color == chess.BLACK and opp_rank < rank:
                        is_passed = False
                        break

            if is_passed:
                passed_count += 1

        return passed_count

    def _initialize_piece_square_tables(self) -> Dict:
        """Initialize piece-square tables"""
        # Simplified piece-square tables
        pawn_table = [
             0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
             5,  5, 10, 25, 25, 10,  5,  5,
             0,  0,  0, 20, 20,  0,  0,  0,
             5, -5,-10,  0,  0,-10, -5,  5,
             5, 10, 10,-20,-20, 10, 10,  5,
             0,  0,  0,  0,  0,  0,  0,  0
        ]

        knight_table = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        ]

        bishop_table = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20
        ]

        rook_table = [
             0,  0,  0,  0,  0,  0,  0,  0,
             5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
             0,  0,  0,  5,  5,  0,  0,  0
        ]

        queen_table = [
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
             -5,  0,  5,  5,  5,  5,  0, -5,
              0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20
        ]

        king_middlegame_table = [
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
             20, 20,  0,  0,  0,  0, 20, 20,
             20, 30, 10,  0,  0, 10, 30, 20
        ]

        king_endgame_table = [
            -50,-40,-30,-20,-20,-30,-40,-50,
            -30,-20,-10,  0,  0,-10,-20,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-30,  0,  0,  0,  0,-30,-30,
            -50,-30,-30,-30,-30,-30,-30,-50
        ]

        return {
            chess.PAWN: {'middlegame': pawn_table},
            chess.KNIGHT: {'middlegame': knight_table},
            chess.BISHOP: {'middlegame': bishop_table},
            chess.ROOK: {'middlegame': rook_table},
            chess.QUEEN: {'middlegame': queen_table},
            chess.KING: {
                'middlegame': king_middlegame_table,
                'endgame': king_endgame_table
            }
        }

# Test the evaluator
if __name__ == "__main__":
    evaluator = PositionEvaluator()
    board = chess.Board()

    print("Testing Position Evaluator...")
    print(f"Starting position evaluation: {evaluator.evaluate_position(board):.2f}")

    # Test a few positions
    test_positions = [
        "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",  # Italian Game
        "rnbqkb1r/pp1ppppp/5n2/2p5/2P5/5N2/PP1PPPPP/RNBQKB1R w KQkq - 2 3",  # English Opening
        "8/8/8/3k4/3K4/8/8/8 w - - 0 1"  # King and King endgame
    ]

    for i, fen in enumerate(test_positions, 1):
        board = chess.Board(fen)
        evaluation = evaluator.evaluate_position(board)
        print(f"Position {i} evaluation: {evaluation:.2f}")
        print(f"FEN: {fen}")
        print()
