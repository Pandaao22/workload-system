
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "kafedra-ai-secret-2024")
DEBUG = True
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "workload.db")

MAX_WORKLOAD_DEFAULT = 900

POSITIONS = [
    "Профессор",
    "Доцент",
    "Старший преподаватель",
    "Преподаватель",
    "Ассистент",
]
POSITION_MAX_WORKLOAD = {
    "Профессор":               900,
    "Доцент":                  850,
    "Старший преподаватель":   800,
    "Преподаватель":           750,
    "Ассистент":               700,
}
SEMESTERS = [1, 2]
DEPARTMENT_NAME = "Кафедра технологий искусственного интеллекта"
UNIVERSITY_NAME  = "Университет"