import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from database.models import Course
from keyboards.inline.client import course_choices, get_course_choice_kb, ege_subjects, create_client_kb
from loader import dp
from services.messages import delete_message


class FSMClient(StatesGroup):
    course = State()
    subjects = State()


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message, state: FSMContext):
    text = '\n'.join((
        "• Я отправляю тебе задачу в рандомное время, за исключением, когда тебе совсем неудобно отвечать. "
        "Ее можно решить без ручек и листочков",
        "• У тебя есть варианты ответа и 5 минут на ее решение",
        "• В конце каждой недели я отправляю тебе рекомендации по темам, которые было бы неплохо повторить",
        "[Можно подробнее ознакомиться со всем функциями бота вот тут] (https://www.google.com/)"
    ))
    await message.answer(text, parse_mode=types.ParseMode.MARKDOWN)
    await message.answer("*Пожалуйста, выбери направление*", parse_mode=types.ParseMode.MARKDOWN,
                         reply_markup=get_course_choice_kb())
    await FSMClient.course.set()


@dp.callback_query_handler(Text(equals=course_choices), state=FSMClient.course)
async def choice_course(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_message(callback_query.message)
    choice = callback_query.data

    if choice == "Не участвую":
        await callback_query.answer("Будем рады тебя видеть на подготовке в любое время!", show_alert=True)
        await state.finish()
        return

    await callback_query.answer()
    async with state.proxy() as data:
        data['course'] = choice

    text = '\n'.join((
        "Выбери предметы для подготовки",
        "Но! помни, что предметы поменять не получится. А если добавить новые, то тебе будет приходить больше задач",
        f"*Список предметов {choice}*"
    ))
    course = Course.ege if choice == 'ЕГЭ' else Course.oge
    await callback_query.message.answer(text, parse_mode=types.ParseMode.MARKDOWN,
                                        reply_markup=create_client_kb(course, []))
    await FSMClient.next()


@dp.callback_query_handler(Text(equals=ege_subjects), state=FSMClient.subjects)
async def subjects(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    async with state.proxy() as data:
        if 'subjects' not in data:
            data['subjects'] = [callback_query.data]
        elif len(data['subjects']) < 5:
            data['subjects'].append(callback_query.data)
        course, subjects = data['course'], data['subjects']

    course = Course.ege if course == 'ЕГЭ' else Course.oge
    await callback_query.message.edit_reply_markup(create_client_kb(course, subjects))
