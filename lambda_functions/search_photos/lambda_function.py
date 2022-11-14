import json
import boto3
import requests
from requests.auth import HTTPBasicAuth


def lambda_handler(event, context):

    client = boto3.client('lex-runtime')
    user_id = "114514"
    # q = 'show me photos with sky and building in them'
    # q = 'sky, building'
    # event_dic = json.loads(event['body'])
    q = event['multiValueQueryStringParameters']['q'][0]
    response = client.post_text(
        botName='Photo_Bot',
        botAlias='v_a',
        userId=user_id,
        inputText=q,
    )

    # if does have key, go to es
    if 'processing the keywords of ' in response["message"]:
        keywords = response["message"].replace('processing the keywords of ', '')
        keywords = keywords.strip('[]')
        keywords_list = keywords.split(", ")
        for i in keywords_list:
            if i == 'empty':
                keywords_list.remove(i)

        host = 'https://search-photos-scozuytzo7gfyugjmx6cawysyi.us-east-1.es.amazonaws.com'
        index = 'photos'
        url = host + '/' + index + '/_search'

        # and query
        '''
        query = {
            "size": 5,
            "query": {
                "bool":{
                    "must":[]
                }
            }
        }

        for i in keywords_list:
            match_cond = {
                "match":{
                    "labels":i
                }
            }
            query['query']['bool']['must'].append(match_cond)
        '''

        # or query
        query = {
            "query": {
                "bool": {
                    "should": []
                }
            }
        }

        for i in keywords_list:
            match_cond = {
                "match": {
                    "labels": i
                }
            }
            query['query']['bool']['should'].append(match_cond)

        headers = {"Content-Type": "application/json"}
        r = requests.get(url, auth=HTTPBasicAuth('sihanasaku', 'Wsh010217!'), headers=headers, data=json.dumps(query))
        query_result = json.loads(r.content)
        result_photos = query_result['hits']['hits']
        return_message = []
        for photo in result_photos:
            photo_info = {
                "_id": photo["_id"],
                "createdTimestamp": photo["_source"]["createdTimestamp"]
            }
            return_message.append(photo_info)

    else:
        return_message = []
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        'body': json.dumps(return_message)
    }
