import boto3
import json as js
import os

boto_session = None
ymq_queue = None

def get_boto_session():
    global boto_session

    if boto_session is not None:
        return boto_session

    boto_session = boto3.session.Session(
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

    return boto_session
    
def get_ymq_queue():
    global ymq_queue

    if ymq_queue is not None:
        return ymq_queue

    ymq_queue = get_boto_session().resource(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1'
    ).Queue(os.environ['YMQ_QUEUE_URL'])

    return ymq_queue

def create_task(text):
    get_ymq_queue().send_message(MessageBody=js.dumps({'text': text}))

def handler(event, context):
    create_task(event)

    return {
        'statusCode': 200,
        'body': 'ok'
    }                 
