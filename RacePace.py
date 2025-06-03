import json
import numpy as np
from typing import Union, Dict

from API import API
from Logger import Logger
from Utils import event_format_practice_session_count, sort_dict_by_value


class RacePace:
    def __init__(self, api: API, logger: Logger, year: int, gp: Union[str, int], compound_weights: Dict[str, float],
                 min_stint_length: int = 5) -> None:
        self.api: API = api
        self.log: Logger = logger
        self.year: int = year
        self.gp: Union[str, int] = gp
        self.compound_weights: Dict[str, float] = compound_weights
        self.min_stint_length: int = min_stint_length
        self.data = sort_dict_by_value(self._normalize(), descending=True)

    def _normalize(self):
        pace_data = self._race_pace()

        compound_to_driver_times = {}

        # Step 1: Gather lap times by compound
        for driver, compounds in pace_data.items():
            for compound, pace in compounds.items():
                compound = compound.upper()
                if compound not in self.compound_weights:
                    continue
                if pace is None or not np.isfinite(pace):
                    continue
                compound_to_driver_times.setdefault(compound, {})[driver] = pace

        # Step 2: Normalize per-compound scores
        per_driver_scores = {}

        for compound, times in compound_to_driver_times.items():
            values = list(times.values())
            if not values:
                continue

            for driver, pace in times.items():
                per_driver_scores.setdefault(driver, []).append((
                    min(values) / pace,
                    self.compound_weights[compound]  # compound guaranteed to be in weights
                ))

        # Step 3: Weighted average per driver
        data = {}
        for driver, score_weight_pairs in per_driver_scores.items():
            total_weight = sum(w for _, w in score_weight_pairs)
            if total_weight > 0:
                weighted_sum = sum(score * weight for score, weight in score_weight_pairs)
                data[driver] = weighted_sum / total_weight

        return data

    def _race_pace(self):
        """
        Calculates the race pace per driver using the data from the free practice sessions
        :return:
        """
        self.log.debug(f"Collecting race pace ({self.gp} {self.year})")

        schedule = self.api.get_event_schedule(self.year)
        event_format = schedule.get_event_by_name(self.gp)['EventFormat']

        pace = {}
        for i in range(event_format_practice_session_count(event_format)):
            session = self.api.get_session(self.year, self.gp, f"FP{i + 1}")
            session.load(laps=True, telemetry=False, weather=False, messages=False)
            laps = session.laps.pick_accurate().pick_quicklaps(1.15)

            for driver in laps['Driver'].unique():
                driver_laps = laps.pick_drivers([driver])
                compound_groups = driver_laps.groupby('Compound')

                if driver not in pace.keys():
                    pace[driver] = {}

                for compound, group in compound_groups:
                    if len(group) >= self.min_stint_length:
                        new_time = group['LapTime'].mean().total_seconds()
                        if compound not in pace[driver].keys():
                            pace[driver][compound] = new_time
                        else:
                            if new_time < pace[driver][compound]:
                                pace[driver][compound] = new_time

        return pace

    def __repr__(self):
        return json.dumps(self.data, indent=4)
