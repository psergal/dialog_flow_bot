import random
import dialogflow_v2beta1 as dialogflow
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import os
from dotenv import load_dotenv


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
    language_code = 'ru'
    vk_session = vk_api.VkApi(token=vk_api_key)
    vk_api = vk_session.get_api()
    long_poll = VkLongPoll(vk_session)
    for event in long_poll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            df_response = detect_intent_texts(df_project, vk_group_id, event.text, language_code)
            if df_response:
                respond_from_df_to_vk(event, vk_api, df_response)
