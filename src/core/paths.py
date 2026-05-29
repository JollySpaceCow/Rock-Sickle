import os
import sys
import tempfile


APP_DIR_NAME = "Rock Sickle"
APP_ID = "rock-sickle"


def _home_dir():
    return os.path.expanduser("~")


def get_user_data_dir():
    """Return a stable, user-writable directory for saved player data."""
    if sys.platform.startswith("win"):
        base_dir = os.environ.get("APPDATA") or os.path.join(_home_dir(), "AppData", "Roaming")
        return os.path.join(base_dir, APP_DIR_NAME)

    if sys.platform == "darwin":
        return os.path.join(_home_dir(), "Library", "Application Support", APP_DIR_NAME)

    base_dir = os.environ.get("XDG_DATA_HOME") or os.path.join(_home_dir(), ".local", "share")
    return os.path.join(base_dir, APP_ID)


def get_user_log_dir():
    """Return a stable, user-writable directory for logs."""
    if sys.platform.startswith("win"):
        return get_user_data_dir()

    if sys.platform == "darwin":
        return os.path.join(_home_dir(), "Library", "Logs", APP_DIR_NAME)

    base_dir = os.environ.get("XDG_STATE_HOME") or os.path.join(_home_dir(), ".local", "state")
    return os.path.join(base_dir, APP_ID)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def get_progress_file_path():
    return os.path.join(ensure_dir(get_user_data_dir()), "rock_sickle_progress.json")


def get_log_file_path():
    try:
        return os.path.join(ensure_dir(get_user_log_dir()), "rock_sickle.log")
    except OSError:
        return os.path.join(tempfile.gettempdir(), "rock_sickle.log")


def get_legacy_progress_file_path():
    """Return the old app-adjacent progress location used by previous builds."""
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    return os.path.join(project_root, "rock_sickle_progress.json")
