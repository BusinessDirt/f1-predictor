from Logger import Logger
from API import API
from RaceMetrics import RaceMetrics

logger = Logger(name="f1-predictor", log_file="logs/f1-predictor.log")

api = API(logger, "./cache")
api.set_log_level('ERROR')


def print_schedule():
    schedule = api.get_event_schedule(2025).sort_values(by='RoundNumber')
    for _, event in schedule.iterrows():
        print(f"Round {event['RoundNumber']} - {event['Location']} in {event['Country']}")


race_metrics = RaceMetrics(api, logger, 2025, 'Spain')
overtakes = race_metrics.average_overtakes(5)
print(overtakes)