import os
import json
import logging

logger = logging.getLogger()

def get_progress_file_path():
    """Get path to the game progress file."""
    # Store in same directory as the root script
    return os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "rock_sickle_progress.json")

def load_game_progress():
    """Load game progress and settings from file and ensure all keys exist."""
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
            "bonus_cards_picked": 0
        },
        "settings": {
            "master_volume": 1.0,
            "show_game_status": False,
            "use_modern_status_display": True,
            "show_timers": False,
            "speak_quiz_questions": True,
            "speak_quiz_answers": True
        }
    }
    
    try:
        progress_path = get_progress_file_path()
        if os.path.exists(progress_path):
            with open(progress_path, 'r') as f:
                loaded = json.load(f)
                # Merge loaded progress into defaults to handle missing keys
                for key, value in loaded.items():
                    if isinstance(value, dict) and key in defaults:
                        defaults[key].update(value)
                    else:
                        defaults[key] = value
                return defaults
    except Exception as e:
        logger.error(f"Error loading game progress: {e}")
    
    return defaults

def save_game_progress(progress):
    """Save game progress to file."""
    try:
        progress_path = get_progress_file_path()
        with open(progress_path, 'w') as f:
            json.dump(progress, f)
    except Exception as e:
        logger.error(f"Error saving game progress: {e}")

def increment_stat(stat_name, amount=1):
    """Increment a specific game statistic in the progress file."""
    progress = load_game_progress()
    if "stats" not in progress:
        progress["stats"] = {}
    
    progress["stats"][stat_name] = progress["stats"].get(stat_name, 0) + amount
    save_game_progress(progress)
    return progress
