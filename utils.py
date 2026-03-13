
from config import POSITION_MAX_WORKLOAD, MAX_WORKLOAD_DEFAULT


def get_max_workload_for_position(position: str) -> int:
    return POSITION_MAX_WORKLOAD.get(position, MAX_WORKLOAD_DEFAULT)


def calculate_total_hours(lecture: int, practice: int, lab: int) -> int:
    return (lecture or 0) + (practice or 0) + (lab or 0)


def workload_status(current: int, maximum: int) -> dict:
    if maximum == 0:
        return {"percent": 0, "label": "Не задана", "color": "secondary"}

    percent = round(current / maximum * 100, 1)

    if percent < 60:
        label, color = "Низкая", "info"
    elif percent < 85:
        label, color = "Нормальная", "success"
    elif percent <= 100:
        label, color = "Высокая", "warning"
    else:
        label, color = "Перегрузка!", "danger"

    return {"percent": min(percent, 100), "label": label, "color": color}


def validate_hours(value, field_name: str) -> tuple[int, str | None]:
    try:
        val = int(value)
        if val < 0:
            raise ValueError
        return val, None
    except (ValueError, TypeError):
        return 0, f"Поле «{field_name}» должно быть неотрицательным числом."


def format_teacher_name(full_name: str) -> str:
    parts = full_name.strip().split()
    if len(parts) >= 3:
        return f"{parts[0]} {parts[1][0]}.{parts[2][0]}."
    return full_name