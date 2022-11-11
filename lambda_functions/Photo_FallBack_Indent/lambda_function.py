import time
import dateutil.parser
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

def query_to_keywords(query):
    keywords = []
    if "show me" in query:
        words = query.replace(', ', ' ')
        word_lists = words.split(' ')
        if "and" in query:
            and_index = word_lists.index("and")
            keywords.append(word_lists[and_index-1])
            keywords.append(word_lists[and_index+1])
        else:
            keywords.append(word_lists[-1])
    else:
        word_lists = query.split(', ')
        keywords = word_lists
    return keywords


""" --- Functions that control the bot's behavior --- """

def process_keywords(intent_request):
    query = intent_request['inputTranscript']
    keywords = query_to_keywords(query)
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'processing the keywords of {}'.format(keywords)})


""" --- Intents --- """


def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    intent_name = intent_request['currentIntent']['name']
    return process_keywords(intent_request)


""" --- Main handler --- """


def lambda_handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
