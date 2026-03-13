
from database import get_connection


def get_all_subjects() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM subjects ORDER BY name"
    ).fetchall()
    conn.close()
    return rows


def get_subject_by_id(subject_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM subjects WHERE id = ?", (subject_id,)
    ).fetchone()
    conn.close()
    return row


def add_subject(name: str, code: str = "", description: str = "") -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO subjects (name, code, description) VALUES (?, ?, ?)",
            (name.strip(), code.strip(), description.strip())
        )
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        conn.close()
        raise ValueError(f"Дисциплина «{name}» уже существует.") from e
    finally:
        conn.close()


def update_subject(subject_id: int, name: str, code: str = "", description: str = "") -> bool:
    conn = get_connection()
    cur = conn.execute(
        """UPDATE subjects SET name = ?, code = ?, description = ?
           WHERE id = ?""",
        (name.strip(), code.strip(), description.strip(), subject_id)
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def delete_subject(subject_id: int) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted