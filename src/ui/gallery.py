import pygame
import time
from src.core.assets import load_asset
from src.core.progress import load_game_progress
from src.game.achievements import ACHIEVEMENTS

# Constants for the achievements pane
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GREY = (50, 50, 50)
GOLD = (255, 215, 0)
PANE_BG = (40, 40, 40, 230)  # Dark translucent background

def render_achievements_pane(screen, scale, offset_x, offset_y, board_type="Classic"):
    """Render the achievements as a pop-up pane within the main game screen."""
    from src.game.achievements import check_achievement_completion, get_achievement_by_id
    from src.core.progress import save_game_progress
    
    game_progress = load_game_progress()
    
    # Retroactively check for achievement completion
    newly_completed = check_achievement_completion(game_progress)
    if newly_completed:
        if 'completed_achievements' not in game_progress:
            game_progress['completed_achievements'] = game_progress.get('completed_quests', [])
            
        for a_id in newly_completed:
            if a_id not in game_progress['completed_achievements']:
                game_progress['completed_achievements'].append(a_id)
                achievement = get_achievement_by_id(a_id)
                if achievement and "reward" in achievement:
                    if 'unlocked_gallery_items' not in game_progress:
                        game_progress['unlocked_gallery_items'] = []
                    if achievement["reward"] not in game_progress['unlocked_gallery_items']:
                        game_progress['unlocked_gallery_items'].append(achievement["reward"])
        save_game_progress(game_progress)
        
    completed_achievements = game_progress.get("completed_achievements", game_progress.get("completed_quests", []))
    stats = game_progress.get("stats", {})
    
    # Pane sizing and positioning
    pane_width = int(600 * scale)
    pane_height = int(450 * scale)
    pane_x = int((screen.get_width() // 2) - (pane_width // 2))
    pane_y = int((screen.get_height() // 2) - (pane_height // 2))
    pane_rect = pygame.Rect(pane_x, pane_y, pane_width, pane_height)
    
    # Draw translucent background
    bg_surface = pygame.Surface((pane_width, pane_height), pygame.SRCALPHA)
    bg_surface.fill(PANE_BG)
    screen.blit(bg_surface, (pane_x, pane_y))
    
    # Draw border
    pygame.draw.rect(screen, GOLD if board_type == "Expert" else GRAY, pane_rect, width=int(2 * scale), border_radius=int(10 * scale))
    
    # Fonts
    title_font = pygame.font.SysFont(None, int(48 * scale))
    font = pygame.font.SysFont(None, int(22 * scale))
    subtitle_font = pygame.font.SysFont(None, int(28 * scale))
    
    # Draw Title
    title_surf = title_font.render("Achievements", True, GOLD)
    screen.blit(title_surf, (pane_rect.centerx - title_surf.get_width() // 2, pane_y + int(20 * scale)))
    
    # Draw Achievements list
    achievement_y_start = pane_y + int(80 * scale)
    achievement_spacing = int(60 * scale)
    
    for i, achievement in enumerate(ACHIEVEMENTS):
        is_completed = achievement["id"] in completed_achievements
        color = GOLD if is_completed else GRAY
        
        # Calculate current progress
        req = achievement["requirement"]
        stat_name = req["stat"]
        target_val = req["value"]
        
        current_val = stats.get(stat_name, 0)
        # Handle special cases for top-level progress keys
        if stat_name == "completed_games":
            current_val = game_progress.get("completed_games", 0)
        elif stat_name == "expert_board_completed":
            current_val = 1 if game_progress.get("expert_board_completed", False) else 0
        elif stat_name == "secret_board_completed":
            current_val = 1 if game_progress.get("secret_board_completed", False) else 0
            
        # Ensure current value doesn't exceed target for the display
        display_val = min(current_val, target_val)
        
        # Achievement box
        a_box_rect = pygame.Rect(pane_x + int(20 * scale), achievement_y_start + i * achievement_spacing, pane_width - int(40 * scale), int(55 * scale))
        pygame.draw.rect(screen, DARK_GREY, a_box_rect, border_radius=int(5 * scale))
        if is_completed:
            pygame.draw.rect(screen, GOLD, a_box_rect, width=int(1 * scale), border_radius=int(5 * scale))
        
        # Achievement Title
        a_title = font.render(achievement["title"], True, color)
        screen.blit(a_title, (a_box_rect.x + int(10 * scale), a_box_rect.y + int(8 * scale)))
        
        # Achievement Description
        a_desc = font.render(achievement["description"], True, WHITE if is_completed else GRAY)
        screen.blit(a_desc, (a_box_rect.x + int(10 * scale), a_box_rect.y + int(28 * scale)))
        
        # Status / Progress
        if is_completed:
            status_text = "COMPLETED!"
        else:
            status_text = f"{display_val}/{target_val}"
            
        status_surf = font.render(status_text, True, color)
        screen.blit(status_surf, (a_box_rect.right - status_surf.get_width() - int(10 * scale), a_box_rect.y + int(18 * scale)))

    # Return the pane rect so main loop can handle clicks outside it to close
    return pane_rect
