import os
import json
import logging

logger = logging.getLogger()

def get_progress_file_path():
    """Get path to the game progress file."""
    # Store in same directory as the root script
    return os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "rock_sickle_progress.json")

def load_game_progress():
    """Load game progress and settings from file."""
    try:
        progress_path = get_progress_file_path()
        if os.path.exists(progress_path):
            with open(progress_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading game progress: {e}")
    
    # Default progress and settings if file doesn't exist or there's an error
    return {
        "classic_board_completed": False,
        "unlocked_boards": ["Classic"],
        "completed_games": 0,
        "settings": {
            "master_volume": 1.0,           # 100% volume by default
            "show_game_status": False,      # Game status off by default
            "use_modern_status_display": True,  # Modern status display on by default
            "show_timers": False            # Show timers off by default
        }
    }

def save_game_progress(progress):
    """Save game progress to file."""
    try:
        progress_path = get_progress_file_path()
        with open(progress_path, 'w') as f:
            json.dump(progress, f)
    except Exception as e:
        logger.error(f"Error saving game progress: {e}")
