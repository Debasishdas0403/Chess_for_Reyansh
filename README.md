# 🏆 Intelligent Chess Bot Application

A sophisticated chess application built with Streamlit that allows you to play against an intelligent AI opponent powered by the minimax algorithm with alpha-beta pruning.

![Chess Bot Demo](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

### 🎮 Core Gameplay
- **Interactive Chess Board**: Click-based piece movement with visual feedback
- **Intelligent AI Opponent**: Powered by minimax algorithm with alpha-beta pruning
- **Multiple Difficulty Levels**: From Beginner (Depth 3) to Expert (Depth 6)
- **Legal Move Validation**: Ensures all moves follow chess rules
- **Game State Detection**: Automatic checkmate, stalemate, and draw detection

### 🧠 AI Engine
- **Minimax Algorithm**: Optimal move selection through game tree exploration
- **Alpha-Beta Pruning**: Up to 50% reduction in nodes evaluated
- **Position Evaluation**: Comprehensive evaluation including:
  - Material balance
  - Piece-square tables
  - King safety
  - Pawn structure
  - Piece mobility
  - Center control
- **Opening Book**: Database of strong opening moves
- **Transposition Table**: Caching for improved performance

### 📊 Analysis & Statistics
- **Real-time Position Evaluation**: See who's winning at any moment
- **Move History**: Complete game record with timestamps
- **Thinking Time Display**: See how long the bot takes to calculate
- **Game Statistics**: Track wins, losses, and draws
- **PGN Export**: Save games in standard chess notation

### 🎨 User Interface
- **Clean, Modern Design**: Intuitive Streamlit interface
- **Responsive Layout**: Works on desktop and mobile
- **Move Input Options**: UCI notation or dropdown selection
- **Visual Feedback**: Highlighted moves and position indicators
- **Game Controls**: New game, undo moves, difficulty selection

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project files**:
   ```bash
   # If using git
   git clone <your-repository-url>
   cd intelligent-chess-bot

   # Or download and extract the files to a folder
   ```

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

### First Game
1. Select your difficulty level in the sidebar
2. Choose whether to play as White or Black
3. Make your move using either:
   - UCI notation (e.g., "e2e4")
   - Dropdown selection from legal moves
4. Watch the bot calculate and respond
5. Continue until checkmate, stalemate, or draw!

## 📁 Project Structure

```
intelligent-chess-bot/
├── app.py                 # Main Streamlit application
├── chess_engine.py        # Minimax engine implementation
├── evaluation.py          # Position evaluation functions
├── utils.py              # Utility functions and helpers
├── requirements.txt       # Python dependencies
├── config.json           # Application configuration
└── README.md             # This file
```

### File Descriptions

- **`app.py`**: Main Streamlit interface with game controls and display
- **`chess_engine.py`**: Core AI engine using minimax with alpha-beta pruning
- **`evaluation.py`**: Chess position evaluation with material and positional factors
- **`utils.py`**: Helper functions for PGN export, statistics, and utilities
- **`config.json`**: Configurable settings for engine and UI behavior

## 🎯 How to Play

### Game Controls
- **New Game**: Start a fresh game
- **Undo Move**: Take back the last two moves (yours and bot's)
- **Difficulty**: Adjust AI strength from Beginner to Expert

### Making Moves
1. **UCI Notation**: Type moves like "e2e4" (from e2 to e4)
2. **Dropdown**: Select from available legal moves
3. **Validation**: Invalid moves are rejected with helpful messages

### Understanding the Interface
- **Position Evaluation**: Shows who has the advantage (+/- score)
- **Move History**: Complete list of moves with timing
- **Game Status**: Current turn, move number, and special states
- **FEN Notation**: Technical position description for analysis

## 🔧 Configuration

Edit `config.json` to customize the application:

```json
{
  "default_difficulty": 4,
  "max_thinking_time": 10.0,
  "enable_opening_book": true,
  "show_thinking_info": true,
  "auto_save_games": true
}
```

### Configuration Options
- `default_difficulty`: Starting AI difficulty (3-6)
- `max_thinking_time`: Maximum seconds for AI to think
- `enable_opening_book`: Use opening move database
- `show_thinking_info`: Display AI calculation details
- `auto_save_games`: Automatically save completed games

## 🧪 Technical Details

### Chess Engine Architecture

The AI uses a sophisticated minimax algorithm with several optimizations:

1. **Minimax with Alpha-Beta Pruning**:
   - Explores game tree to find optimal moves
   - Prunes branches that won't affect the result
   - Typically reduces nodes evaluated by 50%

2. **Position Evaluation Function**:
   - **Material**: Piece values (pawn=1, knight/bishop=3, rook=5, queen=9)
   - **Position**: Piece-square tables for optimal placement
   - **King Safety**: Pawn shield and exposure evaluation
   - **Pawn Structure**: Doubled, isolated, and passed pawn assessment
   - **Mobility**: Piece activity and move availability
   - **Center Control**: Bonus for controlling key squares

3. **Search Optimizations**:
   - **Move Ordering**: Search better moves first for efficient pruning
   - **Transposition Table**: Cache evaluated positions
   - **Iterative Deepening**: Gradually increase search depth
   - **Time Management**: Stop search within reasonable time limits

### Performance Characteristics

| Difficulty | Search Depth | Avg. Nodes | Thinking Time |
|------------|--------------|------------|---------------|
| Beginner   | 3            | ~1,000     | 0.1-0.5s     |
| Intermediate| 4           | ~10,000    | 0.5-2s       |
| Advanced   | 5            | ~50,000    | 2-5s         |
| Expert     | 6            | ~200,000   | 5-10s        |

## 🚀 Deployment

### Streamlit Community Cloud

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial chess bot application"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select the main branch and `app.py`
   - Click "Deploy"

3. **Configuration**:
   - Ensure `requirements.txt` includes all dependencies
   - Set any secrets in Streamlit Cloud settings if needed

### Local Development

For development and testing:

```bash
# Install in development mode
pip install -e .

# Run with debug info
streamlit run app.py --logger.level=debug

# Run tests (if you add them)
python -m pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Here are some ways to improve the project:

### Potential Enhancements
- **Advanced UI**: Drag-and-drop piece movement
- **Opening Database**: Larger collection of opening moves
- **Endgame Tablebase**: Perfect endgame play
- **Analysis Mode**: Detailed position analysis
- **Multiplayer**: Human vs human games
- **Time Controls**: Blitz, rapid, and classical time limits
- **Puzzle Mode**: Tactical puzzles and training

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with clear description

## 📈 Performance Tips

### For Better AI Performance
- **Increase Depth**: Higher difficulty for stronger play
- **Reduce Time Limit**: Faster moves but potentially weaker
- **Disable Opening Book**: Test pure engine strength

### For Better User Experience
- **Stable Internet**: Ensure stable connection for Streamlit Cloud
- **Modern Browser**: Use Chrome, Firefox, or Safari for best performance
- **Desktop/Laptop**: Recommended over mobile for complex games

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**:
```bash
pip install --upgrade -r requirements.txt
```

**Slow AI responses**:
- Reduce difficulty level
- Check `max_thinking_time` in config.json
- Ensure sufficient system resources

**Board not displaying**:
- Check browser console for JavaScript errors
- Try refreshing the page
- Ensure Streamlit is running on correct port

**Invalid moves accepted**:
- This shouldn't happen due to validation
- Report as a bug with the game state (FEN)

## 📚 Learning Resources

### Chess Programming
- [Chess Programming Wiki](https://www.chessprogramming.org/)
- [Minimax Algorithm](https://en.wikipedia.org/wiki/Minimax)
- [Alpha-Beta Pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)

### Python Chess Libraries
- [python-chess Documentation](https://python-chess.readthedocs.io/)
- [Stockfish Engine](https://stockfishchess.org/)

### Streamlit Development
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Community](https://discuss.streamlit.io/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **python-chess**: Excellent chess library for move generation and validation
- **Streamlit**: Amazing framework for rapid web app development
- **Chess Programming Community**: Valuable resources and algorithms
- **Stockfish**: Inspiration for evaluation techniques

## 📞 Support

If you encounter issues or have questions:

1. **Check the troubleshooting section** above
2. **Review the configuration** in `config.json`
3. **Look for similar issues** in the repository
4. **Create a new issue** with detailed description and error messages

---

**Enjoy playing chess against your intelligent AI opponent!** ♟️🤖

*Built with ❤️ using Python and Streamlit*
