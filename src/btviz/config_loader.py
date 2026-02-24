import json
from importlib.resources import files

def load_config():
    """Load the packaged default config at btviz/data/config.json."""
    cfg = files("btviz").joinpath("data/config.json")
    return json.loads(cfg.read_text(encoding="utf-8"))