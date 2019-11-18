import json
import requests
import argparse
import dialogflow_v2beta1 as dialogflow
from dotenv import load_dotenv
import os

def get_args():
    parser = argparse.ArgumentParser(description='DialogFlow Intent`s handling')
    parser.add_argument('--intents_mode', default='upload', choices=['upload', 'download'],
                        help='Define would you like download or upload questions')
    parser.add_argument('--q_list_url', default='https://dvmn.org/filer/canonical/1556745451/104/',
                        help='url for questions')
    parser.add_argument('--headers', default={
        'User-Agent': 'curl',
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=UTF-8',
    },  help=argparse.SUPPRESS)
    parser.add_argument('--q_fname', default='questions.json',  help='Set file name for questions')
    args = parser.parse_args()
    return args


def load_questions(q_list_url, headers, q_fname):
    resp = requests.get(q_list_url, headers=headers)
    if not resp.ok:
        return None
    json_resp = resp.json()
    with open(q_fname, 'w', encoding='UTF-8') as write_file:
        json.dump(json_resp, write_file)


def list_intents(project_id):
    intents_client = dialogflow.IntentsClient()
    parent = intents_client.project_agent_path(project_id)
    intents = intents_client.list_intents(parent)
    intents_list= [intent.display_name for intent in intents]
    return intents_list


def create_intent(project_id, display_name, training_phrases_parts,
                  message_texts):
    """Create an intent of the given intent type."""
    intents_client = dialogflow.IntentsClient()

    parent = intents_client.project_agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.types.Intent.TrainingPhrase.Part(
            text=training_phrases_part)
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.types.Intent.Message.Text(text=message_texts)
    message = dialogflow.types.Intent.Message(text=text)

    intent = dialogflow.types.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message])

    response = intents_client.create_intent(parent, intent)
    return response


if __name__ == '__main__':
    args = get_args()
    if args.intents_mode ==  'download':
        load_questions(args.q_list_url, args.headers, args.q_fname)
    elif args.intents_mode == 'upload':
        load_dotenv()
        df_project = os.environ['DF_PROJECT']
        existed_intents = list_intents(df_project)
        with open(args.q_fname, 'r', encoding='UTF-8') as questions:
            df_questions = json.load(questions)
        for intent_name, tranings in df_questions.items():
            if intent_name not in existed_intents:
                df_response = create_intent(df_project, intent_name, tranings['questions'], [tranings['answer']])
                print(f'Intent created: {df_response.display_name}')
            else:
                print(f' intent:{intent_name} - already exists')


