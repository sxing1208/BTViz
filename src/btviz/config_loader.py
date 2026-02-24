import json
from pathlib import Path

def load_config():
    """
    Load packaged config.json.

    Works for:
    - editable installs / normal python
    - wheels
    - PyInstaller --onefile / --onedir
    """
    try:
        from importlib.resources import files
        cfg = files("btviz").joinpath("data/config.json")
        return json.loads(cfg.read_text(encoding="utf-8"))
    except Exception:
        pass

    try:
        import sys
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        cfg = base / "data" / "config.json"
        return json.loads(cfg.read_text(encoding="utf-8"))
    except Exception as e:
        raise FileNotFoundError(
            "Could not locate bundled config.json. "
            "Make sure PyInstaller includes it at data/config.json"
        ) from e