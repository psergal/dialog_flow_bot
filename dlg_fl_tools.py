import dialogflow_v2beta1 as dialogflow
import logging

logger = logging.getLogger("bot_logger")


def detect_intent_texts(project_id, session_id, text, lang_code):
    """
    Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation.
    """
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=lang_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    if response.query_result.intent.is_fallback:
        logger.error('Ups.. Default Fallback Intent', extra={'df_intent': True})
        return
    return response.query_result.fulfillment_text
