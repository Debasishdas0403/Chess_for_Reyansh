#!/bin/bash

# Deployment script for Streamlit Community Cloud
# This script helps prepare the application for deployment

echo "🚀 Preparing Chess Bot for deployment..."

# Check if all required files exist
required_files=("app.py" "chess_engine.py" "evaluation.py" "utils.py" "requirements.txt" "config.json")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done

echo "✅ All required files present"

# Check Python version
python_version=$(python3 --version 2>&1)
echo "🐍 Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Test the application
echo "🧪 Testing application..."
python3 -c "
import chess
import streamlit
from chess_engine import ChessEngine
from evaluation import PositionEvaluator
import utils

print('Testing chess engine...')
engine = ChessEngine()
board = chess.Board()
move = engine.get_best_move(board, depth=3)
print(f'Engine test: {move.uci() if move else "No move"}')

print('Testing evaluator...')
evaluator = PositionEvaluator()
score = evaluator.evaluate_position(board)
print(f'Evaluation test: {score:.2f}')

print('All tests passed!')
"

if [ $? -eq 0 ]; then
    echo "✅ Application tests passed"
else
    echo "❌ Application tests failed"
    exit 1
fi

echo "🎉 Chess Bot is ready for deployment!"
echo ""
echo "📝 Next steps for Streamlit Community Cloud:"
echo "1. Push all files to your GitHub repository"
echo "2. Go to https://share.streamlit.io"
echo "3. Connect your GitHub account"
echo "4. Select your repository and branch"
echo "5. Set app file to 'app.py'"
echo "6. Click 'Deploy!'"
echo ""
echo "🔗 Your app will be available at: https://your-app-name.streamlit.app"
