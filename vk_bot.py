import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import os
from dotenv import load_dotenv

import dialogflow_tools

import logging.config
import TG_log_class


logger = logging.getLogger("bot_logger")


def respond_from_df_to_vk(vk_event, vk_api_resp, df_answer):
    vk_api_resp.messages.send(
        user_id=vk_event.user_id,
        message=df_answer,
        random_id=random.randint(1, 1000)
    )


if __name__ == "__main__":
    load_dotenv()
    service_tlg_token = os.environ['SVC_TLG_TOKEN']
    service_chat_id = os.environ['TLG_CHAT_ID']
    logger_config = TG_log_class.create_logger_config(service_tlg_token, service_chat_id, __file__)
    logging.config.dictConfig(logger_config)

    vk_api_key = os.environ['VK_API']
    df_project = os.environ['DF_PROJECT']
    vk_group_id = os.environ['VK_GROUP']

    language_code = 'ru'
    vk_session = vk_api.VkApi(token=vk_api_key)
    vk_api = vk_session.get_api()
    long_poll = VkLongPoll(vk_session)
    for event in long_poll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            df_response = dialogflow_tools.detect_intent_texts(df_project, vk_group_id, event.text, language_code)
            if df_response:
                respond_from_df_to_vk(event, vk_api, df_response)
