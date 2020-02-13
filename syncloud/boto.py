import boto3


class BotoClients():
    """
    Wraps creation of boto3 clients so that they can be managed,
    and stubber can be used during testing.
    """

    def __init__(self):
        self._clients = {}

    def client(self, name):
        cli = self._clients.get(name)
        if not cli:
            self._clients[name] = cli = boto3.client(name)
        return cli

    @property
    def s3(self):
        return self.client('s3')

    @property
    def cloudformation(self):
        return self.client('cloudformation')

    @property
    def sqs(self):
        return self.client('sqs')


boto_clients = BotoClients()
