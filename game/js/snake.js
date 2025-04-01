// Инициализация Telegram WebApp
let tg = window.Telegram.WebApp;
tg.expand();

// Константы игры
const CANVAS_WIDTH = 400;
const CANVAS_HEIGHT = 300;
const GRID_SIZE = 20;
const SNAKE_SPEED = 150;

// Состояние игры
let gameState = {
    canvas: null,
    ctx: null,
    snake: [],
    food: null,
    direction: 'right',
    nextDirection: 'right',
    score: 0,
    highScore: 0,
    gameActive: false,
    gameLoop: null
};

// DOM элементы
const canvas = document.getElementById('gameCanvas');
const scoreElement = document.getElementById('score');
const highScoreElement = document.getElementById('high-score');
const startButton = document.getElementById('start-button');
const pauseButton = document.getElementById('pause-button');
const modal = document.getElementById('game-over-modal');
const finalScoreElement = document.getElementById('final-score');
const finalHighScoreElement = document.getElementById('final-high-score');

// Кнопки управления
const upButton = document.getElementById('up-button');
const downButton = document.getElementById('down-button');
const leftButton = document.getElementById('left-button');
const rightButton = document.getElementById('right-button');

// Инициализация игры
function initGame() {
    // Настройка canvas
    canvas.width = CANVAS_WIDTH;
    canvas.height = CANVAS_HEIGHT;
    gameState.ctx = canvas.getContext('2d');

    // Сброс состояния
    gameState.snake = [
        { x: 3, y: 1 },
        { x: 2, y: 1 },
        { x: 1, y: 1 }
    ];
    gameState.direction = 'right';
    gameState.nextDirection = 'right';
    gameState.score = 0;
    updateScore();
    createFood();

    // Активация кнопок
    startButton.disabled = false;
    pauseButton.disabled = true;
    gameState.gameActive = false;
}

// Создание еды
function createFood() {
    let food;
    do {
        food = {
            x: Math.floor(Math.random() * (CANVAS_WIDTH / GRID_SIZE)),
            y: Math.floor(Math.random() * (CANVAS_HEIGHT / GRID_SIZE))
        };
    } while (gameState.snake.some(segment => segment.x === food.x && segment.y === food.y));
    gameState.food = food;
}

// Обновление счета
function updateScore() {
    scoreElement.textContent = gameState.score;
    highScoreElement.textContent = gameState.highScore;
}

// Отрисовка игры
function draw() {
    // Очистка canvas
    gameState.ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    // Отрисовка змейки
    gameState.ctx.fillStyle = '#2ecc71';
    gameState.snake.forEach((segment, index) => {
        if (index === 0) {
            // Голова змейки
            gameState.ctx.fillStyle = '#27ae60';
        } else {
            // Тело змейки
            gameState.ctx.fillStyle = '#2ecc71';
        }
        gameState.ctx.fillRect(
            segment.x * GRID_SIZE,
            segment.y * GRID_SIZE,
            GRID_SIZE - 1,
            GRID_SIZE - 1
        );
    });

    // Отрисовка еды
    gameState.ctx.fillStyle = '#e74c3c';
    gameState.ctx.fillRect(
        gameState.food.x * GRID_SIZE,
        gameState.food.y * GRID_SIZE,
        GRID_SIZE - 1,
        GRID_SIZE - 1
    );
}

// Обновление состояния игры
function update() {
    if (!gameState.gameActive) return;

    // Обновление направления
    gameState.direction = gameState.nextDirection;

    // Получение новой позиции головы
    const head = { ...gameState.snake[0] };
    switch (gameState.direction) {
        case 'up': head.y--; break;
        case 'down': head.y++; break;
        case 'left': head.x--; break;
        case 'right': head.x++; break;
    }

    // Проверка столкновения со стенами
    if (
        head.x < 0 ||
        head.x >= CANVAS_WIDTH / GRID_SIZE ||
        head.y < 0 ||
        head.y >= CANVAS_HEIGHT / GRID_SIZE
    ) {
        endGame();
        return;
    }

    // Проверка столкновения с собой
    if (gameState.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
        endGame();
        return;
    }

    // Добавление новой головы
    gameState.snake.unshift(head);

    // Проверка столкновения с едой
    if (head.x === gameState.food.x && head.y === gameState.food.y) {
        gameState.score++;
        updateScore();
        createFood();
    } else {
        // Удаление хвоста, если не съели еду
        gameState.snake.pop();
    }
}

// Игровой цикл
function gameLoop() {
    update();
    draw();
    gameState.gameLoop = setTimeout(() => {
        requestAnimationFrame(gameLoop);
    }, SNAKE_SPEED);
}

// Начало игры
function startGame() {
    gameState.gameActive = true;
    startButton.disabled = true;
    pauseButton.disabled = false;
    gameLoop();
}

// Пауза игры
function pauseGame() {
    gameState.gameActive = !gameState.gameActive;
    pauseButton.textContent = gameState.gameActive ? 'Пауза' : 'Продолжить';
}

// Окончание игры
function endGame() {
    gameState.gameActive = false;
    clearTimeout(gameState.gameLoop);
    
    if (gameState.score > gameState.highScore) {
        gameState.highScore = gameState.score;
    }

    finalScoreElement.textContent = gameState.score;
    finalHighScoreElement.textContent = gameState.highScore;
    modal.style.display = 'flex';
}

// Обработка управления
function handleKeyPress(e) {
    if (!gameState.gameActive) return;

    switch (e.key) {
        case 'ArrowUp':
            if (gameState.direction !== 'down') gameState.nextDirection = 'up';
            break;
        case 'ArrowDown':
            if (gameState.direction !== 'up') gameState.nextDirection = 'down';
            break;
        case 'ArrowLeft':
            if (gameState.direction !== 'right') gameState.nextDirection = 'left';
            break;
        case 'ArrowRight':
            if (gameState.direction !== 'left') gameState.nextDirection = 'right';
            break;
    }
}

// Обработчики событий
document.addEventListener('keydown', handleKeyPress);

upButton.addEventListener('click', () => {
    if (gameState.direction !== 'down') gameState.nextDirection = 'up';
});

downButton.addEventListener('click', () => {
    if (gameState.direction !== 'up') gameState.nextDirection = 'down';
});

leftButton.addEventListener('click', () => {
    if (gameState.direction !== 'right') gameState.nextDirection = 'left';
});

rightButton.addEventListener('click', () => {
    if (gameState.direction !== 'left') gameState.nextDirection = 'right';
});

startButton.addEventListener('click', startGame);
pauseButton.addEventListener('click', pauseGame);

modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
        initGame();
    }
});

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', initGame);

// Обработка событий Telegram WebApp
tg.ready(); 