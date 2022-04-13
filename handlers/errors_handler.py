import logging

from aiogram.utils import exceptions

from loader import dp


@dp.errors_handler()
async def errors_handler(update, exception):
    """
    Exceptions handler. Catches all exceptions within task factory tasks.
    :param update:
    :param exception:
    :return: stdout logging
    """

    if isinstance(exception, exceptions.CantDemoteChatCreator):
        logging.exception("Can't demote chat creator")
        return True

    if isinstance(exception, exceptions.MessageNotModified):
        logging.exception('Message is not modified')
        return True

    if isinstance(exception, exceptions.MessageCantBeDeleted):
        logging.exception('Message cant be deleted')
        return True

    if isinstance(exception, exceptions.MessageToDeleteNotFound):
        logging.exception('Message to delete not found')
        return True

    if isinstance(exception, exceptions.MessageTextIsEmpty):
        logging.exception('MessageTextIsEmpty')
        return True

    if isinstance(exception, exceptions.Unauthorized):
        logging.exception(f'Unauthorized: {exception}')
        return True

    if isinstance(exception, exceptions.InvalidQueryID):
        logging.exception(f'InvalidQueryID: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, exceptions.TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, exceptions.RetryAfter):
        logging.exception(f'RetryAfter: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, exceptions.CantParseEntities):
        logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True

    logging.exception(f'Update: {update} \n{exception}')
