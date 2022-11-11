import boto3
from decimal import Decimal
import json
import urllib.request
import urllib.parse
import urllib.error
import requests
from requests.auth import HTTPBasicAuth

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')


def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response


def get_labels(response):
    labels = []
    for l in response['Labels']:
        labels.append(l['Name'])
    return labels


# --------------- Main handler ------------------


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    try:
        # Calls rekognition DetectLabels API to detect labels in S3 object
        response = detect_labels(bucket, key)
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
    labels = get_labels(response)
    # add custom labels
    s3_cli = boto3.client('s3')
    object_summary = s3_cli.head_object(
        Bucket=bucket,
        Key=key,
    )
    if 'x-amz-meta-customlabels' in object_summary['ResponseMetadata']['HTTPHeaders'].keys():
        custom_labels = object_summary['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels'].split(", ")
        labels = labels + custom_labels

    photo_info = {
        'objectKey': key,
        'bucket': bucket,
        'createdTimestamp': event['Records'][0]['eventTime'],
        'labels': labels
    }
    es_key = key.replace("images/", "")
    # insert photo_info to es
    es_index = 'photos'
    host = 'https://search-photos-scozuytzo7gfyugjmx6cawysyi.us-east-1.es.amazonaws.com'
    url = host + '/' + es_index + '/_doc/' + es_key
    headers = {"Content-Type": "application/json"}
    r = requests.put(url, auth=HTTPBasicAuth('sihanasaku', 'Wsh010217!'), headers=headers, data=json.dumps(photo_info))
    result = json.loads(r.content)
    return result