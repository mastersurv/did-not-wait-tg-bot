from dataclasses import dataclass

from enum import Enum


# Датаклассы и перечисления используются для удобной передачи данных

@dataclass
class User:
    telegram_id: int
    full_name: str
    username: str


class Course(Enum):
    ege = 0
    oge = 1
