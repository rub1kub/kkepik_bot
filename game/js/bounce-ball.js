// Инициализация Telegram WebApp
let tg = window.Telegram.WebApp;
tg.expand();

// Константы игры
const CANVAS_WIDTH = 400;
const CANVAS_HEIGHT = 300;
const PADDLE_WIDTH = 80;
const PADDLE_HEIGHT = 10;
const BALL_SIZE = 10;
const BALL_SPEED = 5;
const PADDLE_SPEED = 8;

// Состояние игры
let gameState = {
    canvas: null,
    ctx: null,
    paddle1: {
        x: CANVAS_WIDTH / 2 - PADDLE_WIDTH / 2,
        y: PADDLE_HEIGHT + 10,
        width: PADDLE_WIDTH,
        height: PADDLE_HEIGHT,
        color: '#3498db',
        score: 0
    },
    paddle2: {
        x: CANVAS_WIDTH / 2 - PADDLE_WIDTH / 2,
        y: CANVAS_HEIGHT - PADDLE_HEIGHT - 10,
        width: PADDLE_WIDTH,
        height: PADDLE_HEIGHT,
        color: '#e74c3c',
        score: 0
    },
    ball: {
        x: CANVAS_WIDTH / 2,
        y: CANVAS_HEIGHT / 2,
        size: BALL_SIZE,
        speedX: BALL_SPEED,
        speedY: BALL_SPEED,
        color: '#2ecc71'
    },
    gameActive: false,
    animationFrame: null
};

// DOM элементы
const canvas = document.getElementById('gameCanvas');
const score1Element = document.getElementById('score1');
const score2Element = document.getElementById('score2');
const startButton = document.getElementById('start-button');
const pauseButton = document.getElementById('pause-button');
const modal = document.getElementById('game-over-modal');
const finalScore1Element = document.getElementById('final-score1');
const finalScore2Element = document.getElementById('final-score2');

// Инициализация игры
function initGame() {
    // Настройка canvas
    canvas.width = CANVAS_WIDTH;
    canvas.height = CANVAS_HEIGHT;
    gameState.ctx = canvas.getContext('2d');

    // Сброс состояния
    gameState.paddle1.x = CANVAS_WIDTH / 2 - PADDLE_WIDTH / 2;
    gameState.paddle2.x = CANVAS_WIDTH / 2 - PADDLE_WIDTH / 2;
    gameState.ball.x = CANVAS_WIDTH / 2;
    gameState.ball.y = CANVAS_HEIGHT / 2;
    gameState.ball.speedX = BALL_SPEED;
    gameState.ball.speedY = BALL_SPEED;
    gameState.paddle1.score = 0;
    gameState.paddle2.score = 0;
    updateScore();

    // Активация кнопок
    startButton.disabled = false;
    pauseButton.disabled = true;
    gameState.gameActive = false;
}

// Обновление счета
function updateScore() {
    score1Element.textContent = gameState.paddle1.score;
    score2Element.textContent = gameState.paddle2.score;
}

// Отрисовка игры
function draw() {
    // Очистка canvas
    gameState.ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    // Отрисовка центральной линии
    gameState.ctx.setLineDash([5, 5]);
    gameState.ctx.beginPath();
    gameState.ctx.moveTo(0, CANVAS_HEIGHT / 2);
    gameState.ctx.lineTo(CANVAS_WIDTH, CANVAS_HEIGHT / 2);
    gameState.ctx.strokeStyle = '#95a5a6';
    gameState.ctx.stroke();
    gameState.ctx.setLineDash([]);

    // Отрисовка платформ
    gameState.ctx.fillStyle = gameState.paddle1.color;
    gameState.ctx.fillRect(
        gameState.paddle1.x,
        gameState.paddle1.y,
        gameState.paddle1.width,
        gameState.paddle1.height
    );

    gameState.ctx.fillStyle = gameState.paddle2.color;
    gameState.ctx.fillRect(
        gameState.paddle2.x,
        gameState.paddle2.y,
        gameState.paddle2.width,
        gameState.paddle2.height
    );

    // Отрисовка мяча
    gameState.ctx.fillStyle = gameState.ball.color;
    gameState.ctx.beginPath();
    gameState.ctx.arc(
        gameState.ball.x,
        gameState.ball.y,
        gameState.ball.size,
        0,
        Math.PI * 2
    );
    gameState.ctx.fill();
}

// Обновление состояния игры
function update() {
    if (!gameState.gameActive) return;

    // Обновление позиции мяча
    gameState.ball.x += gameState.ball.speedX;
    gameState.ball.y += gameState.ball.speedY;

    // Отскок от стен
    if (gameState.ball.x <= gameState.ball.size || gameState.ball.x >= CANVAS_WIDTH - gameState.ball.size) {
        gameState.ball.speedX = -gameState.ball.speedX;
    }

    // Проверка столкновения с платформами
    if (
        gameState.ball.y - gameState.ball.size <= gameState.paddle1.y + gameState.paddle1.height &&
        gameState.ball.x >= gameState.paddle1.x &&
        gameState.ball.x <= gameState.paddle1.x + gameState.paddle1.width
    ) {
        gameState.ball.speedY = Math.abs(gameState.ball.speedY);
        gameState.paddle1.score++;
        updateScore();
    }

    if (
        gameState.ball.y + gameState.ball.size >= gameState.paddle2.y &&
        gameState.ball.x >= gameState.paddle2.x &&
        gameState.ball.x <= gameState.paddle2.x + gameState.paddle2.width
    ) {
        gameState.ball.speedY = -Math.abs(gameState.ball.speedY);
        gameState.paddle2.score++;
        updateScore();
    }

    // Проверка гола
    if (gameState.ball.y <= 0) {
        gameState.paddle2.score++;
        updateScore();
        resetBall();
    }

    if (gameState.ball.y >= CANVAS_HEIGHT) {
        gameState.paddle1.score++;
        updateScore();
        resetBall();
    }
}

// Сброс мяча
function resetBall() {
    gameState.ball.x = CANVAS_WIDTH / 2;
    gameState.ball.y = CANVAS_HEIGHT / 2;
    gameState.ball.speedX = BALL_SPEED * (Math.random() > 0.5 ? 1 : -1);
    gameState.ball.speedY = BALL_SPEED * (Math.random() > 0.5 ? 1 : -1);
}

// Игровой цикл
function gameLoop() {
    update();
    draw();
    gameState.animationFrame = requestAnimationFrame(gameLoop);
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
    cancelAnimationFrame(gameState.animationFrame);
    
    finalScore1Element.textContent = gameState.paddle1.score;
    finalScore2Element.textContent = gameState.paddle2.score;
    modal.style.display = 'flex';
}

// Обработка движения платформ
function handlePaddleMove(e, paddle) {
    if (!gameState.gameActive) return;

    const touch = e.touches ? e.touches[0] : e;
    const rect = canvas.getBoundingClientRect();
    const x = touch.clientX - rect.left;

    paddle.x = Math.max(0, Math.min(CANVAS_WIDTH - PADDLE_WIDTH, x - PADDLE_WIDTH / 2));
}

// Обработчики событий
canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const y = e.clientY - rect.top;
    
    if (y < CANVAS_HEIGHT / 2) {
        handlePaddleMove(e, gameState.paddle1);
    } else {
        handlePaddleMove(e, gameState.paddle2);
    }
});

canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const y = e.touches[0].clientY - rect.top;
    
    if (y < CANVAS_HEIGHT / 2) {
        handlePaddleMove(e, gameState.paddle1);
    } else {
        handlePaddleMove(e, gameState.paddle2);
    }
}, { passive: false });

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
tg.ready(); 