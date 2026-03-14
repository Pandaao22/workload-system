/* ============================================================
   main.js — Основные скрипты системы управления нагрузкой
   ============================================================ */


/* ── Показать/скрыть пароль ──────────────────────────────── */
function togglePassword(inputId, iconId) {
  const input = document.getElementById(inputId);
  const icon  = document.getElementById(iconId);
  if (!input) return;

  if (input.type === 'password') {
    input.type   = 'text';
    icon.className = 'bi bi-eye-slash';
  } else {
    input.type   = 'password';
    icon.className = 'bi bi-eye';
  }
}


/* ── Проверка совпадения паролей (профиль) ───────────────── */
function checkPasswordMatch(newId, confirmId, hintId) {
  const np   = document.getElementById(newId);
  const cp   = document.getElementById(confirmId);
  const hint = document.getElementById(hintId);
  if (!np || !cp || !hint) return;

  cp.addEventListener('input', function () {
    if (cp.value.length === 0) {
      hint.style.display = 'none';
      return;
    }
    hint.style.display = 'block';
    if (np.value === cp.value) {
      hint.textContent = '✓ Пароли совпадают';
      hint.style.color = 'var(--clr-green)';
    } else {
      hint.textContent = '✗ Пароли не совпадают';
      hint.style.color = 'var(--clr-red)';
    }
  });
}


/* ── Автозаполнение макс. нагрузки по должности ─────────── */
function initPositionWorkload(selectId, inputId, workloads) {
  const select = document.getElementById(selectId);
  const input  = document.getElementById(inputId);
  if (!select || !input) return;

  select.addEventListener('change', function () {
    const pos = this.value;
    if (workloads[pos]) {
      input.value = workloads[pos];
    }
  });
}


/* ── Подтверждение удаления ──────────────────────────────── */
function confirmDelete(message) {
  return confirm(message || 'Вы уверены, что хотите удалить эту запись?');
}


/* ── Автоматически скрыть flash-уведомления через 5 сек ─── */
function initAutoHideAlerts(timeout) {
  setTimeout(function () {
    document.querySelectorAll('.alert.fade.show').forEach(function (el) {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    });
  }, timeout || 5000);
}


/* ── Инициализация при загрузке страницы ─────────────────── */
document.addEventListener('DOMContentLoaded', function () {

  // Автоскрытие уведомлений
  initAutoHideAlerts(5000);

  // Кнопка показа пароля на странице входа
  const loginPwd = document.getElementById('login-pwd');
  const loginEye = document.getElementById('login-eye');
  if (loginPwd && loginEye) {
    document.getElementById('login-eye-btn').addEventListener('click', function () {
      togglePassword('login-pwd', 'login-eye');
    });
  }

  // Проверка паролей на странице профиля
  checkPasswordMatch('new-pwd', 'confirm-pwd', 'match-hint');

  // Проверка паролей на форме нового пользователя
  checkPasswordMatch('new-password-input', 'confirm-password-input', 'password-match-hint');

});


/* ── Мобильный сайдбар ───────────────────────────────────── */
function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const icon    = document.getElementById('menu-icon');
  if (!sidebar) return;

  const isOpen = sidebar.classList.toggle('open');
  overlay.classList.toggle('active', isOpen);
  icon.className = isOpen ? 'bi bi-x' : 'bi bi-list';
}

function closeSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const icon    = document.getElementById('menu-icon');
  if (!sidebar) return;

  sidebar.classList.remove('open');
  overlay.classList.remove('active');
  if (icon) icon.className = 'bi bi-list';
}

/* Закрывать сайдбар при нажатии Escape */
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeSidebar();
});
const AI_STORAGE_KEY   = 'ai_chat_messages';
const AI_OPEN_KEY      = 'ai_chat_open';
const AI_HISTORY_KEY   = 'ai_chat_history';

let aiHistory = [];

/* Сохранить состояние в sessionStorage */
function aiSaveState() {
  const box  = document.getElementById('ai-messages');
  if (!box) return;
  const msgs = Array.from(box.querySelectorAll('.ai-msg')).map(el => ({
    html: el.innerHTML,
    cls:  el.className,
  }));
  sessionStorage.setItem(AI_STORAGE_KEY, JSON.stringify(msgs));
  sessionStorage.setItem(AI_HISTORY_KEY, JSON.stringify(aiHistory));
  sessionStorage.setItem(AI_OPEN_KEY,    document.getElementById('ai-panel')?.classList.contains('open') ? '1' : '0');
}

/* Восстановить состояние из sessionStorage */
function aiRestoreState() {
  const panel = document.getElementById('ai-panel');
  const box   = document.getElementById('ai-messages');
  const sugg  = document.getElementById('ai-suggestions');
  if (!panel || !box) return;

  /* История переписки */
  try {
    const saved = sessionStorage.getItem(AI_HISTORY_KEY);
    if (saved) aiHistory = JSON.parse(saved);
  } catch(e) { aiHistory = []; }

  /* Сообщения */
  try {
    const saved = sessionStorage.getItem(AI_STORAGE_KEY);
    if (saved) {
      const msgs = JSON.parse(saved);
      if (msgs.length > 0) {
        box.innerHTML = '';
        msgs.forEach(m => {
          const div = document.createElement('div');
          div.className = m.cls.replace(' typing', ''); /* убираем класс typing */
          div.innerHTML  = m.html;
          box.appendChild(div);
        });
        /* Скрыть подсказки если уже был диалог */
        if (sugg && msgs.length > 1) sugg.style.display = 'none';
      }
    }
  } catch(e) {}

  /* Открыт ли чат */
  if (sessionStorage.getItem(AI_OPEN_KEY) === '1') {
    panel.classList.add('open');
    setTimeout(() => {
      scrollAI();
      document.getElementById('ai-input')?.focus();
    }, 50);
  }
}

function toggleAI() {
  const panel = document.getElementById('ai-panel');
  const isOpen = panel.classList.toggle('open');
  if (isOpen) {
    setTimeout(() => {
      scrollAI();
      document.getElementById('ai-input').focus();
    }, 50);
  }
  aiSaveState();
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 100) + 'px';
}

function handleAIKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendAIMessage();
  }
}

function sendSuggestion(text) {
  const sugg = document.getElementById('ai-suggestions');
  if (sugg) sugg.style.display = 'none';
  document.getElementById('ai-input').value = text;
  sendAIMessage();
}

function scrollAI() {
  const box = document.getElementById('ai-messages');
  if (box) box.scrollTop = box.scrollHeight;
}

function addMsg(text, role) {
  const box = document.getElementById('ai-messages');
  const div = document.createElement('div');
  div.className = 'ai-msg ' + role;
  div.innerHTML = text.replace(/\n/g, '<br>');
  box.appendChild(div);
  scrollAI();
  return div;
}

async function sendAIMessage() {
  const input = document.getElementById('ai-input');
  const btn   = document.getElementById('ai-send');
  const text  = input.value.trim();
  if (!text) return;

  addMsg(text, 'user');
  aiHistory.push({ role: 'user', content: text });
  input.value = '';
  input.style.height = 'auto';
  btn.disabled = true;

  const typing = addMsg('ИИ думает...', 'bot typing');

  try {
    const resp = await fetch('/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history: aiHistory.slice(-10) })
    });
    const data  = await resp.json();
    const reply = data.reply || data.error || 'Ошибка ответа';
    typing.remove();
    addMsg(reply, 'bot');
    aiHistory.push({ role: 'assistant', content: reply });
  } catch (e) {
    typing.remove();
    addMsg('⚠️ Ошибка соединения с сервером', 'bot');
  } finally {
    btn.disabled = false;
    input.focus();
  }

  aiSaveState();
}

/* Инициализация виджета при загрузке страницы */
document.addEventListener('DOMContentLoaded', function () {
  aiRestoreState();
});

/* Сохранить перед уходом со страницы */
window.addEventListener('beforeunload', function () {
  aiSaveState();
});