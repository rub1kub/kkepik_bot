// Инициализация Telegram WebApp
let tg = window.Telegram.WebApp;
tg.expand();

// Состояние игры
let gameState = {
    board: Array(9).fill(''),
    currentPlayer: 'X',
    scores: {
        X: 0,
        O: 0
    },
    gameActive: true
};

// DOM элементы
const gameBoard = document.querySelector('.game-board');
const cells = document.querySelectorAll('.cell');
const status = document.querySelector('.status');
const playerX = document.querySelector('.player-x');
const playerO = document.querySelector('.player-o');
const resetButton = document.querySelector('.reset-button');
const modal = document.querySelector('.modal');
const modalMessage = document.querySelector('.modal h2');

// Инициализация игры
function initGame() {
    gameState.board = Array(9).fill('');
    gameState.currentPlayer = 'X';
    gameState.gameActive = true;
    updateUI();
}

// Обновление интерфейса
function updateUI() {
    // Обновление доски
    cells.forEach((cell, index) => {
        cell.textContent = gameState.board[index];
        cell.classList.remove('x', 'o', 'win');
        if (gameState.board[index]) {
            cell.classList.add(gameState.board[index].toLowerCase());
        }
    });

    // Обновление статуса
    status.textContent = `Ход игрока ${gameState.currentPlayer}`;

    // Обновление активного игрока
    playerX.classList.toggle('active', gameState.currentPlayer === 'X');
    playerO.classList.toggle('active', gameState.currentPlayer === 'O');

    // Обновление счета
    playerX.querySelector('.player-score').textContent = gameState.scores.X;
    playerO.querySelector('.player-score').textContent = gameState.scores.O;
}

// Проверка победы
function checkWin() {
    const winPatterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], // горизонтали
        [0, 3, 6], [1, 4, 7], [2, 5, 8], // вертикали
        [0, 4, 8], [2, 4, 6]             // диагонали
    ];

    for (const pattern of winPatterns) {
        const [a, b, c] = pattern;
        if (gameState.board[a] && 
            gameState.board[a] === gameState.board[b] && 
            gameState.board[a] === gameState.board[c]) {
            return gameState.board[a];
        }
    }

    return null;
}

// Проверка ничьей
function checkDraw() {
    return gameState.board.every(cell => cell !== '');
}

// Обработка хода
function handleMove(index) {
    if (!gameState.gameActive || gameState.board[index] !== '') return;

    gameState.board[index] = gameState.currentPlayer;
    updateUI();

    const winner = checkWin();
    if (winner) {
        gameState.scores[winner]++;
        gameState.gameActive = false;
        showModal(`Игрок ${winner} победил!`);
        return;
    }

    if (checkDraw()) {
        gameState.gameActive = false;
        showModal('Ничья!');
        return;
    }

    gameState.currentPlayer = gameState.currentPlayer === 'X' ? 'O' : 'X';
}

// Показать модальное окно
function showModal(message) {
    modalMessage.textContent = message;
    modal.style.display = 'flex';
}

// Скрыть модальное окно
function hideModal() {
    modal.style.display = 'none';
    initGame();
}

// Обработчики событий
cells.forEach((cell, index) => {
    cell.addEventListener('click', () => handleMove(index));
});

resetButton.addEventListener('click', () => {
    if (gameState.gameActive) {
        if (confirm('Вы уверены, что хотите начать новую игру?')) {
            initGame();
        }
    } else {
        initGame();
    }
});

modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        hideModal();
    }
});

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', initGame);

// Обработка событий Telegram WebApp
tg.ready(); 