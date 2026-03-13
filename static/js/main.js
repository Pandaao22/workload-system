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