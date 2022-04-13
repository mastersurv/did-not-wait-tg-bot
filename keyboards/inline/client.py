from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from database.models import Course

course_choices = ['ЕГЭ', 'ОГЭ', 'Не участвую']
ege_subjects = ['Русский язык', 'Математика', 'Базовая математика', 'Обществознание', 'История', 'Литература',
                'Английский язык', 'Химия', 'Биология', 'Физика', 'Информатика', 'География', 'Немецкий язык']
oge_subjects = ['Русский язык', 'Математика', 'Обществознание', 'История', 'Литература',
                'Английский язык', 'Химия', 'Биология', 'Физика', 'Информатика', 'География']

default_time_interval_callback = CallbackData("default_time_interval", "choice")
default_time_interval_kb = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton("С 9:00 до 21:00 МСК", callback_data=default_time_interval_callback.new("9AM-9PM")),
    InlineKeyboardButton("Настроить под себя", callback_data=default_time_interval_callback.new("custom"))
]])
time_intervals = ["9AM-1PM", "1PM-5PM", "5PM-9PM"]
time_interval_callback = CallbackData("time_interval", "choice")


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


def get_time_interval_kb(intervals_with_checkmark: list[str] = None):
    include_done_button = intervals_with_checkmark is not None
    if intervals_with_checkmark is None:
        intervals_with_checkmark = []
    time_intervals_labels = ["С 9:00 до 13:00 МСК", "С 13:00 до 17:00 МСК", "С 17:00 до 21:00 МСК"]
    for index, time_interval_label in enumerate(time_intervals_labels):
        if time_intervals[index] in intervals_with_checkmark:
            time_intervals_labels[index] = "✅ " + time_interval_label
    buttons = [InlineKeyboardButton(time_interval_label, callback_data=time_interval_callback.new(time_interval))
               for time_interval, time_interval_label in zip(time_intervals, time_intervals_labels)]
    if include_done_button:
        buttons.append(InlineKeyboardButton("Готово", callback_data=time_interval_callback.new("done")))
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard
