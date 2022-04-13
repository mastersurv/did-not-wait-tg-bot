from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.models import Course

course_choices = ['ЕГЭ', 'ОГЭ', 'Не участвую']
ege_subjects = ['Русский язык', 'Математика', 'Базовая математика', 'Обществознание', 'История', 'Литература',
                'Английский язык', 'Химия', 'Биология', 'Физика', 'Информатика', 'География', 'Немецкий язык']
oge_subjects = ['Русский язык', 'Математика', 'Обществознание', 'История', 'Литература',
                'Английский язык', 'Химия', 'Биология', 'Физика', 'Информатика', 'География']


def get_course_choice_kb() -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = []
    for choice in course_choices:
        buttons.append(InlineKeyboardButton(choice, callback_data=choice))
    keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=[buttons])
    return keyboard


def create_client_kb(course: Course, subjects_with_checkmark: list[str]) -> InlineKeyboardMarkup:
    subjects = {Course.ege: ege_subjects, Course.oge: oge_subjects}
    buttons: list[InlineKeyboardButton] = []
    flag = False
    for subject in subjects[course]:
        if subject in subjects_with_checkmark:
            subject_name = "✅ " + subject
            flag = True
        else:
            subject_name = subject
        buttons.append(InlineKeyboardButton(subject_name, callback_data=subject_name))
    button_selected = InlineKeyboardButton(text="Готово", callback_data="selected")
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    if flag:
        keyboard.row(button_selected)
    return keyboard
