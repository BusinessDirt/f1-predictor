import os

import fastf1
from fastf1.core import Session, DriverResult
from fastf1.events import EventSchedule
from fastf1.ergast import Ergast

import logging
from typing import Union, List, Optional, Literal

from Logger import Logger


class API:
    def __init__(self, logger: Logger, cache_dir: str):
        self.f1 = fastf1
        self.ergast = Ergast()
        self.log: Logger = logger
        self.cache_dir = cache_dir

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.f1.Cache.enable_cache(self.cache_dir)

    def set_log_level(self, level: Union[str, int]):
        self.f1.set_log_level(level)

    def get_session(self, year: int, gp: Union[str, int], identifier: str) -> Session:
        return self.f1.get_session(year, gp, identifier)

    def get_event_schedule(self, year: int) -> EventSchedule:
        return self.f1.get_event_schedule(year)

    def gp_in_schedule(self, year: int, gp: Union[str, int]) -> bool:
        schedule = self.get_event_schedule(year)
        for _, event in schedule.iterrows():
            if type(gp) is str:
                if gp.lower() in event['EventName'].lower() or \
                        gp.lower() in event['Location'].lower() or \
                        gp.lower() in event['Country'].lower():
                    return True
            else:
                if gp is event['RoundNumber']:
                    return True

        return False

    def get_constructor_standings(self, year: int):
        return self.ergast.get_constructor_standings(year)

    @staticmethod
    def get_drivers(session: Session) -> List[DriverResult]:
        return [session.get_driver(driver) for driver in session.drivers]
