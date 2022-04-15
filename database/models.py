from dataclasses import dataclass

from enum import Enum


# Датаклассы и перечисления используются для удобной передачи данных


@dataclass
class User:
    telegram_id: int
    full_name: str
    direction: str
    interval: int
    subjects: list[str]


@dataclass
class Task:
    id: int
    text: str
    variant1: str
    variant2: str
    variant3: str
    right_variant: int
    solution: str
    subject: str
    direction: str
    subtheme: str


class Course(Enum):
    ege = 0
    oge = 1