# ============================================================
# main.py — Основной файл запуска Flask-приложения
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from functools import wraps

from config import SECRET_KEY, DEBUG, POSITIONS, SEMESTERS, DEPARTMENT_NAME
from database import init_db
import teachers as tch
import subjects as sub
import workload  as wld
import reports   as rep
import auth      as au
from utils import workload_status

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ── Flask-Login ──────────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view             = "login"
login_manager.login_message          = "Пожалуйста, войдите в систему."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return au.get_user_by_id(int(user_id))

# ── Инициализация БД при старте ─────────────────────────────
with app.app_context():
    init_db()
    au.ensure_default_admin()


# ── Декоратор: только admin ──────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Доступ запрещён. Требуются права администратора.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# ── Декоратор: admin или editor ──────────────────────────────
def editor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_edit():
            flash("Доступ запрещён. Требуются права редактора.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# ════════════════════════════════════════════════════════════
# ВХОД / ВЫХОД
# ════════════════════════════════════════════════════════════
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))
        user = au.verify_password(username, password)
        if user:
            login_user(user, remember=remember)
            flash(f"Добро пожаловать, {user.full_name}!", "success")
            return redirect(request.args.get("next") or url_for("index"))
        flash("Неверный логин или пароль.", "danger")
    return render_template("login.html", dept=DEPARTMENT_NAME)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("login"))


# ════════════════════════════════════════════════════════════
# ГЛАВНАЯ СТРАНИЦА
# ════════════════════════════════════════════════════════════
@app.route("/")
@login_required
def index():
    teachers_summary = tch.get_teachers_with_workload_summary()
    stats            = wld.get_workload_stats()
    overloaded       = rep.report_overloaded_teachers()
    data = []
    for t in teachers_summary:
        row = dict(t)
        row["status"] = workload_status(row["total_hours"], row["max_workload"])
        data.append(row)
    return render_template("index.html", teachers=data, stats=stats,
                           overloaded_count=len(overloaded), dept=DEPARTMENT_NAME)


# ════════════════════════════════════════════════════════════
# ПРЕПОДАВАТЕЛИ
# ════════════════════════════════════════════════════════════
@app.route("/teachers")
@login_required
def teachers_list():
    return render_template("teachers.html", teachers=tch.get_all_teachers(),
                           positions=POSITIONS, dept=DEPARTMENT_NAME)


@app.route("/teachers/add", methods=["GET", "POST"])
@login_required
@editor_required
def teacher_add():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        position  = request.form.get("position", "")
        email     = request.form.get("email", "").strip()
        if not full_name or not position:
            flash("Заполните обязательные поля.", "danger")
        else:
            try:
                tch.add_teacher(full_name, position,
                                int(request.form.get("max_workload", 900)), email)
                flash(f"Преподаватель «{full_name}» добавлен.", "success")
                return redirect(url_for("teachers_list"))
            except ValueError:
                flash("Ошибка в данных формы.", "danger")
    from config import POSITION_MAX_WORKLOAD
    return render_template("teacher_form.html", action="add", teacher=None,
                           positions=POSITIONS, position_workloads=POSITION_MAX_WORKLOAD,
                           dept=DEPARTMENT_NAME)


@app.route("/teachers/edit/<int:tid>", methods=["GET", "POST"])
@login_required
@editor_required
def teacher_edit(tid):
    teacher = tch.get_teacher_by_id(tid)
    if not teacher:
        flash("Преподаватель не найден.", "danger")
        return redirect(url_for("teachers_list"))
    if request.method == "POST":
        try:
            tch.update_teacher(tid,
                request.form.get("full_name", "").strip(),
                request.form.get("position", ""),
                int(request.form.get("max_workload", 900)),
                request.form.get("email", "").strip())
            flash("Данные обновлены.", "success")
            return redirect(url_for("teachers_list"))
        except ValueError:
            flash("Ошибка в данных формы.", "danger")
    from config import POSITION_MAX_WORKLOAD
    return render_template("teacher_form.html", action="edit", teacher=dict(teacher),
                           positions=POSITIONS, position_workloads=POSITION_MAX_WORKLOAD,
                           dept=DEPARTMENT_NAME)


@app.route("/teachers/delete/<int:tid>", methods=["POST"])
@login_required
@editor_required
def teacher_delete(tid):
    t = tch.get_teacher_by_id(tid)
    if t:
        tch.delete_teacher(tid)
        flash(f"Преподаватель «{t['full_name']}» удалён.", "warning")
    return redirect(url_for("teachers_list"))


# ════════════════════════════════════════════════════════════
# ДИСЦИПЛИНЫ
# ════════════════════════════════════════════════════════════
@app.route("/subjects")
@login_required
def subjects_list():
    return render_template("subjects.html", subjects=sub.get_all_subjects(),
                           dept=DEPARTMENT_NAME)


@app.route("/subjects/add", methods=["GET", "POST"])
@login_required
@editor_required
def subject_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Введите название дисциплины.", "danger")
        else:
            try:
                sub.add_subject(name, request.form.get("code","").strip(),
                                request.form.get("description","").strip())
                flash(f"Дисциплина «{name}» добавлена.", "success")
                return redirect(url_for("subjects_list"))
            except ValueError as e:
                flash(str(e), "danger")
    return render_template("subject_form.html", action="add", subject=None, dept=DEPARTMENT_NAME)


@app.route("/subjects/edit/<int:sid>", methods=["GET", "POST"])
@login_required
@editor_required
def subject_edit(sid):
    subject = sub.get_subject_by_id(sid)
    if not subject:
        flash("Дисциплина не найдена.", "danger")
        return redirect(url_for("subjects_list"))
    if request.method == "POST":
        sub.update_subject(sid, request.form.get("name","").strip(),
                           request.form.get("code","").strip(),
                           request.form.get("description","").strip())
        flash("Дисциплина обновлена.", "success")
        return redirect(url_for("subjects_list"))
    return render_template("subject_form.html", action="edit",
                           subject=dict(subject), dept=DEPARTMENT_NAME)


@app.route("/subjects/delete/<int:sid>", methods=["POST"])
@login_required
@editor_required
def subject_delete(sid):
    s = sub.get_subject_by_id(sid)
    if s:
        sub.delete_subject(sid)
        flash(f"Дисциплина «{s['name']}» удалена.", "warning")
    return redirect(url_for("subjects_list"))


# ════════════════════════════════════════════════════════════
# УЧЕБНАЯ НАГРУЗКА
# ════════════════════════════════════════════════════════════
@app.route("/workload")
@login_required
def workload_list():
    return render_template("workload.html", entries=wld.get_all_workload(),
                           dept=DEPARTMENT_NAME)


@app.route("/workload/add", methods=["GET", "POST"])
@login_required
@editor_required
def workload_add():
    if request.method == "POST":
        try:
            wld.assign_workload(
                int(request.form["teacher_id"]), int(request.form["subject_id"]),
                int(request.form.get("lecture_hours",  0) or 0),
                int(request.form.get("practice_hours", 0) or 0),
                int(request.form.get("lab_hours",      0) or 0),
                int(request.form.get("semester", 1)),
                request.form.get("academic_year", "2024-2025").strip())
            flash("Нагрузка назначена.", "success")
            return redirect(url_for("workload_list"))
        except Exception as e:
            flash(f"Ошибка: {e}", "danger")
    return render_template("workload_form.html", action="add", entry=None,
                           teachers=tch.get_all_teachers(), subjects=sub.get_all_subjects(),
                           semesters=SEMESTERS, dept=DEPARTMENT_NAME)


@app.route("/workload/edit/<int:wid>", methods=["GET", "POST"])
@login_required
@editor_required
def workload_edit(wid):
    entry = wld.get_workload_entry(wid)
    if not entry:
        flash("Запись не найдена.", "danger")
        return redirect(url_for("workload_list"))
    if request.method == "POST":
        try:
            wld.update_workload(wid,
                int(request.form.get("lecture_hours",  0) or 0),
                int(request.form.get("practice_hours", 0) or 0),
                int(request.form.get("lab_hours",      0) or 0),
                int(request.form.get("semester", 1)),
                request.form.get("academic_year", "2024-2025").strip())
            flash("Нагрузка обновлена.", "success")
            return redirect(url_for("workload_list"))
        except Exception as e:
            flash(f"Ошибка: {e}", "danger")
    return render_template("workload_form.html", action="edit", entry=dict(entry),
                           teachers=tch.get_all_teachers(), subjects=sub.get_all_subjects(),
                           semesters=SEMESTERS, dept=DEPARTMENT_NAME)


@app.route("/workload/delete/<int:wid>", methods=["POST"])
@login_required
@editor_required
def workload_delete(wid):
    wld.delete_workload(wid)
    flash("Запись удалена.", "warning")
    return redirect(url_for("workload_list"))


@app.route("/workload/teacher/<int:tid>")
@login_required
def workload_teacher(tid):
    teacher = tch.get_teacher_by_id(tid)
    if not teacher:
        flash("Преподаватель не найден.", "danger")
        return redirect(url_for("workload_list"))
    entries     = wld.get_workload_by_teacher(tid)
    total_hours = wld.get_teacher_total_hours(tid)
    status      = workload_status(total_hours, teacher["max_workload"])
    return render_template("workload_teacher.html", teacher=dict(teacher),
                           entries=entries, total_hours=total_hours,
                           status=status, dept=DEPARTMENT_NAME)


# ════════════════════════════════════════════════════════════
# ОТЧЁТЫ
# ════════════════════════════════════════════════════════════
@app.route("/reports")
@login_required
def reports_page():
    semester = request.args.get("semester", type=int)
    return render_template("reports.html",
                           all_teachers    = rep.report_all_teachers(),
                           overloaded      = rep.report_overloaded_teachers(),
                           underloaded     = rep.report_underloaded_teachers(),
                           subjects_report = rep.report_subjects_summary(),
                           semester_data   = rep.report_by_semester(semester) if semester else [],
                           selected_sem    = semester,
                           semesters       = SEMESTERS, dept=DEPARTMENT_NAME)


# ════════════════════════════════════════════════════════════
# УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (только admin)
# ════════════════════════════════════════════════════════════
@app.route("/users")
@login_required
@admin_required
def users_list():
    return render_template("users.html", users=au.get_all_users(),
                           roles=au.ROLES, dept=DEPARTMENT_NAME)


@app.route("/users/add", methods=["GET", "POST"])
@login_required
@admin_required
def user_add():
    if request.method == "POST":
        username  = request.form.get("username", "").strip()
        password  = request.form.get("password", "").strip()
        full_name = request.form.get("full_name", "").strip()
        role      = request.form.get("role", "viewer")
        if not username or not password or not full_name:
            flash("Заполните все обязательные поля.", "danger")
        elif len(password) < 6:
            flash("Пароль должен содержать минимум 6 символов.", "danger")
        else:
            try:
                au.create_user(username, password, full_name, role)
                flash(f"Пользователь «{username}» создан.", "success")
                return redirect(url_for("users_list"))
            except ValueError as e:
                flash(str(e), "danger")
    return render_template("user_form.html", action="add", user=None,
                           roles=au.ROLES, dept=DEPARTMENT_NAME)


@app.route("/users/edit/<int:uid>", methods=["GET", "POST"])
@login_required
@admin_required
def user_edit(uid):
    users  = au.get_all_users()
    user   = next((u for u in users if u["id"] == uid), None)
    if not user:
        flash("Пользователь не найден.", "danger")
        return redirect(url_for("users_list"))
    if request.method == "POST":
        full_name    = request.form.get("full_name", "").strip()
        role         = request.form.get("role", "viewer")
        is_active    = bool(request.form.get("is_active"))
        new_password = request.form.get("new_password", "").strip()
        if new_password and len(new_password) < 6:
            flash("Пароль должен содержать минимум 6 символов.", "danger")
        else:
            try:
                au.update_user(uid, full_name, role, is_active, new_password)
                flash("Данные пользователя обновлены.", "success")
                return redirect(url_for("users_list"))
            except ValueError as e:
                flash(str(e), "danger")
    return render_template("user_form.html", action="edit", user=user,
                           roles=au.ROLES, dept=DEPARTMENT_NAME)


@app.route("/users/delete/<int:uid>", methods=["POST"])
@login_required
@admin_required
def user_delete(uid):
    if uid == current_user.id:
        flash("Нельзя удалить собственную учётную запись.", "danger")
        return redirect(url_for("users_list"))
    try:
        au.delete_user(uid)
        flash("Пользователь удалён.", "warning")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("users_list"))


# ── Профиль / смена пароля ───────────────────────────────────
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        old_pw  = request.form.get("old_password", "")
        new_pw  = request.form.get("new_password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()
        from werkzeug.security import check_password_hash
        row = au.get_user_by_username(current_user.username)
        if not check_password_hash(row["password_hash"], old_pw):
            flash("Текущий пароль неверен.", "danger")
        elif new_pw != confirm:
            flash("Новые пароли не совпадают.", "danger")
        elif len(new_pw) < 6:
            flash("Пароль должен быть не короче 6 символов.", "danger")
        else:
            au.update_user(current_user.id, current_user.full_name,
                           current_user.role, True, new_pw)
            flash("Пароль изменён успешно.", "success")
            return redirect(url_for("index"))
    return render_template("profile.html", dept=DEPARTMENT_NAME)


# ════════════════════════════════════════════════════════════
# ЗАПУСК
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{'='*55}")
    print(f"  {DEPARTMENT_NAME}")
    print(f"  Система управления учебной нагрузкой")
    print(f"{'='*55}")
    print(f"  Откройте браузер: http://127.0.0.1:5000")
    print(f"  Логин по умолчанию: admin / admin1234")
    print(f"{'='*55}\n")
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)