import os
import sys
import tempfile

# Application directory names
APP_DIR_NAME = "Rock Sickle"
APP_ID = "rock-sickle"

def _home_dir() -> str:
    """Return the user's home directory."""
    return os.path.expanduser("~")

def get_user_data_dir() -> str:
    """Return a stable, user‑writable directory for saved player data."""
    if sys.platform.startswith("win"):
        base_dir = os.environ.get("APPDATA") or os.path.join(_home_dir(), "AppData", "Roaming")
        return os.path.join(base_dir, APP_DIR_NAME)

    if sys.platform == "darwin":
        return os.path.join(_home_dir(), "Library", "Application Support", APP_DIR_NAME)

    base_dir = os.environ.get("XDG_DATA_HOME") or os.path.join(_home_dir(), ".local", "share")
    return os.path.join(base_dir, APP_ID)

def get_user_log_dir() -> str:
    """Return a stable, user‑writable directory for logs."""
    if sys.platform.startswith("win"):
        return get_user_data_dir()

    if sys.platform == "darwin":
        return os.path.join(_home_dir(), "Library", "Logs", APP_DIR_NAME)

    base_dir = os.environ.get("XDG_STATE_HOME") or os.path.join(_home_dir(), ".local", "state")
    return os.path.join(base_dir, APP_ID)

def ensure_dir(path: str) -> str:
    """Create *path* if it does not exist and return it."""
    os.makedirs(path, exist_ok=True)
    return path

def get_progress_dir() -> str:
    """Return the directory that stores split progress JSON files.

    The directory is created if it does not already exist.
    """
    return ensure_dir(os.path.join(get_user_data_dir(), "progress"))

def get_progress_file_path() -> str:
    """Legacy helper – returns the old monolithic progress file location.

    This is retained for migration purposes only.
    """
    return os.path.join(ensure_dir(get_user_data_dir()), "rock_sickle_progress.json")

def get_log_file_path() -> str:
    """Return the path to the log file, ensuring its directory exists."""
    try:
        return os.path.join(ensure_dir(get_user_log_dir()), "rock_sickle.log")
    except OSError:
        return os.path.join(tempfile.gettempdir(), "rock_sickle.log")
