import json

from Logger import Logger
from Serialize import Serializer
from API import API

from datetime import datetime
from typing import Union


class Overtakes:
    def __init__(self, api: API, logger: Logger, file, years: int = 5):
        self.file = file
        self.log = logger
        self.api = api
        self.years = years
        self.data = Serializer.load(self.file)

        if self.data == {}:
            self.log.info("Updating overtake data: no data found")
            self._normalize()
        elif 'year' in self.data.keys():
            if self.data['year'] < datetime.now().year:
                self.log.info('Updating overtake data: outdated')
                self._normalize()

    def _normalize(self):
        current_year = datetime.now().year
        schedule = self.api.get_event_schedule(current_year).sort_values(by='RoundNumber')
        schedule = schedule[schedule['Session5Date'].notna()]

        locations = schedule['Location'].tolist()
        overtakes = [(location, self._average_overtakes(self.years, location)) for location in locations]
        overtakes.sort(key=lambda o: o[1], reverse=True)
        average_overtakes = sum([o for _, o in overtakes]) / len(overtakes)

        self.data['year'] = current_year
        self.data['overtakes'] = {}
        for location, overtake in overtakes:
            self.data['overtakes'][location] = round(overtake / average_overtakes, 3)

        Serializer.save(self.data, self.file)

    def _average_overtakes(self, n: int, gp: Union[str, int]):
        """
        Calculates the average overtakes for the track during the race
        :param gp: the gp to calculate the average overtakes for
        :param n: the years to average overtakes for
        :return: average overtakes
        """
        current_year = datetime.now().year
        years = list(range(max(current_year - n, 2018), current_year))  # fastf1 supports race data only up to 2018
        overtakes_per_year = []

        self.log.debug(f"Collecting overtakes for {years} - {gp}")

        for y in years:
            if not self.api.gp_in_schedule(y, gp):
                self.log.debug(f"Skipping {y}: event not in schedule ({gp})")
                continue

            session = self.api.get_session(y, gp, 'R')
            session.load(laps=True, telemetry=False, weather=False, messages=False)

            # Grouping the laps by stint and adding up the overtakes separately doesn't change a lot
            # It also considers the possibility of an under- or overcut and packs the numbers a bit closer
            overtake_count = 0
            for driver in session.drivers:
                laps = session.laps.pick_drivers([driver]).sort_values(by='LapNumber')
                laps = laps[laps['PitInTime'].isna() & laps['PitOutTime'].isna()]

                positions = laps['Position'].values
                overtake_count += sum(positions[i] < positions[i - 1] for i in range(1, len(positions)))

            overtakes_per_year.append(overtake_count)
            self.log.debug(f"Overtakes in {y}: {overtake_count}")

        return sum(overtakes_per_year) / len(overtakes_per_year)

    def __repr__(self):
        return json.dumps(self.data, indent=4)