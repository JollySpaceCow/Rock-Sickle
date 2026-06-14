import os
import json
import logging
from src.core.paths import get_progress_dir

logger = logging.getLogger(__name__)


def _load_json(path: str, default):
    """Load a JSON file, returning *default* if the file does not exist or is invalid."""
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {path}: {e}")
    return default


def _save_json(path: str, data):
    """Write *data* to *path* atomically using a temporary file."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception as e:
        logger.error(f"Error saving JSON to {path}: {e}")


def load_game_progress():
    """Load all progress fragments and return a combined dictionary.

    The structure mirrors the original monolithic JSON but each domain is stored in its own file
    under the ``progress`` directory inside the user data folder.
    """
    defaults = {
        "classic_board_completed": False,
        "expert_board_completed": False,
        "secret_board_completed": False,
        "classic_no_jail_completed": False,
        "expert_no_jail_completed": False,
        "unlocked_boards": ["Classic"],
        "completed_games": 0,
        "completed_achievements": [],
        "unlocked_gallery_items": [],
        "stats": {
            "jail_landings": 0,
            "quiz_correct": 0,
            "hard_cpu_defeats": 0,
            "bonus_cards_picked": 0,
        },
        "settings": {
            "godmode": False,
            "godmode_mute": False,
            "godmode_tile": "B",
            "master_volume": 1.0,
            "show_game_status": False,
            "use_modern_status_display": True,
            "show_timers": False,
            "speak_quiz_questions": True,
            "speak_quiz_answers": True,
            "use_device_tts": False,
        },
    }

    progress_dir = get_progress_dir()
    os.makedirs(progress_dir, exist_ok=True)

    # Load each fragment, falling back to the appropriate slice of defaults.
    settings = _load_json(os.path.join(progress_dir, "settings.json"), defaults["settings"])
    stats = _load_json(os.path.join(progress_dir, "stats.json"), defaults["stats"])
    unlocks = _load_json(
        os.path.join(progress_dir, "unlocks.json"),
        {"unlocked_boards": defaults["unlocked_boards"], "unlocked_gallery_items": defaults["unlocked_gallery_items"]},
    )
    achievements = _load_json(
        os.path.join(progress_dir, "achievements.json"), defaults["completed_achievements"]
    )
    game_state = _load_json(
        os.path.join(progress_dir, "game_state.json"),
        {k: v for k, v in defaults.items() if k not in ("settings", "stats", "unlocked_boards", "unlocked_gallery_items", "completed_achievements")},
    )

    # Merge fragments into a single dict expected by the rest of the code.
    progress = {
        **game_state,
        "settings": settings,
        "stats": stats,
        "unlocked_boards": unlocks.get("unlocked_boards", []),
        "unlocked_gallery_items": unlocks.get("unlocked_gallery_items", []),
        "completed_achievements": achievements,
    }
    return progress


def save_game_progress(progress: dict):
    """Persist the supplied *progress* dictionary into separate JSON files.

    Each domain is written to its own file under the ``progress`` directory.
    """
    progress_dir = get_progress_dir()
    os.makedirs(progress_dir, exist_ok=True)

    # Settings and stats are straightforward.
    _save_json(os.path.join(progress_dir, "settings.json"), progress.get("settings", {}))
    _save_json(os.path.join(progress_dir, "stats.json"), progress.get("stats", {}))

    # Unlocks combine two lists.
    _save_json(
        os.path.join(progress_dir, "unlocks.json"),
        {
            "unlocked_boards": progress.get("unlocked_boards", []),
            "unlocked_gallery_items": progress.get("unlocked_gallery_items", []),
        },
    )

    # Achievements list.
    _save_json(
        os.path.join(progress_dir, "achievements.json"),
        progress.get("completed_achievements", []),
    )

    # Anything not part of the above categories goes into game_state.json.
    exclude_keys = {
        "settings",
        "stats",
        "unlocked_boards",
        "unlocked_gallery_items",
        "completed_achievements",
    }
    game_state = {k: v for k, v in progress.items() if k not in exclude_keys}
    _save_json(os.path.join(progress_dir, "game_state.json"), game_state)


def increment_stat(stat_name, amount=1):
    """Increment a specific game statistic in the progress file."""
    progress = load_game_progress()
    progress.setdefault("stats", {})
    progress["stats"][stat_name] = progress["stats"].get(stat_name, 0) + amount
    save_game_progress(progress)
    return progress
