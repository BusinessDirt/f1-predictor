from typing import Union
from datetime import datetime

from API import API
from Logger import Logger


class RaceMetrics:
    def __init__(self, api: API, logger: Logger, year: int, gp: Union[str, int]) -> None:
        self.api: API = api
        self.log: Logger = logger
        self.year: int = year
        self.gp: Union[str, int] = gp

    def average_overtakes(self, n: int):
        """
        Calculates the average overtakes for the track during the race
        :param n: the years to average overtakes for
        :return: average overtakes
        """
        current_year = datetime.now().year
        years = list(range(max(current_year - n, 2018), current_year))  # fastf1 supports race data only up to 2018
        overtakes_per_year = []

        self.log.info(f"Collecting overtakes for {years}")

        for year in years:
            if not self.api.gp_in_schedule(year, self.gp):
                self.log.warning(f"Skipping {year}: event not in schedule ({self.gp})")
                continue

            session = self.api.get_session(year, self.gp, 'R')
            session.load(laps=True, telemetry=False, weather=False, messages=False)

            overtake_count = 0
            for driver in session.drivers:
                laps = session.laps.pick_drivers([driver]).sort_values(by='LapNumber')
                positions = laps['Position'].values
                overtake_count += sum(positions[i] < positions[i - 1] for i in range(1, len(positions)))

            overtakes_per_year.append(overtake_count)
            self.log.info(f"Overtakes in {year}: {overtake_count}")

        return sum(overtakes_per_year) / len(overtakes_per_year)
