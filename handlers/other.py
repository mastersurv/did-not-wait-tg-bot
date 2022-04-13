from aiogram import types

from loader import dp


@dp.message_handler()
async def echo_send(message: types.Message):
    await message.answer(message.text)
