import os
import sys
from argparse import ArgumentParser
from pprint import pprint
from uuid import uuid4

import boto3
import logging

DFLT_BUCKET_NAME = os.environ.get('SYNCLOUD_BUCKET_NAME')
DFLT_QUEUE_URL = os.environ.get('SYNCLOUD_QUEUE_URL')
DFLT_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__),
    'cf', 'bucket_template.yaml'
)

logger = logging.getLogger(__name__)


def log_result(message, result):
    logger.info(message)
    logger.debug(result)


def create_stack(template_path, bucket_name, queue_name):
    stack_name = 'syncloud-' + str(uuid4())
    with open(template_path, 'r', encoding='UTF-8') as f:
        template = f.read()
    parameters = {
        'pBucketName': bucket_name,
        'pQueueName': queue_name
    }

    client = boto3.client('cloudformation')
    res = client.create_stack(
        StackName=stack_name,
        TemplateBody=template,
        DisableRollback=True,
        Parameters=[
            {'ParameterKey': k, 'ParameterValue': v}
            for k, v in parameters.items()
        ]
    )
    log_result('create_stack', res)

    waiter = client.get_waiter('stack_create_complete')
    res = waiter.wait(StackName=stack_name)
    log_result('wait for stack_create_complete', res)

    res = client.describe_stacks(StackName=stack_name)
    log_result('describe_stacks', res)
    return res


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


def setup_bucket_notification(bucket_name, queue_name):
    queue_url, queue_arn = get_queue_details(queue_name)
    
    client = boto3.client('s3')
    res = client.put_bucket_notification_configuration(
        Bucket=bucket_name,
        NotificationConfiguration={
            'QueueConfigurations': [
                {
                    'QueueArn': queue_arn,
                    'Events': [
                        's3:ObjectCreated:*',
                        's3:ObjectRemoved:*'
                    ]
                }
            ]
        }
    )
    log_result('put_bucket_notification_configuration', res)
    return 0


def create_command(opts):
    create_stack(opts.template, opts.bucket, opts.queue)
    setup_bucket_notification(opts.bucket, opts.queue)
    print('create completed')
    return 0


def push_command(opts):
    print('push - not yet implemented')
    return 1


def pull_command(opts):
    print('pull - not yet implemented')
    return 1


def create_parser(prog_name):
    parser = ArgumentParser(prog=prog_name)

    common = ArgumentParser(add_help=False)                                 
    common.add_argument(
        '--bucket', '-b', metavar='NAME',
        default=DFLT_BUCKET_NAME,
        help='specify the bucket name'
    )
    common.add_argument(
        '--queue', '-q', metavar='URL',
        default=DFLT_QUEUE_URL,
        help='specify the queue url'
    )
    common.add_argument(
        '--verbose', '-v',
        action='count', default=0,
        help='increase verbosity'
    )

    sp = parser.add_subparsers(title="command(s)")
    create = sp.add_parser(
        'setup',
        parents=[common],
        help='create bucket and associated queue'
    )
    create.set_defaults(func=create_command)
    create.add_argument(
        '--template', metavar='PATH',
        default=DFLT_TEMPLATE_PATH,
        help='Path to the cloudformation template'
    )

    push = sp.add_parser(
        'push',
        parents=[common],
        help='push local files to the queue'
    )
    push.set_defaults(func=push_command)

    pull = sp.add_parser(
        'pull',
        parents=[common],
        help='pull changes from the bucket locally'
    )
    pull.set_defaults(func=pull_command)
    return parser


def main_guts(args):
    parser = create_parser(args[0])
    opts = parser.parse_args(args[1:])
    if not hasattr(opts, 'func'):
        parser.print_help(sys.stderr)
        return 1
    if opts.verbose == 1:
        logger.setLevel(logging.INFO)
    elif opts.verbose > 1:
        logger.setLevel(logging.DEBUG)
    return opts.func(opts)


def main():
    logging.basicConfig()
    return main_guts(sys.argv)


if __name__ == '__main__':
    main()
