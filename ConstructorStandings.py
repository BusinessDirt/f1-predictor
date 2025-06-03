from API import API
from Logger import Logger
from datetime import datetime


class ConstructorStandings:
    def __init__(self, api: API, logger: Logger):
        self.api: API = api
        self.log: Logger = logger

        self.data = self.api.get_constructor_standings(datetime.now().year).content
        self.data = self.data[0].to_dict(orient='records')

    def __repr__(self):
        return str(self.data)
