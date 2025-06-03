import json
import os


class Serializer:
    @staticmethod
    def save(data: dict, filepath: str) -> None:
        if not isinstance(data, dict):
            raise TypeError("Serializer only supports dictionaries.")

        # Ensure directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Write JSON to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load(filepath: str) -> dict:
        if not os.path.isfile(filepath):
            return {}

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise TypeError("Loaded JSON is not a dictionary.")

        return data
