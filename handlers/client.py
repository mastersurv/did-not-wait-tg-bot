from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from database.models import Course
from keyboards.inline.client import course_choices, get_course_choice_kb, ege_subjects, create_client_kb, \
    default_time_interval_kb, default_time_interval_callback, time_intervals, time_interval_callback, \
    get_time_interval_kb, create_yes_or_cancel_kb
from loader import dp, db
from services.interval import get_interval_from_choices
from services.messages import delete_message


class FSMClient(StatesGroup):
    course = State()
    subjects = State()
    sureness = State()
    time_intervals = State()


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
    if not await db.user_id_present(message.from_user.id):
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
    course = Course.ege if choice == 'егэ' else Course.oge
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
        else:
            return
        course, subjects = data['course'], data['subjects']

    course = Course.ege if course == 'егэ' else Course.oge
    await callback_query.message.edit_reply_markup(create_client_kb(course, subjects))


@dp.callback_query_handler(Text(equals="selected"), state=FSMClient.subjects)
async def show_default_time_intervals(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await delete_message(call.message)
    async with state.proxy() as data:
        list_subjects = "\n".join(data['subjects'])
        await call.message.answer(f"Ты выбрал такие предметы:\n{list_subjects}\nВсё верно?",
                                  reply_markup=create_yes_or_cancel_kb())
    await FSMClient.sureness.set()


@dp.callback_query_handler(Text(equals=["yes", "change"]), state=FSMClient.sureness)
async def yes_or_change(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data == "yes":
        await delete_message(call.message)
        text = '\n'.join((
            "Остался последний шаг.",
            "Давай определимся со временем, когда ты сможешь отвечать на задачи"
        ))
        await call.message.answer(text, reply_markup=default_time_interval_kb)
        await FSMClient.time_intervals.set()
    elif call.data == "change":
        await delete_message(call.message)
        async with state.proxy() as data:
            data['subjects'].clear()
            course, subjects = data['course'], data['subjects']
            course = Course.ege if course == 'егэ' else Course.oge
            text = '\n'.join((
                "Выбери предметы для подготовки",
                "Но! помни, что предметы поменять не получится. А если добавить новые, то тебе будет приходить больше задач",
                f"*Список предметов {data['course']}*"
            ))
            await call.message.answer(text, parse_mode=types.ParseMode.MARKDOWN,
                                      reply_markup=create_client_kb(course, []))
            await FSMClient.subjects.set()


@dp.callback_query_handler(default_time_interval_callback.filter(choice="9AM-9PM"), state=FSMClient.time_intervals)
async def show_final_message(call: types.CallbackQuery, state: FSMContext, choices: set[str] = None):
    await call.answer()
    if choices is None:
        choices = time_intervals
    else:
        choices = list(choices)
    async with state.proxy() as data:
        course, subjects = data['course'], data['subjects']
    interval = get_interval_from_choices(choices)
    await db.add_user(call.from_user.id, call.from_user.full_name,
                      course, interval, subjects)
    text = "Теперь мы готовы начинать. Пристегивайся, игра началась!"
    await call.message.answer(text)
    await state.finish()


@dp.callback_query_handler(default_time_interval_callback.filter(choice="custom"), state=FSMClient.time_intervals)
@dp.callback_query_handler(time_interval_callback.filter(), state=FSMClient.time_intervals)
async def show_time_intervals(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    if callback_data["@"] == default_time_interval_callback.prefix:
        await call.message.delete_reply_markup()
        text = "Важно! Поменять интервал позже можно только раз. Так что подумай хорошенько)"
        await call.message.answer(text, reply_markup=get_time_interval_kb())
    elif callback_data["choice"] != "done":
        chosen_time_interval = callback_data["choice"]
        async with state.proxy() as data:
            if "time_intervals" not in data:
                data["time_intervals"] = {chosen_time_interval}
            elif chosen_time_interval not in data["time_intervals"]:
                data["time_intervals"].add(chosen_time_interval)
            else:
                return
            chosen_time_intervals: set[str] = data["time_intervals"]
        await call.message.edit_reply_markup(get_time_interval_kb(chosen_time_intervals))
    else:
        async with state.proxy() as data:
            chosen_time_intervals = data.get("time_intervals")
        if not chosen_time_intervals:
            await call.answer("Пожалуйста, выбери хотя бы один интервал", show_alert=True)
        else:
            await show_final_message(call, state, choices=chosen_time_intervals)
