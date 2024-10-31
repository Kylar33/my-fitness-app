  const express = require('express');
  const app = express();
  const http = require('http').createServer(app);
  const io = require('socket.io')(http);
  const fs = require('fs');
  const path = require('path');

  // Configuración de Express
  app.use(express.static('public'));

  // Rutas
  app.get('/', (req, res) => {
      res.sendFile(__dirname + '/public/index.html');
  });

  // Estado del juego
  let gameState = {
      board: Array(9).fill(''),
      currentPlayer: 'X',
      gameOver: false
  };

  // Lógica del juego
  function checkWinner(board) {
      const winningCombos = [
          [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
          [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
          [0, 4, 8], [2, 4, 6] // diagonals
      ];

      return winningCombos.some(combo => {
          const [a, b, c] = combo;
          return board[a] && board[a] === board[b] && board[a] === board[c];
      });
  }

  // Configuración de Socket.IO
  io.on('connection', (socket) => {
      console.log('A user connected');

      socket.emit('gameState', gameState);

      socket.on('makeMove', (position) => {
          if (!gameState.gameOver && gameState.board[position] === '') {
              gameState.board[position] = gameState.currentPlayer;
            
              if (checkWinner(gameState.board)) {
                  gameState.gameOver = true;
                  io.emit('gameOver', `Player ${gameState.currentPlayer} wins!`);
              } else if (gameState.board.every(cell => cell !== '')) {
                  gameState.gameOver = true;
                  io.emit('gameOver', 'Draw!');
              } else {
                  gameState.currentPlayer = gameState.currentPlayer === 'X' ? 'O' : 'X';
              }
            
              io.emit('gameState', gameState);
          }
      });

      socket.on('resetGame', () => {
          gameState = {
              board: Array(9).fill(''),
              currentPlayer: 'X',
              gameOver: false
          };
          io.emit('gameState', gameState);
      });
  });

  // Crear directorio public y archivo index.html
  const htmlContent = `
  <!DOCTYPE html>
  <html>
  <head>
      <title>Tic Tac Toe</title>
      <style>
          .board {
              display: grid;
              grid-template-columns: repeat(3, 100px);
              gap: 5px;
              margin: 20px auto;
              width: 310px;
          }
          .cell {
              width: 100px;
              height: 100px;
              border: 2px solid #333;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 40px;
              cursor: pointer;
          }
          .status {
              text-align: center;
              font-size: 24px;
              margin: 20px;
          }
          .reset-btn {
              display: block;
              margin: 20px auto;
              padding: 10px 20px;
              font-size: 18px;
          }
      </style>
  </head>
  <body>
      <div class="status" id="status">Player X's turn</div>
      <div class="board" id="board"></div>
      <button class="reset-btn" onclick="resetGame()">Reset Game</button>

      <script src="/socket.io/socket.io.js"></script>
      <script>
          const socket = io();
          const board = document.getElementById('board');
          const status = document.getElementById('status');

          // Create board cells
          for (let i = 0; i < 9; i++) {
              const cell = document.createElement('div');
              cell.className = 'cell';
              cell.setAttribute('data-index', i);
              cell.addEventListener('click', () => makeMove(i));
              board.appendChild(cell);
          }

          function makeMove(position) {
              socket.emit('makeMove', position);
          }

          function resetGame() {
              socket.emit('resetGame');
          }

          socket.on('gameState', (gameState) => {
              const cells = document.getElementsByClassName('cell');
              for (let i = 0; i < cells.length; i++) {
                  cells[i].textContent = gameState.board[i];
              }
              status.textContent = gameState.gameOver ? 
                  'Game Over' : 
                  \`Player \${gameState.currentPlayer}'s turn\`;
          });

          socket.on('gameOver', (message) => {
              status.textContent = message;
          });
      </script>
  </body>
  </html>
  `;

  const publicDir = path.join(__dirname, 'public');
  if (!fs.existsSync(publicDir)) {
      fs.mkdirSync(publicDir);
  }

  fs.writeFileSync(path.join(publicDir, 'index.html'), htmlContent);

  // Iniciar servidor
  const PORT = process.env.PORT || 3000;
  http.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
  });
