from pathlib import Path


def get_project_root() -> Path:
    """Folder that contains `data/`, `app.py`, and `src/`."""
    return Path(__file__).resolve().parent.parent
