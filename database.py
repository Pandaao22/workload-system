import sqlite3
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")   # включаем поддержку FK
    return conn


def init_db():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name    TEXT    NOT NULL,          -- ФИО
            position     TEXT    NOT NULL,          -- Должность
            max_workload INTEGER NOT NULL DEFAULT 900, -- Макс. нагрузка (часов/год)
            email        TEXT,                      -- Email (опционально)
            created_at   TEXT    DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,    -- Название дисциплины
            code        TEXT,                       -- Код дисциплины (напр. CS401)
            description TEXT,                       -- Краткое описание
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workload (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id      INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
            subject_id      INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
            lecture_hours   INTEGER NOT NULL DEFAULT 0,   -- Лекционные часы
            practice_hours  INTEGER NOT NULL DEFAULT 0,   -- Практические часы
            lab_hours       INTEGER NOT NULL DEFAULT 0,   -- Лабораторные часы
            semester        INTEGER NOT NULL DEFAULT 1,   -- Семестр (1 или 2)
            academic_year   TEXT    NOT NULL DEFAULT '2024-2025',
            created_at      TEXT    DEFAULT (datetime('now')),
            UNIQUE(teacher_id, subject_id, semester, academic_year)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,       -- Логин (строчные)
            password_hash TEXT    NOT NULL,              -- Хэш пароля (werkzeug)
            full_name     TEXT    NOT NULL,              -- ФИО / отображаемое имя
            role          TEXT    NOT NULL DEFAULT 'viewer', -- admin|editor|viewer
            is_active     INTEGER NOT NULL DEFAULT 1,    -- 1=активен, 0=заблокирован
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] База данных инициализирована успешно.")