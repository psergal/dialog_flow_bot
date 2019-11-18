import os
from dotenv import load_dotenv
import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import dialogflow_v2beta1 as dialogflow


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
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)
    call_bot(tlg_token)
