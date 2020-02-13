from botocore.client import BaseClient
from syncloud.boto import BotoClients, boto_clients


def test_isinstance():
    assert isinstance(boto_clients, BotoClients)


def test_caches_s3_client():
    clients = BotoClients()
    a = clients.client('s3')
    b = clients.client('s3')
    assert a is b
    assert isinstance(a, BaseClient)
    assert a is clients.s3


def test_caches_sqs_client():
    clients = BotoClients()
    a = clients.client('sqs')
    b = clients.client('sqs')
    assert a is b
    assert isinstance(a, BaseClient)
    assert a is clients.sqs


def test_caches_cloudformation_client():
    clients = BotoClients()
    a = clients.client('cloudformation')
    b = clients.client('cloudformation')
    assert a is b
    assert isinstance(a, BaseClient)
    assert a is clients.cloudformation
