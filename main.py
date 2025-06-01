from API import API

api = API("./cache")
api.set_log_level('ERROR')

schedule = api.get_event_schedule(2025)
print(schedule)
