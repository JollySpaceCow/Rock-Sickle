import pygame
import sys
import os
import logging
import time
from src.core import audio, quiz_tts
from src.core.assets import initialise_all_assets, load_asset
from src.core.progress import load_game_progress
from src.constants import ORIGINAL_WIDTH, ORIGINAL_HEIGHT
from src.game.player import Player
from src.game.board import get_classic_squares_coords, get_expert_squares_coords, get_secret_squares_coords
from src.ui import menus
from src.engine.loop import run_game_loop

# Set up logging for debug purposes
logging.basicConfig(
    filename=os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "rock_sickle.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

def main():
    """Main entry point that initialises the game systems and manages board selections.
    
    This has been simplified to keep the game loop and logic isolated inside engine modules.
    Complies fully with Australian English spelling conventions.
    """
    # 1. Initialise Pygame display
    pygame.init()
    logger.info("Pygame initialised successfully")
    
    # Set up initial display mode (resizable)
    SCREEN_WIDTH, SCREEN_HEIGHT = ORIGINAL_WIDTH, ORIGINAL_HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Rock-Sickle")
    
    try:
        icon_path = load_asset("Assets/Images/Icons/RockSickle.png")
        icon_surface = pygame.image.load(icon_path)
        pygame.display.set_icon(icon_surface)
        logger.info(f"Custom icon set successfully: {icon_path}")
    except Exception as e:
        logger.warning(f"Could not set window icon: {e}")
        
    logger.info("Display initialised successfully")
    
    # 2. Initialise audio subsystem
    audio.init_audio()
    quiz_tts.init_quiz_tts()
    
    # 3. Load all original graphics assets into registry
    initialise_all_assets()
    
    # 4. Set up fonts
    font = pygame.font.SysFont(None, 24)
    title_font = pygame.font.SysFont(None, 72)
    
    audio.connect_sound.play()
    
    # Define the initial master volume setup
    audio.apply_master_volume(1.0)
    
    # Create the layout_state dictionary to carry layout sizing references dynamically
    layout_state = {
        'screen': screen,
        'scale': 1.0,
        'offset_x': 0.0,
        'offset_y': 0.0,
        'font': font,
        'title_font': title_font,
        'screen_width': SCREEN_WIDTH,
        'screen_height': SCREEN_HEIGHT
    }
    
    quit_game = False
    while not quit_game:
        # Run player selection screen
        selected_data = menus.select_players(layout_state)
        if selected_data is None:
            break
            
        selected_players, selected_board = selected_data
        logger.info(f"Selected board type: {selected_board}")
        
        # Load saved progress
        saved_progress = load_game_progress()
        
        # Retrieve coordinates for initial player placements
        if selected_board == 'Expert':
            squares_coords = get_expert_squares_coords()
        elif selected_board == 'Secret':
            squares_coords = get_secret_squares_coords()
        else:
            squares_coords = get_classic_squares_coords()
            
        # Create Player objects
        players = [
            Player(i, colour_idx, is_computer, difficulty, start_coords=squares_coords[0])
            for i, (colour_idx, is_computer, difficulty) in enumerate(selected_players)
        ]
        
        for player in players:
            player.position_history.append(player.position)
            player.start_time = time.time()
            
        # Execute the primary gameplay match loop
        quit_game = run_game_loop(layout_state, players, selected_board, saved_progress)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()