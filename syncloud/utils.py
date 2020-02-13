import logging

import boto3


logger = logging.getLogger('syncloud')


def log_result(message, result):
    logger.info(message)
    logger.debug(result)


def get_queue_details(queue_name):
    client = boto3.client('sqs')

    res = client.get_queue_url(QueueName=queue_name)
    log_result('get_queue_url', res)
    queue_url = res['QueueUrl']

    res = client.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['QueueArn']
    )
    log_result('get_queue_attributes', res)
    queue_arn = res['Attributes']['QueueArn']
    return queue_url, queue_arn
