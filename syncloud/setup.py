from uuid import uuid4


from .boto import boto_clients
from .utils import log_result, get_queue_details


def create_stack(template_path, bucket_name, queue_name):
    stack_name = 'syncloud-' + str(uuid4())
    with open(template_path, 'r', encoding='UTF-8') as f:
        template = f.read()
    parameters = {
        'pBucketName': bucket_name,
        'pQueueName': queue_name
    }

    client = boto_clients.cloudformation
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


def setup_bucket_notification(bucket_name, queue_name):
    queue_url, queue_arn = get_queue_details(queue_name)

    client = boto_clients.s3
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
