from database import get_connection


def get_all_teachers() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM teachers ORDER BY full_name"
    ).fetchall()
    conn.close()
    return rows


def get_teacher_by_id(teacher_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM teachers WHERE id = ?", (teacher_id,)
    ).fetchone()
    conn.close()
    return row


def add_teacher(full_name: str, position: str, max_workload: int, email: str = "") -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO teachers (full_name, position, max_workload, email)
           VALUES (?, ?, ?, ?)""",
        (full_name.strip(), position, max_workload, email.strip())
    )
    conn.commit()
    teacher_id = cur.lastrowid
    conn.close()
    return teacher_id


def update_teacher(teacher_id: int, full_name: str, position: str,
                   max_workload: int, email: str = "") -> bool:
    conn = get_connection()
    cur = conn.execute(
        """UPDATE teachers
           SET full_name = ?, position = ?, max_workload = ?, email = ?
           WHERE id = ?""",
        (full_name.strip(), position, max_workload, email.strip(), teacher_id)
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def delete_teacher(teacher_id: int) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def get_teachers_with_workload_summary() -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            t.id,
            t.full_name,
            t.position,
            t.max_workload,
            t.email,
            COALESCE(SUM(w.lecture_hours + w.practice_hours + w.lab_hours), 0) AS total_hours
        FROM teachers t
        LEFT JOIN workload w ON w.teacher_id = t.id
        GROUP BY t.id
        ORDER BY t.full_name
    """).fetchall()
    conn.close()
    return rows