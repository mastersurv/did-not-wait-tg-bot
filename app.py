import logging

from aiogram import executor

# noinspection PyUnresolvedReferences
# import filters
# noinspection PyUnresolvedReferences
import handlers
from loader import dp, bot
from services.default import set_default_commands, on_startup_notify, on_shutdown_notify


async def on_startup(dispatcher):
    # logging.info("Создаем подключение к базе данных")
    # await db.create_pool()
    #
    # logging.info("Создаем таблицы в базе данных, если такие еще не были созданы")
    # await db.create_standard_tables()

    await set_default_commands(dispatcher)

    logging.info("Отправляем админам сообщение о том, что бот запустился")
    await on_startup_notify(dispatcher)


async def on_shutdown(dispatcher):
    logging.warning("Отправляем админам сообщение о том, что бот остановился")
    await on_shutdown_notify(dispatcher)

    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    bot_session = await bot.get_session()
    await bot_session.close()


if __name__ == "__main__":
    logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO)
    try:
        executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
    except (KeyboardInterrupt, SystemExit):
        logging.error(f"Бот был остановлен!")
    except BaseException as e:
        logging.exception(f"Бот был остановлен из-за возникшего исключения: {e}")
