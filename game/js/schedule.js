const WEEKDAY_SCHEDULE = [
    { start: '08:45', end: '10:05' },
    { start: '10:25', end: '11:45' },
    { start: '12:05', end: '13:25' },
    { start: '13:35', end: '14:55' }
];

const SATURDAY_SCHEDULE = [
    { start: '08:45', end: '10:00' },
    { start: '10:10', end: '11:25' },
    { start: '11:35', end: '12:50' },
    { start: '13:00', end: '14:15' }
];

// Переменная для отслеживания последнего состояния
let lastState = {
    wasInClass: false,
    lastPairEnd: null
};

function launchConfetti() {
    const duration = 1500;
    const end = Date.now() + duration;

    // Дублируем зеленый цвет для увеличения его вероятности появления
    const colors = ['#fb41a2', '#007fe0', '#01cb56', '#01cb56'];

    (function frame() {
        confetti({
            particleCount: 3,
            angle: 60,
            spread: 45,
            origin: { x: 0, y: 0.8 },
            colors: colors,
            gravity: 1.2,
            scalar: 1.2,
            ticks: 300
        });
        confetti({
            particleCount: 3,
            angle: 120,
            spread: 45,
            origin: { x: 1, y: 0.8 },
            colors: colors,
            gravity: 1.2,
            scalar: 1.2,
            ticks: 300
        });

        if (Date.now() < end) {
            setTimeout(frame, 100);
        }
    }());

    const progressBox = document.getElementById('progressBox');
    progressBox.classList.add('celebrate');
    setTimeout(() => {
        progressBox.classList.remove('celebrate');
    }, 500);
}

function formatTimeLeft(minutes, seconds = 0) {
    if (minutes < 2) {
        const totalSeconds = minutes * 60 + seconds;
        return `${totalSeconds} ${declOfNum(totalSeconds, ['секунда', 'секунды', 'секунд'])}`;
    }
    return `${minutes} ${declOfNum(minutes, ['минута', 'минуты', 'минут'])}`;
}

function declOfNum(n, titles) {
    return titles[n % 10 === 1 && n % 100 !== 11 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20) ? 1 : 2];
}

function updateSchedule() {
    const now = new Date();
    const isSaturday = now.getDay() === 6;

    // Обновляем расписание будних дней (всегда показываем будни в первой таблице)
    const bellList = document.querySelector('#bell_list .row-container');
    bellList.innerHTML = WEEKDAY_SCHEDULE.map((pair, index) => `
        <div class="row ${index < WEEKDAY_SCHEDULE.length - 1 ? 'notlast' : ''}">
            <div>${pair.start}</div>
            <div>${pair.end}</div>
        </div>
    `).join('');
    bellList.closest('.wrap.list').classList.toggle('active', !isSaturday);

    // Обновляем расписание субботы (всегда показываем субботу во второй таблице)
    const saturdayBellList = document.querySelector('#saturday_bell_list .row-container');
    saturdayBellList.innerHTML = SATURDAY_SCHEDULE.map((pair, index) => `
        <div class="row ${index < SATURDAY_SCHEDULE.length - 1 ? 'notlast' : ''}">
            <div>${pair.start}</div>
            <div>${pair.end}</div>
        </div>
    `).join('');
    saturdayBellList.closest('.wrap.list').classList.toggle('active', isSaturday);

    // Обновляем прогресс-бар с правильным расписанием
    updateProgressBar();
}

function updateProgressBar() {
    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();
    const currentSeconds = now.getSeconds();
    const isSaturday = now.getDay() === 6;
    const schedule = isSaturday ? SATURDAY_SCHEDULE : WEEKDAY_SCHEDULE;

    let currentPair = null;
    let progress = 100;
    let timerPassed = 'Приятного';
    let timerLeft = 'отдыха!';
    let isInClass = false;
    let isActive = false;

    // Находим текущую или следующую пару
    let currentOrNextPairIndex = -1;
    for (let i = 0; i < schedule.length; i++) {
        const pair = schedule[i];
        const [startHour, startMinute] = pair.start.split(':').map(Number);
        const [endHour, endMinute] = pair.end.split(':').map(Number);
        const startTime = startHour * 60 + startMinute;
        const endTime = endHour * 60 + endMinute;

        // Если сейчас идет пара
        if (currentTime >= startTime && currentTime < endTime) {
            currentPair = pair;
            const totalDuration = endTime - startTime;
            const elapsedTime = (currentTime - startTime) + (currentSeconds / 60);
            progress = (elapsedTime / totalDuration) * 100;
            
            const remainingMinutes = endTime - currentTime - 1;
            const remainingSeconds = 60 - currentSeconds;
            timerPassed = formatTimeLeft(remainingMinutes, remainingSeconds);
            timerLeft = 'до перемены';
            isActive = true;
            isInClass = true;
            currentOrNextPairIndex = i;
            break;
        }
        // Если пара еще не началась
        else if (currentTime < startTime) {
            currentOrNextPairIndex = i;
            break;
        }
    }

    // Проверяем, не закончилась ли только что пара
    if (!isActive && currentOrNextPairIndex >= 0) {
        const currentPairIndex = currentOrNextPairIndex > 0 ? currentOrNextPairIndex - 1 : -1;
        if (currentPairIndex >= 0) {
            const justEndedPair = schedule[currentPairIndex];
            const [endHour, endMinute] = justEndedPair.end.split(':').map(Number);
            const endTime = endHour * 60 + endMinute;
            
            if (currentTime === endTime && currentSeconds === 0 && lastState.wasInClass) {
                launchConfetti();
            }
        }
    }

    // Если не идет пара, проверяем следующую
    if (!isActive && currentOrNextPairIndex !== -1) {
        const nextPair = schedule[currentOrNextPairIndex];
        const [startHour, startMinute] = nextPair.start.split(':').map(Number);
        const startTime = startHour * 60 + startMinute;

        const remainingMinutes = startTime - currentTime - 1;
        const remainingSeconds = 60 - currentSeconds;
        
        // Проверяем, что время не отрицательное
        if (remainingMinutes >= 0 || (remainingMinutes === -1 && remainingSeconds > 0)) {
            timerPassed = formatTimeLeft(remainingMinutes, remainingSeconds);
            timerLeft = 'до пары';
            progress = 0;
            isActive = true;
        }
    }

    // Проверяем, закончилась ли последняя пара
    const lastPair = schedule[schedule.length - 1];
    const [lastEndHour, lastEndMinute] = lastPair.end.split(':').map(Number);
    const lastEndTime = lastEndHour * 60 + lastEndMinute;

    // Если текущее время после окончания последней пары или нет активных пар
    if (currentTime >= lastEndTime || !isActive) {
        progress = 100;
        timerPassed = 'Приятного';
        timerLeft = 'отдыха!';

        // Запускаем конфетти только в момент окончания последней пары
        if (lastState.wasInClass && currentTime === lastEndTime && currentSeconds === 0) {
            launchConfetti();
        }
    }

    // Обновляем состояние
    lastState.wasInClass = isInClass;
    lastState.lastPairEnd = currentPair ? currentPair.end : null;

    document.getElementById('timerPassed').textContent = timerPassed;
    document.getElementById('timerLeft').textContent = timerLeft;
    document.getElementById('progress_line').style.width = `${100 - Math.min(100, Math.max(0, progress))}%`;
}

// Функция для определения интервала обновления
function getUpdateInterval() {
    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();
    const currentSeconds = now.getSeconds();
    const isSaturday = now.getDay() === 6;
    const schedule = isSaturday ? SATURDAY_SCHEDULE : WEEKDAY_SCHEDULE;

    // Проверяем, близко ли время к началу или концу пары
    for (const pair of schedule) {
        const [startHour, startMinute] = pair.start.split(':').map(Number);
        const [endHour, endMinute] = pair.end.split(':').map(Number);
        const startTime = startHour * 60 + startMinute;
        const endTime = endHour * 60 + endMinute;

        // Рассчитываем время до начала и конца пары в минутах
        const timeToStart = startTime - currentTime;
        const timeToEnd = endTime - currentTime;

        // Если до начала или конца пары осталось меньше 5 минут
        if ((timeToStart >= -1 && timeToStart <= 5) || (timeToEnd >= -1 && timeToEnd <= 5)) {
            return 100; // Обновляем каждые 100мс для плавности
        }
    }

    // В остальных случаях обновляем каждую секунду
    return 1000;
}

// Функция для управления интервалом обновления
let updateTimer = null;
function startDynamicUpdate() {
    if (updateTimer) {
        clearTimeout(updateTimer);
    }
    
    updateProgressBar();
    const interval = getUpdateInterval();
    updateTimer = setTimeout(startDynamicUpdate, interval);
}

// Запускаем обновление расписания
updateSchedule();
// Запускаем динамическое обновление времени
startDynamicUpdate();

// Обновляем расписание каждую минуту
setInterval(updateSchedule, 60000); 