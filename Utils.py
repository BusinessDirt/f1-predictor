import json


def event_format_practice_session_count(event_format: str) -> int:
    if event_format == "conventional":
        return 3
    elif event_format == "sprint":
        return 2
    elif event_format == "sprint_shootout" or event_format == "sprint_qualifying":
        return 1
    else:
        return 0


def sort_dict_by_value(data: dict[str, float], descending: bool = True) -> dict[str, float]:
    return dict(sorted(data.items(), key=lambda item: item[1], reverse=descending))
