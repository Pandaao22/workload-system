
from database import get_connection
from utils import workload_status


def report_all_teachers() -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            t.id,
            t.full_name,
            t.position,
            t.max_workload,
            t.email,
            COALESCE(SUM(w.lecture_hours), 0)  AS total_lecture,
            COALESCE(SUM(w.practice_hours), 0) AS total_practice,
            COALESCE(SUM(w.lab_hours), 0)      AS total_lab,
            COALESCE(SUM(w.lecture_hours + w.practice_hours + w.lab_hours), 0) AS total_hours
        FROM teachers t
        LEFT JOIN workload w ON w.teacher_id = t.id
        GROUP BY t.id
        ORDER BY t.full_name
    """).fetchall()
    conn.close()

    result = []
    for r in rows:
        rec = dict(r)
        rec["status"] = workload_status(rec["total_hours"], rec["max_workload"])
        result.append(rec)
    return result


def report_by_semester(semester: int) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            t.full_name      AS teacher_name,
            t.position,
            s.name           AS subject_name,
            s.code           AS subject_code,
            w.lecture_hours,
            w.practice_hours,
            w.lab_hours,
            (w.lecture_hours + w.practice_hours + w.lab_hours) AS total_hours,
            w.academic_year
        FROM workload w
        JOIN teachers t ON t.id = w.teacher_id
        JOIN subjects s ON s.id = w.subject_id
        WHERE w.semester = ?
        ORDER BY t.full_name, s.name
    """, (semester,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def report_overloaded_teachers() -> list:
    all_teachers = report_all_teachers()
    return [t for t in all_teachers if t["total_hours"] > t["max_workload"]]


def report_underloaded_teachers(threshold_percent: float = 60.0) -> list:
    all_teachers = report_all_teachers()
    result = []
    for t in all_teachers:
        if t["max_workload"] > 0:
            pct = t["total_hours"] / t["max_workload"] * 100
            if pct < threshold_percent:
                t["percent"] = round(pct, 1)
                result.append(t)
    return result


def report_subjects_summary() -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            s.name           AS subject_name,
            s.code           AS subject_code,
            GROUP_CONCAT(t.full_name, '; ') AS teachers,
            COALESCE(SUM(w.lecture_hours + w.practice_hours + w.lab_hours), 0) AS total_hours
        FROM subjects s
        LEFT JOIN workload w ON w.subject_id = s.id
        LEFT JOIN teachers t ON t.id = w.teacher_id
        GROUP BY s.id
        ORDER BY s.name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]