from valclient.client import Client as BaseClient


class Client(BaseClient):
    def __init__(self, region="ap"):
        super().__init__(region=region)