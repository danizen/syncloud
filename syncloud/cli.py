import os
import sys
from argparse import ArgumentParser
from pprint import pprint
from uuid import uuid4

import boto3

DFLT_BUCKET_NAME = os.environ.get('SYNCLOUD_BUCKET_NAME')
DFLT_QUEUE_URL = os.environ.get('SYNCLOUD_QUEUE_URL')
DFLT_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__),
    'cf', 'bucket_template.yaml'
)


def verbose_result(res):
    pprint(res, indent=2)
    sys.stdout.flush()


def create_command(opts):
    verbose = opts.verbose
    stack_name = 'syncloud-' + str(uuid4())

    with open(opts.template, 'r', encoding='UTF-8') as f:
        template = f.read()
    parameters = {
        'pBucketName': opts.bucket,
        'pQueueName': opts.queue
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
    if verbose:
        verbose_result(res)
    waiter = client.get_waiter('stack_create_complete')

    res = waiter.wait(StackName=stack_name)
    if verbose:
        pprint(res, indent=2)
        sys.stdout.flush()

    res = client.describe_stacks(StackName=stack_name)
    if verbose:
        verbose_result(res)
    outputs = dict(
        (o['OutputKey'], o['OutputValue'])
        for o in res['Stacks'][0]['Outputs']
    )
    if verbose:
        verbose_result(outputs)
    queue_arn = outputs['oQueueArn']

    client = boto3.client('s3')
    res = client.put_bucket_notification_configuration(
        Bucket=opts.bucket,
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
        })
    if verbose:
        verbose_result(res)

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
    parser.add_argument(
        '--bucket', metavar='NAME',
        default=DFLT_BUCKET_NAME,
        help='specify the bucket name'
    )
    parser.add_argument(
        '--queue', metavar='URL',
        default=DFLT_QUEUE_URL,
        help='specify the queue url'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='count', default=0,
        help='increase verbosity'
    )

    sp = parser.add_subparsers(title="command(s)")
    create = sp.add_parser(
        'create',
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
        help='push local files to the queue'
    )
    push.set_defaults(func=push_command)

    pull = sp.add_parser(
        'pull',
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
    return opts.func(opts)


def main():
    return main_guts(sys.argv)


if __name__ == '__main__':
    main()
