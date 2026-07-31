// StreamDeck STM32 BluePill Classroom Simulator Engine

// Stream Deck Button Configuration mapping F13..F21 (0x68 to 0x70)
const DECK_BUTTONS = [
  { id: 0, key: 'F13', numKey: '1', hex: '0x68', label: 'Soundboard SFX', icon: '🔊', row: 0, col: 0, rowPin: 'PA1', colPin: 'PA4' },
  { id: 1, key: 'F14', numKey: '2', hex: '0x69', label: 'Mudo / On-Air', icon: '🎙️', row: 0, col: 1, rowPin: 'PA1', colPin: 'PA5' },
  { id: 2, key: 'F15', numKey: '3', hex: '0x6A', label: 'Alternar Cena', icon: '🎬', row: 0, col: 2, rowPin: 'PA1', colPin: 'PA6' },
  { id: 3, key: 'F16', numKey: '4', hex: '0x6B', label: 'Cronômetro', icon: '⏱️', row: 1, col: 0, rowPin: 'PA2', colPin: 'PA4' },
  { id: 4, key: 'F17', numKey: '5', hex: '0x6C', label: 'Alerta Sala', icon: '🔔', row: 1, col: 1, rowPin: 'PA2', colPin: 'PA5' },
  { id: 5, key: 'F18', numKey: '6', hex: '0x6D', label: 'Efeitos LED', icon: '💡', row: 1, col: 2, rowPin: 'PA2', colPin: 'PA6' },
  { id: 6, key: 'F19', numKey: '7', hex: '0x6E', label: 'Diagrama STM32', icon: '⚡', row: 2, col: 0, rowPin: 'PA3', colPin: 'PA4' },
  { id: 7, key: 'F20', numKey: '8', hex: '0x6F', label: 'Meme Embarcados', icon: '🤖', row: 2, col: 1, rowPin: 'PA3', colPin: 'PA5' },
  { id: 8, key: 'F21', numKey: '9', hex: '0x70', label: 'Celebração', icon: '🎉', row: 2, col: 2, rowPin: 'PA3', colPin: 'PA6' }
];

// App State
let state = {
  isMicMuted: false,
  timerRunning: false,
  timerMs: 0,
  timerInterval: null,
  activeSceneIndex: 0,
  audioCtx: null,
  sfxIndex: 0,
  memeIndex: 0,
  profMode: false,
  bounceCount: 0,
  validCount: 0,
  scopePulseTimer: 0
};

// Memes for Button 8 (F20)
const EMBEDDED_MEMES = [
  "\"Compilou sem warnings na primeira tentativa... Deve ter algo muito errado!\"",
  "\"Por que usar um botão comum se você pode configurar 32 registradores e uma matriz 3x3 no STM32?\"",
  "\"Ponteiros em C não são assustadores... até você esquecer de inicializar e tomar um HardFault Exception!\"",
  "\"Quando o debounce por código funciona perfeitamente de primeira: 🧙‍♂️ Mágica!\"",
  "\"STM32 BluePill: R$ 25,00. Orgulho de fazer um StreamDeck próprio: Não tem preço!\""
];

// Web Audio API Synthesizer (No external MP3 files needed!)
function initAudio() {
  if (!state.audioCtx) {
    state.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
}

function playSynthesizedSound(type) {
  initAudio();
  const ctx = state.audioCtx;
  if (!ctx) return;

  const now = ctx.currentTime;

  if (type === 'beep') {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, now);
    gain.gain.setValueAtTime(0.3, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.15);
  } else if (type === 'chime') {
    [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, now + idx * 0.08);
      gain.gain.setValueAtTime(0.3, now + idx * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.4);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + idx * 0.08);
      osc.stop(now + idx * 0.08 + 0.4);
    });
  } else if (type === 'fanfare') {
    const notes = [440, 554.37, 659.25, 880];
    notes.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(freq, now + idx * 0.12);
      gain.gain.setValueAtTime(0.2, now + idx * 0.12);
      gain.gain.exponentialRampToValueAtTime(0.01, now + idx * 0.12 + 0.5);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + idx * 0.12);
      osc.stop(now + idx * 0.12 + 0.5);
    });
  } else if (type === 'buzzer') {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(150, now);
    gain.gain.setValueAtTime(0.4, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.3);
  }
}

// DOM Rendering
document.addEventListener('DOMContentLoaded', () => {
  renderMatrixGrid();
  setupKeyListeners();
  initScopeCanvas();
});

// Render 3x3 Matrix
function renderMatrixGrid() {
  const container = document.getElementById('matrix-grid');
  container.innerHTML = '';

  DECK_BUTTONS.forEach(btn => {
    const el = document.createElement('div');
    el.className = 'deck-btn';
    el.id = `deck-btn-${btn.id}`;
    el.innerHTML = `
      <div class="btn-header">
        <span class="btn-num">#${btn.id + 1}</span>
        <span class="btn-key-code">${btn.key}</span>
      </div>
      <div class="btn-icon">${btn.icon}</div>
      <div class="btn-sub">${btn.label}</div>
    `;
    el.addEventListener('click', () => triggerButtonAction(btn.id));
    container.appendChild(el);
  });
}

// Global Keydown Handler for F13..F21 & 1..9
function setupKeyListeners() {
  window.addEventListener('keydown', (e) => {
    let matchedBtn = null;
    
    DECK_BUTTONS.forEach(b => {
      if (e.key === b.key || e.code === b.key || e.key === b.numKey) {
        matchedBtn = b;
      }
    });

    if (matchedBtn) {
      e.preventDefault();
      triggerButtonAction(matchedBtn.id);
    }
  });
}

// Toggle Technical Analysis Mode
function toggleProfMode() {
  state.profMode = !state.profMode;
  const btn = document.getElementById('btn-toggle-prof');

  if (state.profMode) {
    btn.classList.add('active-prof');
    showStageScreen('screen-prof-deepdive', '🔬 Análise Técnica');
  } else {
    btn.classList.remove('active-prof');
    showStageScreen('screen-main', 'Apresentação');
  }
}

// Action Dispatcher
function triggerButtonAction(id) {
  const btn = DECK_BUTTONS[id];
  const startTime = performance.now();

  // Update Debounce & Telemetry Counters
  state.validCount++;
  state.bounceCount += Math.floor(Math.random() * 4) + 2;

  document.getElementById('stat-bounces').textContent = state.bounceCount;
  document.getElementById('stat-valid').textContent = state.validCount;

  // Highlight visual button & update Scope Waveform
  highlightVisualButton(id);
  updatePinTelemetry(btn);
  updateUsbInspector(btn.hex);
  triggerScopePulse();

  // If in Technical Analysis mode, keep screen active
  if (state.profMode) {
    playSynthesizedSound('beep');
  } else {
    // Execute Action for regular mode
    switch (id) {
      case 0: handleSoundboard(); break;
      case 1: handleMicToggle(); break;
      case 2: handleSceneSwitch(); break;
      case 3: handleTimerToggle(); break;
      case 4: handleClassroomAlert(); break;
      case 5: handleLedTheme(); break;
      case 6: showStageScreen('screen-stm32', 'Diagrama STM32 BluePill'); playSynthesizedSound('beep'); break;
      case 7: handleMeme(); break;
      case 8: handleCelebration(); break;
    }
  }

  // Calculate Latency
  const latency = (performance.now() - startTime).toFixed(1);
  document.getElementById('status-latency').textContent = `${latency} ms`;
  document.getElementById('status-last-key').textContent = `${btn.key} (${btn.hex})`;
  document.getElementById('hex-code').textContent = btn.hex;
  document.getElementById('log-content').textContent = `[EVENT] Tecla ${btn.key} (${btn.label}) acionada. GPIO: ${btn.rowPin} (GND) -> ${btn.colPin} (RESET).`;
}

// USB HID Inspector Update
function updateUsbInspector(hexVal) {
  const b2 = document.getElementById('b2-val');
  if (b2) b2.textContent = hexVal;
}

// Logic Analyzer Canvas Oscilloscope Simulator
let scopeCtx = null;
let scopeWidth = 450;
let scopeHeight = 120;

function initScopeCanvas() {
  const canvas = document.getElementById('scope-canvas');
  if (!canvas) return;
  scopeCtx = canvas.getContext('2d');
  scopeWidth = canvas.width;
  scopeHeight = canvas.height;
  drawScopeLoop();
}

function triggerScopePulse() {
  state.scopePulseTimer = 25; // 25 frames pulse
}

function drawScopeLoop() {
  if (scopeCtx) {
    scopeCtx.fillStyle = '#05070a';
    scopeCtx.fillRect(0, 0, scopeWidth, scopeHeight);

    // Draw Grid lines
    scopeCtx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    scopeCtx.lineWidth = 1;
    for (let x = 0; x < scopeWidth; x += 30) {
      scopeCtx.beginPath();
      scopeCtx.moveTo(x, 0);
      scopeCtx.lineTo(x, scopeHeight);
      scopeCtx.stroke();
    }
    for (let y = 0; y < scopeHeight; y += 20) {
      scopeCtx.beginPath();
      scopeCtx.moveTo(0, y);
      scopeCtx.lineTo(scopeWidth, y);
      scopeCtx.stroke();
    }

    // Row Line Wave (Pink)
    const isPulsing = state.scopePulseTimer > 0;
    if (isPulsing) state.scopePulseTimer--;

    scopeCtx.strokeStyle = '#ff0844';
    scopeCtx.lineWidth = 2;
    scopeCtx.beginPath();
    scopeCtx.moveTo(0, 35);
    scopeCtx.lineTo(150, 35);
    scopeCtx.lineTo(150, isPulsing ? 60 : 35);
    scopeCtx.lineTo(300, isPulsing ? 60 : 35);
    scopeCtx.lineTo(300, 35);
    scopeCtx.lineTo(scopeWidth, 35);
    scopeCtx.stroke();

    // Col Line Wave (Green)
    scopeCtx.strokeStyle = '#00e676';
    scopeCtx.lineWidth = 2;
    scopeCtx.beginPath();
    scopeCtx.moveTo(0, 85);
    scopeCtx.lineTo(160, 85);
    scopeCtx.lineTo(160, isPulsing ? 105 : 85);
    scopeCtx.lineTo(290, isPulsing ? 105 : 85);
    scopeCtx.lineTo(290, 85);
    scopeCtx.lineTo(scopeWidth, 85);
    scopeCtx.stroke();
  }

  requestAnimationFrame(drawScopeLoop);
}

// Highlight Button UI
function highlightVisualButton(id) {
  const el = document.getElementById(`deck-btn-${id}`);
  if (el) {
    el.classList.add('active');
    setTimeout(() => el.classList.remove('active'), 250);
  }
}

// Pin Telemetry Visualizer
function updatePinTelemetry(btn) {
  document.querySelectorAll('.pin-tag').forEach(p => {
    p.classList.remove('active-row', 'active-col');
  });

  const rowEl = document.getElementById(`pin-${btn.rowPin.toLowerCase()}`);
  const colEl = document.getElementById(`pin-${btn.colPin.toLowerCase()}`);

  if (rowEl) rowEl.classList.add('active-row');
  if (colEl) colEl.classList.add('active-col');
}

// Show specific Stage Screen
function showStageScreen(screenId, sceneName) {
  document.querySelectorAll('.stage-screen').forEach(s => s.classList.remove('active'));
  const target = document.getElementById(screenId);
  if (target) target.classList.add('active');

  document.getElementById('scene-tag').textContent = `Cena Ativa: ${sceneName}`;
}

// F13: Soundboard
function handleSoundboard() {
  const sfxList = ['chime', 'fanfare', 'buzzer', 'beep'];
  const soundName = sfxList[state.sfxIndex % sfxList.length];
  state.sfxIndex++;

  playSynthesizedSound(soundName);
  showStageScreen('screen-main', 'Soundboard SFX');
  document.getElementById('log-content').textContent = `[SFX] Reproduzindo efeito sonoro: ${soundName.toUpperCase()}`;
}

// F14: Mic Toggle
function handleMicToggle() {
  state.isMicMuted = !state.isMicMuted;
  showStageScreen('screen-mic', 'Estúdio de Áudio');

  const card = document.getElementById('mic-card');
  const icon = document.getElementById('mic-icon');
  const statusText = document.getElementById('mic-status-text');
  const subText = document.getElementById('mic-subtext');

  if (state.isMicMuted) {
    card.classList.add('muted');
    icon.textContent = '🔇';
    statusText.textContent = 'MICROFONE MUTADO';
    subText.textContent = 'Áudio desligado pelo Stream Deck (F14)';
    playSynthesizedSound('buzzer');
  } else {
    card.classList.remove('muted');
    icon.textContent = '🎙️';
    statusText.textContent = 'MICROFONE LIGADO (ON AIR)';
    subText.textContent = 'Transmitindo áudio para a sala de aula...';
    playSynthesizedSound('beep');
  }
}

// F15: Scene Switch
function handleSceneSwitch() {
  showStageScreen('screen-scenes', 'Alternador de Cenas');
  const scenes = ['sc-slide', 'sc-cam', 'sc-code'];
  state.activeSceneIndex = (state.activeSceneIndex + 1) % scenes.length;

  document.querySelectorAll('.scene-card').forEach(c => c.classList.remove('active'));
  document.getElementById(scenes[state.activeSceneIndex]).classList.add('active');

  playSynthesizedSound('beep');
}

// F16: Timer Toggle
function handleTimerToggle() {
  showStageScreen('screen-timer', 'Cronômetro Apresentação');

  if (state.timerRunning) {
    clearInterval(state.timerInterval);
    state.timerRunning = false;
    document.getElementById('timer-status').textContent = 'Pausado (Pressione F16 para retomar)';
    playSynthesizedSound('beep');
  } else {
    state.timerRunning = true;
    const startTimestamp = Date.now() - state.timerMs;
    document.getElementById('timer-status').textContent = '⏱️ Em Execução...';

    state.timerInterval = setInterval(() => {
      state.timerMs = Date.now() - startTimestamp;
      const totalSec = Math.floor(state.timerMs / 1000);
      const mins = String(Math.floor(totalSec / 60)).padStart(2, '0');
      const secs = String(totalSec % 60).padStart(2, '0');
      const ms = String(Math.floor((state.timerMs % 1000) / 100));

      document.getElementById('timer-display').textContent = `${mins}:${secs}.${ms}`;
    }, 100);

    playSynthesizedSound('chime');
  }
}

// F17: Classroom Alert
function handleClassroomAlert() {
  const modal = document.getElementById('alert-modal');
  modal.classList.toggle('active');
  playSynthesizedSound('buzzer');
}

function closeModal() {
  document.getElementById('alert-modal').classList.remove('active');
}

// F18: LED Theme Switcher
function handleLedTheme() {
  const themes = ['theme-cyberpunk', 'theme-neon', 'theme-clean'];
  const body = document.body;
  let currentThemeIndex = 0;

  themes.forEach((t, idx) => {
    if (body.classList.contains(t)) currentThemeIndex = idx;
  });

  body.className = themes[(currentThemeIndex + 1) % themes.length];
  playSynthesizedSound('chime');
  document.getElementById('log-content').textContent = `[LED] Alternado para tema visual: ${body.className}`;
}

// F20: Meme Generator
function handleMeme() {
  showStageScreen('screen-meme', 'Meme Embarcados');
  const quote = EMBEDDED_MEMES[state.memeIndex % EMBEDDED_MEMES.length];
  state.memeIndex++;

  document.querySelector('.meme-quote').textContent = quote;
  playSynthesizedSound('chime');
}

// F21: Celebration Confetti
function handleCelebration() {
  showStageScreen('screen-main', 'Encerramento & Vitória');
  playSynthesizedSound('fanfare');
  launchConfetti();
}

// Canvas Confetti Effect
function launchConfetti() {
  const canvas = document.getElementById('confetti-canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const particles = Array.from({ length: 120 }, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height - canvas.height,
    r: Math.random() * 6 + 4,
    d: Math.random() * 10 + 2,
    color: `hsl(${Math.random() * 360}, 100%, 50%)`,
    tilt: Math.random() * 10 - 10
  }));

  let animationFrame;
  let ticks = 0;

  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      ctx.beginPath();
      ctx.lineWidth = p.r;
      ctx.strokeStyle = p.color;
      ctx.moveTo(p.x + p.tilt + p.r / 2, p.y);
      ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 2);
      ctx.stroke();

      p.y += p.d;
      p.tilt += 0.1;

      if (p.y > canvas.height) {
        p.y = -20;
        p.x = Math.random() * canvas.width;
      }
    });

    ticks++;
    if (ticks < 200) {
      animationFrame = requestAnimationFrame(render);
    } else {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }

  render();
}
