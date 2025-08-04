// Chess Game Application
class ChessGame {
    constructor() {
        this.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ];
        
        this.pieceSymbols = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        };
        
        this.pieceValues = {
            'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
            'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
        };
        
        this.currentTurn = 'white';
        this.selectedSquare = null;
        this.moveHistory = [];
        this.gameStats = {
            totalMoves: 0,
            captures: 0,
            checks: 0,
            gamePhase: 'Opening'
        };
        this.gameActive = true;
        this.lastMove = null;
        
        this.init();
    }
    
    init() {
        this.createBoard();
        this.updateUI();
        this.bindEvents();
        this.renderBoard();
    }
    
    createBoard() {
        const boardEl = document.getElementById('chess-board');
        boardEl.innerHTML = '';
        
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                square.classList.add('chess-square');
                square.classList.add((row + col) % 2 === 0 ? 'light' : 'dark');
                square.dataset.row = row;
                square.dataset.col = col;
                
                square.addEventListener('click', (e) => this.handleSquareClick(e));
                boardEl.appendChild(square);
            }
        }
    }
    
    renderBoard() {
        const squares = document.querySelectorAll('.chess-square');
        squares.forEach(square => {
            const row = parseInt(square.dataset.row);
            const col = parseInt(square.dataset.col);
            const piece = this.board[row][col];
            
            // Clear previous styling
            square.classList.remove('selected', 'valid-move', 'last-move');
            
            // Add piece symbol
            if (piece) {
                square.innerHTML = `<span class="chess-piece">${this.pieceSymbols[piece]}</span>`;
            } else {
                square.innerHTML = '';
            }
            
            // Highlight last move
            if (this.lastMove && 
                ((this.lastMove.from.row === row && this.lastMove.from.col === col) ||
                 (this.lastMove.to.row === row && this.lastMove.to.col === col))) {
                square.classList.add('last-move');
            }
        });
        
        // Highlight selected square
        if (this.selectedSquare) {
            const selectedEl = document.querySelector(
                `[data-row="${this.selectedSquare.row}"][data-col="${this.selectedSquare.col}"]`
            );
            if (selectedEl) {
                selectedEl.classList.add('selected');
                this.highlightValidMoves(this.selectedSquare.row, this.selectedSquare.col);
            }
        }
    }
    
    handleSquareClick(e) {
        if (!this.gameActive || this.currentTurn !== 'white') return;
        
        const row = parseInt(e.currentTarget.dataset.row);
        const col = parseInt(e.currentTarget.dataset.col);
        const piece = this.board[row][col];
        
        if (this.selectedSquare) {
            // Try to make a move
            if (this.isValidMove(this.selectedSquare.row, this.selectedSquare.col, row, col)) {
                this.makeMove(this.selectedSquare.row, this.selectedSquare.col, row, col);
                this.selectedSquare = null;
                this.renderBoard();
                
                if (this.gameActive) {
                    setTimeout(() => this.makeAIMove(), 1000);
                }
            } else if (piece && this.isPlayerPiece(piece)) {
                // Select new piece
                this.selectedSquare = { row, col };
                this.renderBoard();
            } else {
                // Deselect
                this.selectedSquare = null;
                this.renderBoard();
            }
        } else if (piece && this.isPlayerPiece(piece)) {
            // Select piece
            this.selectedSquare = { row, col };
            this.renderBoard();
        }
    }
    
    isPlayerPiece(piece) {
        return this.currentTurn === 'white' ? piece === piece.toUpperCase() : piece === piece.toLowerCase();
    }
    
    highlightValidMoves(fromRow, fromCol) {
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                if (this.isValidMove(fromRow, fromCol, row, col)) {
                    const square = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
                    if (square) {
                        square.classList.add('valid-move');
                    }
                }
            }
        }
    }
    
    isValidMove(fromRow, fromCol, toRow, toCol) {
        const piece = this.board[fromRow][fromCol];
        const targetPiece = this.board[toRow][toCol];
        
        if (!piece) return false;
        if (fromRow === toRow && fromCol === toCol) return false;
        
        // Can't capture own pieces
        if (targetPiece && this.isSameColor(piece, targetPiece)) return false;
        
        // Check if it's the correct player's turn
        if (this.currentTurn === 'white' && piece !== piece.toUpperCase()) return false;
        if (this.currentTurn === 'black' && piece !== piece.toLowerCase()) return false;
        
        const pieceType = piece.toLowerCase();
        
        switch (pieceType) {
            case 'p':
                return this.isValidPawnMove(fromRow, fromCol, toRow, toCol, piece);
            case 'r':
                return this.isValidRookMove(fromRow, fromCol, toRow, toCol);
            case 'n':
                return this.isValidKnightMove(fromRow, fromCol, toRow, toCol);
            case 'b':
                return this.isValidBishopMove(fromRow, fromCol, toRow, toCol);
            case 'q':
                return this.isValidQueenMove(fromRow, fromCol, toRow, toCol);
            case 'k':
                return this.isValidKingMove(fromRow, fromCol, toRow, toCol);
            default:
                return false;
        }
    }
    
    isValidPawnMove(fromRow, fromCol, toRow, toCol, piece) {
        const isWhite = piece === piece.toUpperCase();
        const direction = isWhite ? -1 : 1;
        const startRow = isWhite ? 6 : 1;
        const targetPiece = this.board[toRow][toCol];
        
        // Forward move
        if (fromCol === toCol) {
            if (targetPiece) return false; // Can't move forward into a piece
            if (toRow === fromRow + direction) return true; // One square forward
            if (fromRow === startRow && toRow === fromRow + 2 * direction) return true; // Two squares from start
        }
        
        // Diagonal capture
        if (Math.abs(fromCol - toCol) === 1 && toRow === fromRow + direction) {
            return targetPiece && !this.isSameColor(piece, targetPiece);
        }
        
        return false;
    }
    
    isValidRookMove(fromRow, fromCol, toRow, toCol) {
        if (fromRow !== toRow && fromCol !== toCol) return false;
        return this.isPathClear(fromRow, fromCol, toRow, toCol);
    }
    
    isValidKnightMove(fromRow, fromCol, toRow, toCol) {
        const rowDiff = Math.abs(fromRow - toRow);
        const colDiff = Math.abs(fromCol - toCol);
        return (rowDiff === 2 && colDiff === 1) || (rowDiff === 1 && colDiff === 2);
    }
    
    isValidBishopMove(fromRow, fromCol, toRow, toCol) {
        const rowDiff = Math.abs(fromRow - toRow);
        const colDiff = Math.abs(fromCol - toCol);
        if (rowDiff !== colDiff) return false;
        return this.isPathClear(fromRow, fromCol, toRow, toCol);
    }
    
    isValidQueenMove(fromRow, fromCol, toRow, toCol) {
        return this.isValidRookMove(fromRow, fromCol, toRow, toCol) || 
               this.isValidBishopMove(fromRow, fromCol, toRow, toCol);
    }
    
    isValidKingMove(fromRow, fromCol, toRow, toCol) {
        const rowDiff = Math.abs(fromRow - toRow);
        const colDiff = Math.abs(fromCol - toCol);
        return rowDiff <= 1 && colDiff <= 1;
    }
    
    isPathClear(fromRow, fromCol, toRow, toCol) {
        const rowDir = toRow > fromRow ? 1 : toRow < fromRow ? -1 : 0;
        const colDir = toCol > fromCol ? 1 : toCol < fromCol ? -1 : 0;
        
        let currentRow = fromRow + rowDir;
        let currentCol = fromCol + colDir;
        
        while (currentRow !== toRow || currentCol !== toCol) {
            if (this.board[currentRow][currentCol]) return false;
            currentRow += rowDir;
            currentCol += colDir;
        }
        
        return true;
    }
    
    isSameColor(piece1, piece2) {
        return (piece1 === piece1.toUpperCase()) === (piece2 === piece2.toUpperCase());
    }
    
    makeMove(fromRow, fromCol, toRow, toCol) {
        const piece = this.board[fromRow][fromCol];
        const capturedPiece = this.board[toRow][toCol];
        
        // Make the move
        this.board[toRow][toCol] = piece;
        this.board[fromRow][fromCol] = '';
        
        // Record move
        const moveNotation = this.getMoveNotation(piece, fromRow, fromCol, toRow, toCol, capturedPiece);
        this.moveHistory.push({
            piece,
            from: { row: fromRow, col: fromCol },
            to: { row: toRow, col: toCol },
            captured: capturedPiece,
            notation: moveNotation
        });
        
        this.lastMove = { from: { row: fromRow, col: fromCol }, to: { row: toRow, col: toCol } };
        
        // Update stats
        this.gameStats.totalMoves++;
        if (capturedPiece) this.gameStats.captures++;
        
        // Switch turns
        this.currentTurn = this.currentTurn === 'white' ? 'black' : 'white';
        
        // Update game phase
        this.updateGamePhase();
        
        this.updateUI();
        this.updateMoveHistory();
    }
    
    getMoveNotation(piece, fromRow, fromCol, toRow, toCol, captured) {
        const files = 'abcdefgh';
        const ranks = '87654321';
        
        const fromSquare = files[fromCol] + ranks[fromRow];
        const toSquare = files[toCol] + ranks[toRow];
        const pieceSymbol = piece.toUpperCase() === 'P' ? '' : piece.toUpperCase();
        const captureSymbol = captured ? 'x' : '';
        
        return `${pieceSymbol}${captureSymbol}${toSquare}`;
    }
    
    async makeAIMove() {
        if (!this.gameActive || this.currentTurn !== 'black') return;
        
        // Show AI thinking
        document.getElementById('ai-thinking').style.display = 'flex';
        
        const startTime = Date.now();
        
        // Simulate thinking time
        await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200));
        
        const validMoves = this.getAllValidMoves('black');
        
        if (validMoves.length === 0) {
            this.gameActive = false;
            document.getElementById('game-status').textContent = 'Checkmate - White Wins!';
            document.getElementById('ai-thinking').style.display = 'none';
            return;
        }
        
        // Simple AI: Random move with slight preference for captures
        let bestMove = validMoves[Math.floor(Math.random() * validMoves.length)];
        
        // Prefer captures
        const captures = validMoves.filter(move => 
            this.board[move.to.row][move.to.col] !== ''
        );
        
        if (captures.length > 0 && Math.random() < 0.7) {
            bestMove = captures[Math.floor(Math.random() * captures.length)];
        }
        
        // Update AI analysis
        const thinkingTime = (Date.now() - startTime) / 1000;
        document.getElementById('moves-calculated').textContent = validMoves.length;
        document.getElementById('thinking-time').textContent = `${thinkingTime.toFixed(1)}s`;
        document.getElementById('best-move').textContent = 
            this.getMoveNotation(
                this.board[bestMove.from.row][bestMove.from.col],
                bestMove.from.row, bestMove.from.col,
                bestMove.to.row, bestMove.to.col,
                this.board[bestMove.to.row][bestMove.to.col]
            );
        
        // Make the move
        this.makeMove(bestMove.from.row, bestMove.from.col, bestMove.to.row, bestMove.to.col);
        this.renderBoard();
        
        document.getElementById('ai-thinking').style.display = 'none';
    }
    
    getAllValidMoves(color) {
        const moves = [];
        
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const piece = this.board[row][col];
                if (!piece) continue;
                
                const isWhite = piece === piece.toUpperCase();
                if ((color === 'white' && !isWhite) || (color === 'black' && isWhite)) continue;
                
                for (let toRow = 0; toRow < 8; toRow++) {
                    for (let toCol = 0; toCol < 8; toCol++) {
                        if (this.isValidMove(row, col, toRow, toCol)) {
                            moves.push({
                                from: { row, col },
                                to: { row: toRow, col: toCol }
                            });
                        }
                    }
                }
            }
        }
        
        return moves;
    }
    
    updateGamePhase() {
        const totalMoves = this.gameStats.totalMoves;
        if (totalMoves < 20) {
            this.gameStats.gamePhase = 'Opening';
        } else if (totalMoves < 40) {
            this.gameStats.gamePhase = 'Middlegame';
        } else {
            this.gameStats.gamePhase = 'Endgame';
        }
    }
    
    evaluatePosition() {
        let evaluation = 0;
        
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const piece = this.board[row][col];
                if (piece) {
                    const value = this.pieceValues[piece.toLowerCase()];
                    evaluation += piece === piece.toUpperCase() ? value : -value;
                }
            }
        }
        
        return evaluation;
    }
    
    updateUI() {
        document.getElementById('current-turn').textContent = 
            this.currentTurn.charAt(0).toUpperCase() + this.currentTurn.slice(1);
        
        document.getElementById('game-status').textContent = 
            this.gameActive ? 'Active' : 'Game Over';
        
        document.getElementById('position-eval').textContent = 
            this.evaluatePosition().toFixed(1);
        
        document.getElementById('total-moves').textContent = this.gameStats.totalMoves;
        document.getElementById('captures').textContent = this.gameStats.captures;
        document.getElementById('checks').textContent = this.gameStats.checks;
        document.getElementById('game-phase').textContent = this.gameStats.gamePhase;
    }
    
    updateMoveHistory() {
        const historyEl = document.getElementById('move-history');
        
        if (this.moveHistory.length === 0) {
            historyEl.innerHTML = '<p class="move-history-empty">No moves yet. Click on a piece to start!</p>';
            return;
        }
        
        let html = '';
        for (let i = 0; i < this.moveHistory.length; i += 2) {
            const moveNumber = Math.floor(i / 2) + 1;
            const whiteMove = this.moveHistory[i];
            const blackMove = this.moveHistory[i + 1];
            
            html += `
                <div class="move-entry">
                    <span class="move-number">${moveNumber}.</span>
                    <span class="move-white">${whiteMove.notation}</span>
                    ${blackMove ? `<span class="move-black">${blackMove.notation}</span>` : ''}
                </div>
            `;
        }
        
        historyEl.innerHTML = html;
        historyEl.scrollTop = historyEl.scrollHeight;
    }
    
    newGame() {
        this.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ];
        
        this.currentTurn = 'white';
        this.selectedSquare = null;
        this.moveHistory = [];
        this.gameStats = {
            totalMoves: 0,
            captures: 0,
            checks: 0,
            gamePhase: 'Opening'
        };
        this.gameActive = true;
        this.lastMove = null;
        
        document.getElementById('ai-thinking').style.display = 'none';
        document.getElementById('moves-calculated').textContent = '0';
        document.getElementById('thinking-time').textContent = '0.0s';
        document.getElementById('best-move').textContent = '-';
        
        this.renderBoard();
        this.updateUI();
        this.updateMoveHistory();
    }
    
    showHint() {
        if (this.currentTurn !== 'white' || !this.gameActive) return;
        
        const validMoves = this.getAllValidMoves('white');
        if (validMoves.length === 0) return;
        
        const randomMove = validMoves[Math.floor(Math.random() * validMoves.length)];
        
        // Briefly highlight the hint move
        const fromSquare = document.querySelector(
            `[data-row="${randomMove.from.row}"][data-col="${randomMove.from.col}"]`
        );
        const toSquare = document.querySelector(
            `[data-row="${randomMove.to.row}"][data-col="${randomMove.to.col}"]`
        );
        
        if (fromSquare && toSquare) {
            fromSquare.style.backgroundColor = '#90EE90';
            toSquare.style.backgroundColor = '#90EE90';
            
            setTimeout(() => {
                this.renderBoard();
            }, 2000);
        }
    }
    
    bindEvents() {
        document.getElementById('new-game-btn').addEventListener('click', () => this.newGame());
        document.getElementById('hint-btn').addEventListener('click', () => this.showHint());
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChessGame();
});