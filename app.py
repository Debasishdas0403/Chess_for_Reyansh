import streamlit as st
import chess
import chess.svg
import chess.engine
from chess_engine import ChessEngine
from evaluation import PositionEvaluator
import time
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Intelligent Chess Bot",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chess-board {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .game-info {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .move-history {
        max-height: 300px;
        overflow-y: auto;
        background-color: #ffffff;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'board' not in st.session_state:
        st.session_state.board = chess.Board()
    if 'game_history' not in st.session_state:
        st.session_state.game_history = []
    if 'engine' not in st.session_state:
        st.session_state.engine = ChessEngine()
    if 'evaluator' not in st.session_state:
        st.session_state.evaluator = PositionEvaluator()
    if 'game_stats' not in st.session_state:
        st.session_state.game_stats = {
            'games_played': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0
        }

def render_board():
    """Render the chess board using SVG"""
    board_svg = chess.svg.board(
        board=st.session_state.board,
        size=400,
        coordinates=True,
        lastmove=st.session_state.board.peek() if st.session_state.board.move_stack else None
    )
    
    # Display the board
    st.markdown(
        f'<div class="chess-board">{board_svg}</div>',
        unsafe_allow_html=True
    )

def make_move(move_uci):
    """Make a move on the board"""
    try:
        move = chess.Move.from_uci(move_uci)
        if move in st.session_state.board.legal_moves:
            st.session_state.board.push(move)
            st.session_state.game_history.append({
                'move': move_uci,
                'san': st.session_state.board.san(move),
                'timestamp': datetime.now().isoformat()
            })
            return True
        return False
    except:
        return False

def bot_move():
    """Let the bot make a move"""
    if not st.session_state.board.is_game_over():
        with st.spinner("Bot is thinking..."):
            start_time = time.time()
            best_move = st.session_state.engine.get_best_move(
                st.session_state.board,
                depth=st.session_state.difficulty
            )
            thinking_time = time.time() - start_time
            
            if best_move:
                st.session_state.board.push(best_move)
                st.session_state.game_history.append({
                    'move': best_move.uci(),
                    'san': st.session_state.board.san(best_move),
                    'timestamp': datetime.now().isoformat(),
                    'thinking_time': thinking_time,
                    'is_bot': True
                })
                return best_move, thinking_time
    return None, 0

def main():
    initialize_session_state()
    
    # Header
    st.title("♟️ Intelligent Chess Bot")
    st.markdown("Play against an AI opponent powered by minimax algorithm with alpha-beta pruning!")
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎮 Game Controls")
        
        # Difficulty selection
        difficulty_map = {
            "Beginner (Depth 3)": 3,
            "Intermediate (Depth 4)": 4,
            "Advanced (Depth 5)": 5,
            "Expert (Depth 6)": 6
        }
        
        difficulty_choice = st.selectbox(
            "Select Difficulty",
            options=list(difficulty_map.keys()),
            index=1
        )
        st.session_state.difficulty = difficulty_map[difficulty_choice]
        
        # Game controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Game"):
                st.session_state.board = chess.Board()
                st.session_state.game_history = []
                st.rerun()
        
        with col2:
            if st.button("↩️ Undo Move") and st.session_state.board.move_stack:
                # Undo last two moves (player and bot)
                if len(st.session_state.board.move_stack) >= 2:
                    st.session_state.board.pop()
                    st.session_state.board.pop()
                    st.session_state.game_history = st.session_state.game_history[:-2]
                st.rerun()
        
        # Player color selection
        st.markdown("---")
        player_color = st.radio("Play as:", ["White", "Black"], index=0)
        
        # Game statistics
        st.markdown("---")
        st.subheader("📊 Statistics")
        stats = st.session_state.game_stats
        st.metric("Games Played", stats['games_played'])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Wins", stats['wins'])
        with col2:
            st.metric("Losses", stats['losses'])
        with col3:
            st.metric("Draws", stats['draws'])
    
    # Main game area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Render the chess board
        render_board()
        
        # Move input
        if not st.session_state.board.is_game_over():
            current_turn = "White" if st.session_state.board.turn else "Black"
            player_turn = (
                (player_color == "White" and st.session_state.board.turn) or
                (player_color == "Black" and not st.session_state.board.turn)
            )
            
            if player_turn:
                st.subheader(f"Your turn ({current_turn})")
                
                # Move input methods
                move_input_method = st.radio("Input method:", ["UCI Notation", "Dropdown"], horizontal=True)
                
                if move_input_method == "UCI Notation":
                    move_input = st.text_input(
                        "Enter your move (e.g., e2e4):",
                        placeholder="Enter UCI notation",
                        key="move_input"
                    )
                    
                    if st.button("Make Move") and move_input:
                        if make_move(move_input):
                            st.success(f"Move {move_input} played!")
                            st.rerun()
                        else:
                            st.error("Invalid move! Please try again.")
                
                else:
                    # Dropdown move selection
                    legal_moves = list(st.session_state.board.legal_moves)
                    if legal_moves:
                        move_options = [move.uci() for move in legal_moves]
                        selected_move = st.selectbox("Select a move:", move_options)
                        
                        if st.button("Make Selected Move"):
                            if make_move(selected_move):
                                st.success(f"Move {selected_move} played!")
                                st.rerun()
            else:
                st.subheader(f"Bot's turn ({current_turn})")
                if st.button("Let Bot Move") or st.session_state.get('auto_play', False):
                    best_move, thinking_time = bot_move()
                    if best_move:
                        st.success(f"Bot played: {best_move.uci()} (Thinking time: {thinking_time:.2f}s)")
                        st.rerun()
        
        # Game status
        if st.session_state.board.is_game_over():
            result = st.session_state.board.result()
            if result == "1-0":
                st.success("🎉 White wins!")
            elif result == "0-1":
                st.success("🎉 Black wins!")
            else:
                st.info("🤝 Game ended in a draw!")
    
    with col2:
        # Position evaluation
        st.subheader("📈 Position Analysis")
        eval_score = st.session_state.evaluator.evaluate_position(st.session_state.board)
        
        # Display evaluation
        if eval_score > 0:
            st.metric("Position Evaluation", f"+{eval_score:.2f}", "White advantage")
        elif eval_score < 0:
            st.metric("Position Evaluation", f"{eval_score:.2f}", "Black advantage")
        else:
            st.metric("Position Evaluation", "0.00", "Equal position")
        
        # Move history
        st.subheader("📝 Move History")
        if st.session_state.game_history:
            history_text = ""
            for i, move_data in enumerate(st.session_state.game_history):
                move_num = (i // 2) + 1
                if i % 2 == 0:
                    history_text += f"{move_num}. {move_data['san']} "
                else:
                    history_text += f"{move_data['san']}\n"
                    
                if move_data.get('is_bot'):
                    history_text += f"(Bot: {move_data.get('thinking_time', 0):.1f}s) "
            
            st.markdown(f'<div class="move-history">{history_text}</div>', unsafe_allow_html=True)
        else:
            st.write("No moves yet")
        
        # Current position info
        st.subheader("ℹ️ Position Info")
        st.write(f"**Turn:** {'White' if st.session_state.board.turn else 'Black'}")
        st.write(f"**Move Number:** {st.session_state.board.fullmove_number}")
        st.write(f"**Halfmove Clock:** {st.session_state.board.halfmove_clock}")
        
        if st.session_state.board.is_check():
            st.warning("⚠️ King in check!")
        
        # FEN notation
        st.subheader("🔤 FEN Notation")
        st.code(st.session_state.board.fen())

if __name__ == "__main__":
    main()
