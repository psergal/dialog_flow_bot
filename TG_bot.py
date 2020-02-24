import os
from dotenv import load_dotenv
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import dialogflow_tools

import logging.config
import TG_log_class


logger = logging.getLogger("bot_logger")


def df_callback(update, context):
    """Main working function for successful path.

    Get the update from the particular chat sends it to Google DialogFlow service
    finds the appropriate intent extracts the answer and transfers it to the user-bot chat
    DialogFlow project should be specify in the .env file.
    """

    df_project = os.environ['DF_PROJECT']
    df_response = dialogflow_tools.detect_intent_texts(df_project, update.message.chat_id, update.message.text, 'ru')
    if df_response:
        context.bot.send_message(chat_id=update.message.chat_id, text=df_response)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error, extra={'Update_err': True})


def call_bot(telegram_token):
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    df_handler = MessageHandler(Filters.text, df_callback)
    dispatcher.add_handler(df_handler)
    dispatcher.add_error_handler(error)
    updater.start_polling()


if __name__ == '__main__':
    load_dotenv()
    tlg_token = os.environ['TLG_TOKEN']

    service_tlg_token = os.environ['SVC_TLG_TOKEN']
    service_chat_id = os.environ['TLG_CHAT_ID']
    logger_config = TG_log_class.create_logger_config(service_tlg_token, service_chat_id, __file__)

    logging.config.dictConfig(logger_config)
    call_bot(tlg_token)
