import asyncio
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from loader import dp


class TaskGroup(StatesGroup):
    open = State()
    doing = State()
    detailed_solution = State()


task_callback = CallbackData("task", "user_choice", "right_choice")


@dp.message_handler(commands=['receive_task'])
async def temp_new_task_notification(message: types.Message):
    text = "Вам пришла новая задача"
    timestamp = int(datetime.now().timestamp())
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton("Открыть", callback_data=f"new_task:open:{timestamp}")
    ]])
    await message.answer(text, reply_markup=keyboard)
    await TaskGroup.open.set()


@dp.callback_query_handler(state=TaskGroup.open)
async def send_task(call: types.CallbackQuery, state: FSMContext):
    current_timestamp = int(datetime.now().timestamp())
    notification_timestamp = int(call.data.split(':')[-1])
    if current_timestamp - notification_timestamp > 10 * 60:
        await call.message.answer("Дружок, прости, ты не успел :(")
        await state.finish()
        return

    header = ("<b><i>У тебя есть 5 минут :)</></>",)
    text = (
        "",
        "Какое произведение не принадлежит А.С. Пушкину?",
        "",
        "Варианты ответа:",
        '1. <i>"Евгений Онегин"</>',
        '2. <i>"Капитанская дочка"</>',
        '3. <i>"Ревизор"</>'
    )
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(str(number), callback_data=task_callback.new(
            user_choice=number, right_choice=3
        ))
        for number in range(1, 4)
    ]])
    await call.message.answer('\n'.join(header + text), types.ParseMode.HTML, reply_markup=keyboard)
    await TaskGroup.doing.set()

    await asyncio.sleep(5 * 60)
    header = ("<b><i>Упс... Время для ответа вышло :(</></>",)
    await call.message.delete_reply_markup()
    await call.message.edit_text('\n'.join(header + text), types.ParseMode.HTML)


@dp.callback_query_handler(task_callback.filter(), state=TaskGroup.doing)
async def check_answer(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete_reply_markup()
    user_choice, right_choice = int(callback_data["user_choice"]), int(callback_data["right_choice"])

    if user_choice == right_choice:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton("Подробное решение", callback_data="detailed_solution")
        ]])
        text = '\n'.join((
            "Слушай, да ты крут!",
            "Совершенно верный ответ и отличная работа!"
        ))
        await call.message.answer(text, types.ParseMode.HTML, reply_markup=keyboard)
        await TaskGroup.detailed_solution.set()

    else:
        await show_detailed_answer(call, state, include_header=True)


@dp.callback_query_handler(state=TaskGroup.detailed_solution)
async def show_detailed_answer(call: types.CallbackQuery, state: FSMContext, include_header=False):
    await call.message.delete_reply_markup()
    text = (
        'Это нужно просто запомнить - "Ревизор" не принадлежит А.С. Пушкину :)',
        "",
        "Не расслабляйся, я могу появиться любую минуту! Давай и дальше оттачивать навыки быстрого решения.",
        "Увидимся)"
    )
    if include_header:
        header = ("Почти, ты был очень близок!", "Давай вместе посмотрим, более подробное решение:", "")
        text = header + text
    await call.message.answer('\n'.join(text))
    await state.finish()
