from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

import config


class AdminFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.from_user.id in config.ADMINS
