import random
import dialogflow_v2beta1 as dialogflow
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import os
from dotenv import load_dotenv
import time
import sys
import telegram.ext
import requests
import logging


class TelegramLogsHandler(logging.Handler):
    def __init__(self, telegram_token, telegram_chat_id):
        super().__init__()
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_bot = telegram.Bot(self.telegram_token)
        self.telegram_bot.send_message(chat_id=self.telegram_chat_id, text=f'VK bot has started at {time.ctime()}')

    def emit(self, record):
        log_entry = self.format(record)
        if isinstance(record.exc_info, tuple) and record.exc_info[0] == requests.exceptions.ConnectionError:
            return
        else:
            self.telegram_bot.send_message(chat_id=self.telegram_chat_id, text=f'{log_entry}')


def respond_from_df_to_vk(vk_event, vk_api_resp, df_answer):
    vk_api_resp.messages.send(
        user_id=vk_event.user_id,
        message=df_answer,
        random_id=random.randint(1, 1000)
    )


def detect_intent_texts(project_id, session_id, text, lang_code):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation."""
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=lang_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    if response.query_result.intent.display_name == 'Default Fallback Intent':
        print('Default Fallback Intent')
        return
    return response.query_result.fulfillment_text


if __name__ == "__main__":
    load_dotenv()
    vk_api_key = os.environ['VK_API']
    df_project = os.environ['DF_PROJECT']
    vk_group_id = os.environ['VK_GROUP']

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

    language_code = 'ru'
    vk_session = vk_api.VkApi(token=vk_api_key)
    vk_api = vk_session.get_api()
    long_poll = VkLongPoll(vk_session)
    for event in long_poll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            df_response = detect_intent_texts(df_project, vk_group_id, event.text, language_code)
            if df_response:
                respond_from_df_to_vk(event, vk_api, df_response)
