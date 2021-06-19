from .logging import start_logger
from .config import Config, get_config
from .httpclient import MBTAClient
from .state import SQLITE3Datastore


class Project:
    def __init__(self, config_path: str):
        self.config = get_config(config_path)
        self.log = start_logger(self.config)
        self.client = MBTAClient(log=self.log, config=self.config)
        self.state = SQLITE3Datastore(log=self.log, filepath=self.config.DatabasePath)
        self.get_all_routes()

    def get_all_routes(self):
        routes = self.client.get_routes()
        print(routes)