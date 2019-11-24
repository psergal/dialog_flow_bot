import requests
import os
from dotenv import load_dotenv
import logging
import telegram.ext
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import dialogflow_v2beta1 as dialogflow
import time
import sys


class TelegramLogsHandler(logging.Handler):
    def __init__(self, telegram_token, telegram_chat_id):
        super().__init__()
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_bot = telegram.Bot(self.telegram_token)
        self.telegram_bot.send_message(chat_id=self.telegram_chat_id, text=f'Telegram bot has started at {time.ctime()}')

    def emit(self, record):
        log_entry = self.format(record)
        if isinstance(record.exc_info, tuple) and record.exc_info[0] == requests.exceptions.ConnectionError:
            return
        else:
            self.telegram_bot.send_message(chat_id=self.telegram_chat_id, text=f'{log_entry}')


def detect_intent_texts(project_id, session_id, text, language_code):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation."""
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result.fulfillment_text


def df_callback(update, context):
    """
    Gets the update from the particular chat sends it to Google DialogFlow service
    finds the appropriate intent extracts the answer and transfers it to the user-bot chat
    DialogFlow project should be specify in the .env file
    """
    df_project = os.environ['DF_PROJECT']
    df_response = detect_intent_texts(df_project, update.message.chat_id, update.message.text, 'ru')
    context.bot.send_message(chat_id=update.message.chat_id, text=df_response)


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


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

    svc_tlg_token = os.environ['SVC_TLG_TOKEN']
    svc_chat_id = os.environ['TLG_CHAT_ID']

    log_format = "%(levelname)s %(asctime)s - %(funcName)s - %(message)s"
    formatter = logging.Formatter(log_format)

    logger = logging.getLogger("bot_logger")
    tlg_handler = TelegramLogsHandler(svc_tlg_token, svc_chat_id)
    tlg_handler.setLevel(logging.ERROR)
    tlg_handler.setFormatter(formatter)
    logger.addHandler(tlg_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    call_bot(tlg_token)
