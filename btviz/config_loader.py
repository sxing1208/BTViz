import json
from .btviz_exceptions import *


def load_config(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        raise ConfigurationError(f"Error loading or parsing config file {file_path}: {e}")
    