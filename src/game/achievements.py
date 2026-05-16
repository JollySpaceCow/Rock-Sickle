"""
Module for managing game achievements and completion logic.
All achievements and their requirements are defined here.
"""

# Define the achievements available in the game
ACHIEVEMENTS = [
    {
        "id": "first_steps",
        "title": "First Steps",
        "description": "Complete your first game on any board.",
        "requirement": {"stat": "completed_games", "value": 1},
        "reward": "Gallery Entry: Early Sketches"
    },
    {
        "id": "jailbird",
        "title": "Jailbird",
        "description": "Land in jail 10 times.",
        "requirement": {"stat": "jail_landings", "value": 10},
        "reward": "Gallery Entry: The Prisoner's Dilemma"
    },
    {
        "id": "expert_navigator",
        "title": "Expert Navigator",
        "description": "Complete the Expert board.",
        "requirement": {"stat": "expert_board_completed", "value": 1},
        "reward": "Gallery Entry: Map of the Stars"
    },
    {
        "id": "marathon_runner",
        "title": "Marathon Runner",
        "description": "Complete the 1000-space Secret board.",
        "requirement": {"stat": "secret_board_completed", "value": 1},
        "reward": "Gallery Entry: The Golden Medal"
    },
    {
        "id": "quiz_master",
        "title": "Quiz Master",
        "description": "Answer 20 quiz questions correctly.",
        "requirement": {"stat": "quiz_correct", "value": 20},
        "reward": "Gallery Entry: Knowledge is Power"
    },
    {
        "id": "cpu_crusher",
        "title": "CPU Crusher",
        "description": "Win a game where a Hard CPU player is competing.",
        "requirement": {"stat": "hard_cpu_defeats", "value": 1},
        "reward": "Gallery Entry: Silicon Tears"
    }
]

def check_achievement_completion(progress):
    """
    Check if any new achievements have been completed based on the current progress stats.
    Returns a list of newly completed achievement IDs.
    """
    newly_completed = []
    # Support both old 'completed_quests' and new 'completed_achievements' keys for migration
    completed_ids = progress.get("completed_achievements", progress.get("completed_quests", []))
    stats = progress.get("stats", {})
    
    for achievement in ACHIEVEMENTS:
        if achievement["id"] in completed_ids:
            continue
            
        req = achievement["requirement"]
        stat_name = req["stat"]
        target_val = req["value"]
        
        # Check if the stat meets the requirement
        current_val = stats.get(stat_name, 0)
        
        # Special case for board completion flags which might be top-level
        if stat_name == "completed_games":
            current_val = progress.get("completed_games", 0)
        elif stat_name == "expert_board_completed":
            current_val = 1 if progress.get("expert_board_completed", False) else 0
        elif stat_name == "secret_board_completed":
            current_val = 1 if progress.get("secret_board_completed", False) else 0
            
        if current_val >= target_val:
            newly_completed.append(achievement["id"])
            
    return newly_completed

def get_achievement_by_id(achievement_id):
    """Find an achievement by its ID."""
    for achievement in ACHIEVEMENTS:
        if achievement["id"] == achievement_id:
            return achievement
    return None
