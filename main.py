from Logger import Logger
from API import API

from RacePace import RacePace
from Overtakes import Overtakes
from ConstructorStandings import ConstructorStandings

logger = Logger(name="f1-predictor", log_file="logs/f1-predictor.log")

api = API(logger, "f1-cache")
api.set_log_level('ERROR')


def print_schedule():
    schedule = api.get_event_schedule(2025).sort_values(by='RoundNumber')
    for _, event in schedule.iterrows():
        print(f"Round {event['RoundNumber']} - {event['Location']} in {event['Country']}")


compound_weights = {
    'SOFT': 0.2,
    'MEDIUM': 0.4,
    'HARD': 0.4,
}

overtakes = Overtakes(api, logger, "data/overtakes.json", 5)
race_pace = RacePace(api, logger, 2025, 'Barcelona', compound_weights, 5)
constructor_standings = ConstructorStandings(api, logger)

print(overtakes)
print(race_pace)
print(constructor_standings)