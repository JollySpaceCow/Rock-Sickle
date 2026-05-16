import pygame
import random
import time
import sys
import os
import traceback
from src.core import audio
import logging
import math
import json

from src.constants import (
    ORIGINAL_WIDTH, ORIGINAL_HEIGHT,
    WHITE, BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, GRAY, PINK, DULL_PINK, DARK_GREY, GOLD, DARK_GREEN,
    player_colours,
    GAP_BETWEEN_TILES,
    CLASSIC_JAIL_POS, EXPERT_JAIL_POS, SECRET_JAIL_POS,
    DIE_POS, JAIL_SIZE
)
from src.core.progress import get_progress_file_path, load_game_progress, save_game_progress, increment_stat
from src.core.assets import load_asset
from src.game.board import (
    get_board_squares, get_classic_squares_coords, get_expert_squares_coords, get_secret_squares_coords
)
from src.game.player import Player
from src.game.achievements import ACHIEVEMENTS, check_achievement_completion, get_achievement_by_id
from src.ui.gallery import render_achievements_pane


# Set up logging for debug purposes
logging.basicConfig(
    filename=os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "rock_sickle.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# Global variables for scaled images
player_images_scaled = []
cpu_image_scaled = None
cpu_difficulty_images_scaled = {}  # Dictionary to hold scaled CPU difficulty images
dice_images_scaled = []
tile_images_scaled = {}
restart_button_scaled = None
settings_button_scaled = None
achievement_button_scaled = None
magnify_button_scaled = None
bonus_result_images_scaled = {}
bonus_images_scaled = {}
cover_bonus_scaled = None
cover_quiz_scaled = None
board_image_scaled = None

def transform_coords(x, y, scale, game_state):
    """Transform world coordinates to screen coordinates based on camera state."""
    camera_zoom = game_state.get('camera_zoom', 1.0)
    camera_focus_x = game_state.get('camera_focus_x', 400.0)
    camera_focus_y = game_state.get('camera_focus_y', 300.0)
    
    # Position relative to focus point
    rel_x = x - camera_focus_x
    rel_y = y - camera_focus_y
    
    # Scale by camera zoom and window scale
    screen_x = rel_x * camera_zoom * scale + SCREEN_WIDTH / 2
    screen_y = rel_y * camera_zoom * scale + SCREEN_HEIGHT / 2
    
    return int(screen_x), int(screen_y)

def update_camera_targets(game_state, players):
    """Calculate target camera focus and zoom based on current mode."""
    mode = game_state.get('camera_mode', 0)
    
    # Default values
    target_zoom = 1.0
    target_focus_x = 400.0 # Center of 800x600 board
    target_focus_y = 300.0
    
    if mode == 1: # All Players
        active_players = [p for p in players if not p.finished]
        if active_players:
            min_x = min(p.current_x for p in active_players)
            max_x = max(p.current_x for p in active_players)
            min_y = min(p.current_y for p in active_players)
            max_y = max(p.current_y for p in active_players)
            
            target_focus_x = (min_x + max_x) / 2
            target_focus_y = (min_y + max_y) / 2
            
            # Add padding
            width = (max_x - min_x) + 200
            height = (max_y - min_y) + 200
            
            # Calculate required zoom to fit this bounding box
            zoom_x = 800 / max(1, width)
            zoom_y = 600 / max(1, height)
            target_zoom = min(zoom_x, zoom_y, 4.0) # Cap zoom at 4.0
            target_zoom = max(target_zoom, 1.0) # Don't zoom out past 1.0
        
    elif mode == 2: # Current Player
        cp_idx = game_state.get('current_player', 0)
        if cp_idx < len(players):
            cp = players[cp_idx]
            target_focus_x = cp.current_x
            target_focus_y = cp.current_y
            target_zoom = 2.5 # Nice close up
            
    game_state['camera_target_zoom'] = target_zoom
    game_state['camera_target_focus_x'] = target_focus_x
    game_state['camera_target_focus_y'] = target_focus_y


# Game progress functions moved to src.core.progress

# Asset loading moved to src.core.assets

# Initialise Pygame
pygame.init()
logger.info("Pygame initialised successfully")



# Screen settings - imported from constants
SCREEN_WIDTH, SCREEN_HEIGHT = ORIGINAL_WIDTH, ORIGINAL_HEIGHT
offset_x, offset_y = 0, 0
scale = 1.0
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Rock-Sickle")

# Set the window icon AFTER the display is initialised (required on macOS)
try:
    icon_path = load_asset("Assets/Images/Icons/RockSickle.png")
    icon_surface = pygame.image.load(icon_path)
    pygame.display.set_icon(icon_surface)
    logger.info(f"Custom icon set successfully: {icon_path}")
except Exception as e:
    logger.warning(f"Could not set window icon: {e}")

logger.info("Display initialised successfully")


# Load image assets - tiles, players, and all that jazz
try:
    # Load classic tile images - convert all to 32-bit RGBA format
    def load_and_convert(path):
        """Load an image and convert it to 32-bit RGBA format for proper scaling"""
        img = pygame.image.load(load_asset(path))
        return img.convert_alpha()
    
    forward_one_original = load_and_convert("Assets/Images/Tiles/Forward One.png")
    back_two_original = load_and_convert("Assets/Images/Tiles/Back Two.png")
    restart_button_original = load_and_convert("Assets/Images/Tiles/Restart.png")
    settings_button_original = load_and_convert("Assets/Images/Tiles/Mr Geary.png")
    achievement_button_original = load_and_convert("Assets/Images/Tiles/Target.png")
    e_achievement_button_original = load_and_convert("Assets/Images/Tiles/eTarget.png")
    tile_images_original = {
        'Go': load_and_convert("Assets/Images/Tiles/Go.png"),
        '1_East': forward_one_original,
        '1_South': pygame.transform.rotate(forward_one_original, 90),
        '1_West': pygame.transform.rotate(forward_one_original, 180),
        '1_North': pygame.transform.rotate(forward_one_original, 270),
        '-2_East': pygame.transform.rotate(back_two_original, 180),
        '-2_South': pygame.transform.rotate(back_two_original, 270),
        '-2_West': back_two_original,
        '-2_North': pygame.transform.rotate(back_two_original, 90),
        'B': load_and_convert("Assets/Images/Tiles/Bonus.png"),
        'Q': load_and_convert("Assets/Images/Tiles/Quiz.png"),
        'J': load_and_convert("Assets/Images/Tiles/Go To Jail.png"),
        '0': load_and_convert("Assets/Images/Tiles/Safe Space.png"),
        'P': load_and_convert("Assets/Images/Tiles/Choose Your Path.png"),
        'F': load_and_convert("Assets/Images/Tiles/Finish.png"),
        'Jail': load_and_convert("Assets/Images/Tiles/Jail Location.png"),
    }
    
    e_forward_one_original = load_and_convert("Assets/Images/Tiles/eForward One.png")
    e_back_two_original = load_and_convert("Assets/Images/Tiles/eBack Two.png")
    e_restart_button_original = load_and_convert("Assets/Images/Tiles/eRestart.png")
    e_settings_button_original = load_and_convert("Assets/Images/Tiles/eMr Geary.png")
    
    expert_tile_images_original = {
        'Go': load_and_convert("Assets/Images/Tiles/Go.png"),  # Reusing Go tile for expert
        '1_East': e_forward_one_original,
        '1_South': pygame.transform.rotate(e_forward_one_original, 90),
        '1_West': pygame.transform.rotate(e_forward_one_original, 180),
        '1_North': pygame.transform.rotate(e_forward_one_original, 270),
        '-2_East': pygame.transform.rotate(e_back_two_original, 180),
        '-2_South': pygame.transform.rotate(e_back_two_original, 270),
        '-2_West': e_back_two_original,
        '-2_North': pygame.transform.rotate(e_back_two_original, 90),
        'B': load_and_convert("Assets/Images/Tiles/eBonus.png"),
        'Q': load_and_convert("Assets/Images/Tiles/eQuiz.png"),
        'J': load_and_convert("Assets/Images/Tiles/eGo To Jail.png"),
        '0': load_and_convert("Assets/Images/Tiles/eSafe Space.png"),
        'P': load_and_convert("Assets/Images/Tiles/eChoose Your Path.png"),
        'F': load_and_convert("Assets/Images/Tiles/eFin.png"),
        'Jail': load_and_convert("Assets/Images/Tiles/eJail Location.png"),
        'FP': load_and_convert("Assets/Images/Tiles/Free Parking.png"),
    }
    
    # Store both sets
    board_tile_images = {
        'Classic': tile_images_original,
        'Expert': expert_tile_images_original,
        'Secret': tile_images_original  # Reuse Classic tiles for Secret board
    }
    
    board_buttons = {
        'Classic': {
            'restart': restart_button_original,
            'settings': settings_button_original,
            'achievement': achievement_button_original
        },
        'Expert': {
            'restart': e_restart_button_original,
            'settings': e_settings_button_original,
            'achievement': e_achievement_button_original
        },
        'Secret': {
            'restart': restart_button_original,
            'settings': settings_button_original,
            'achievement': achievement_button_original
        }
    }
    
    logger.info("Classic and expert tile images loaded successfully")
except Exception as e:
    logger.error(f"Error loading tile images: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    player_image_paths = [
        "Assets/Images/Players/Player Red.png",
        "Assets/Images/Players/Player Orange.png",
        "Assets/Images/Players/Player Yellow.png",
        "Assets/Images/Players/Player Green.png",
        "Assets/Images/Players/Player Blue.png",
        "Assets/Images/Players/Player Purple.png",
    ]
    player_images_original = [load_and_convert(img) for img in player_image_paths]
    logger.info("Original player images loaded successfully")
except Exception as e:
    logger.error(f"Error loading player images: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    cpu_image_original = load_and_convert("Assets/Images/Players/Player CPU.png")
    logger.info("Original CPU image loaded successfully")
except Exception as e:
    logger.error(f"Error loading CPU image: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    dice_images_original = [
        load_and_convert(f"Assets/Images/Dices/{i}.png") for i in range(1, 7)
    ]
    logger.info("Original dice images loaded successfully")
except Exception as e:
    logger.error(f"Error loading dice images: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    difficulty_images_original = {
        'easy': load_and_convert("Assets/Images/DifficultyButtons/1Baby.png"),
        'normal': load_and_convert("Assets/Images/DifficultyButtons/3Consentrated.png"),
        'hard': load_and_convert("Assets/Images/DifficultyButtons/4Angery.png"),
    }
    logger.info("Original difficulty images loaded successfully")
    
    # Load CPU difficulty images
    cpu_difficulty_images_original = {
        'easy': load_and_convert("Assets/Images/Players/CPUEasy.png"),
        'normal': load_and_convert("Assets/Images/Players/CPUNormal.png"),
        'hard': load_and_convert("Assets/Images/Players/CPUHard.png"),
    }
    logger.info("CPU difficulty images loaded successfully")
except Exception as e:
    logger.error(f"Error loading difficulty images: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Load bonus result images as 32-bit surfaces with per-pixel alpha
try:
    bonus_result_paths = {
        'back1': "Assets/Images/Bonus Card Results/Back1.png",
        'back1alt': "Assets/Images/Bonus Card Results/Back1Alt.png",
        'back3': "Assets/Images/Bonus Card Results/Back3.png",
        'back5': "Assets/Images/Bonus Card Results/Back5.png",
        'forward2': "Assets/Images/Bonus Card Results/Forward2.png",
        'forward3': "Assets/Images/Bonus Card Results/Forward3.png",
        'forward3alt': "Assets/Images/Bonus Card Results/Forward3Alt.png",
        'forward4': "Assets/Images/Bonus Card Results/Forward4.png",
        'jail1': "Assets/Images/Bonus Card Results/Go To Jail 1.png",
        'jail2': "Assets/Images/Bonus Card Results/Go To Jail 2.png",
        'jail3': "Assets/Images/Bonus Card Results/Go To Jail 3.png",
        'jail4': "Assets/Images/Bonus Card Results/Go To Jail 4.png",
        'pickquiz': "Assets/Images/Bonus Card Results/PickQuizCard.png",
        'pickquizalt': "Assets/Images/Bonus Card Results/PickQuizCardAlt.png",
        'pickquizaltalt': "Assets/Images/Bonus Card Results/PickQuizCardAltAlt.png",
        # Expert bonus card images
        'expert_back2_1': "Assets/Images/Bonus Card Results Expert/Back2.png",
        'expert_back2_2': "Assets/Images/Bonus Card Results Expert/Back2Alt.png",
        'expert_back5_1': "Assets/Images/Bonus Card Results Expert/Back5.png",
        'expert_back5_2': "Assets/Images/Bonus Card Results Expert/Back5Alt.png",
        'expert_forward2_1': "Assets/Images/Bonus Card Results Expert/Forward2 1.png",
        'expert_forward2_2': "Assets/Images/Bonus Card Results Expert/Forward2 2.png",
        'expert_forward2_3': "Assets/Images/Bonus Card Results Expert/Forward2 3.png",
        'expert_forward2_4': "Assets/Images/Bonus Card Results Expert/Forward2 4.png",
        'expert_forward2_5': "Assets/Images/Bonus Card Results Expert/Forward2 5.png",
        'expert_forward2_6': "Assets/Images/Bonus Card Results Expert/Forward2 6.png",
        'expert_forward5': "Assets/Images/Bonus Card Results Expert/Forward5.png",
        'expert_jail1': "Assets/Images/Bonus Card Results Expert/Go To Jail 1.png",
        'expert_jail2': "Assets/Images/Bonus Card Results Expert/Go To Jail 2.png",
        'expert_jail3': "Assets/Images/Bonus Card Results Expert/Go To Jail 3.png",
        'expert_jail4': "Assets/Images/Bonus Card Results Expert/Go To Jail 4.png",
        'expert_jail_free': "Assets/Images/Bonus Card Results Expert/Jail Free.png",
    }
    bonus_result_images_original = {}
    for key, path in bonus_result_paths.items():
        bonus_result_images_original[key] = load_and_convert(path)
    # Load card covers for the flipping animation
    cover_bonus_original = load_and_convert("Assets/Images/CardCovers/CoverBonus.png")
    cover_quiz_original = load_and_convert("Assets/Images/CardCovers/CoverQuiz.png")
    
    logger.info("Original bonus result images and card covers loaded successfully as 32-bit surfaces")
except Exception as e:
    logger.error(f"Error loading bonus result images or card covers: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

audio.init_audio()

# Font setup for text rendering
font = pygame.font.SysFont(None, 24)

# Board logic extracted to src.game.board

# Default to Classic board
squares, next_positions = get_board_squares("Classic")

# Initialize with classic board coordinates
squares_coords = get_classic_squares_coords()

# Jail positions and sizes imported from constants
JAIL_POS = CLASSIC_JAIL_POS

import src.game.cards as cards

# Player class moved to src.game.player

from src.game.mechanics import roll_die, interpolate_position, get_movement_path, get_movement_path_with_choice, get_ending_position_after_choice

# Card logic moved to src.game.cards

def apply_effect(player, square_type, game_state, scale):
    """Apply the effect of landing on a square."""
        
    chain = False
    message = ""
    
    # Expert board now has the correct layout directly, no need for special handling
    
    if square_type == '0':
        message = f"Player {player.id + 1} on safe space."
        player.turn_ended = True
    elif square_type == '1':
        if player.position + 1 < len(squares):
            target_pos = player.position + 1
            movement_path = [player.position, target_pos]
            anim = {
                'player': player,
                'path': movement_path,
                'index': 0,
                'last_time': time.time(),
                'message': "Move forward 1 space.",
                'is_initial_move': False,
                'delay': 0.5
            }
            player.active_animations.append(anim)
            message = f"Player {player.id + 1} moves forward 1 space."
            chain = True
            player.turn_ended = False
        else:
            message = f"Player {player.id + 1} can't move forward."
            player.turn_ended = True
    elif square_type == '-2':
        if player.position == 0:
            message = f"Player {player.id + 1} can't move back."
            player.turn_ended = True
        else:
            # Move back 2 spaces
            num_back = 2
            # Calculate target position (at most back to start)
            target_pos = max(0, player.position - num_back)
            # Create movement path
            movement_path = [player.position]
            
            # If position is 2 or greater, go back 2 spaces
            if player.position >= num_back:
                for i in range(1, num_back + 1):
                    movement_path.append(player.position - i)
            # Otherwise go back to the start
            else:
                for i in range(1, player.position + 1):
                    movement_path.append(player.position - i)
            
            anim = {
                'player': player,
                'path': movement_path,
                'index': 0,
                'last_time': time.time(),
                'message': f"Moving back {len(movement_path)-1} spaces.",
                'is_backwards': True,
                'delay': 0.5
            }
            player.active_animations.append(anim)
            message = f"Player {player.id + 1} moves back 2 spaces."
            chain = True
    elif square_type == 'B':
        if game_state.get('selected_board') == "Expert" and cards.expert_bonus_card_index < len(cards.expert_bonus_cards):
            # Use expert bonus cards on the expert board
            # Allow picking another bonus card if:
            # 1. No bonus card animation is active, OR
            # 2. Player has moved from a different position since the last bonus card pickup
            current_pos = player.position
            last_bonus_pos = game_state.get('last_bonus_position', {}).get(str(player.id), None)
            can_pick_bonus = not game_state.get('bonus_image_key') or current_pos != last_bonus_pos
            
            if can_pick_bonus:
                bonus = cards.expert_bonus_cards[cards.expert_bonus_card_index]
                cards.expert_bonus_card_index = (cards.expert_bonus_card_index + 1) % len(cards.expert_bonus_cards)
                audio.drip_drop_sound.play()
                effect = cards.parse_bonus_card(bonus)
                image_key = cards.get_bonus_image_key(effect, "Expert")
                if image_key:
                    game_state['bonus_image_key'] = image_key
                    game_state['bonus_image_start'] = time.time()
                    game_state['bonus_image_state'] = 'waiting'
                    game_state['bonus_action'] = effect
                    message = f"Player {player.id + 1} picks bonus card: {bonus}."
                else:
                    message = f"Player {player.id + 1} picks unknown bonus card."
                
                # Track the position where this bonus card was picked up
                if 'last_bonus_position' not in game_state:
                    game_state['last_bonus_position'] = {}
                game_state['last_bonus_position'][str(player.id)] = current_pos
                
                # Set the processing_bonus_card flag for tracking quiz and animation state
                game_state['processing_bonus_card'] = True
                
                # IMPORTANT: Don't end the player's turn yet
                player.has_rolled = True
                increment_stat("bonus_cards_picked")

            else:
                # The player can't pick a new bonus card from the same position while actively processing one
                message = f"Player {player.id + 1} must finish current bonus card first."
                player.has_rolled = True
        elif cards.bonus_card_index < len(cards.bonus_cards):
            # Allow picking another bonus card if:
            # 1. No bonus card animation is active, OR
            # 2. Player has moved from a different position since the last bonus card pickup
            current_pos = player.position
            last_bonus_pos = game_state.get('last_bonus_position', {}).get(str(player.id), None)
            can_pick_bonus = not game_state.get('bonus_image_key') or current_pos != last_bonus_pos
            
            if can_pick_bonus:
                bonus = cards.bonus_cards[cards.bonus_card_index]
                cards.bonus_card_index = (cards.bonus_card_index + 1) % len(cards.bonus_cards)
                audio.drip_drop_sound.play()
                effect = cards.parse_bonus_card(bonus)
                image_key = cards.get_bonus_image_key(effect, "Classic")
                if image_key:
                    game_state['bonus_image_key'] = image_key
                    game_state['bonus_image_start'] = time.time()
                    game_state['bonus_image_state'] = 'waiting'
                    game_state['bonus_action'] = effect
                    message = f"Player {player.id + 1} picks bonus card: {bonus}."
                else:
                    message = f"Player {player.id + 1} picks unknown bonus card."
                
                # Track the position where this bonus card was picked up
                if 'last_bonus_position' not in game_state:
                    game_state['last_bonus_position'] = {}
                game_state['last_bonus_position'][str(player.id)] = current_pos
                
                # Set the processing_bonus_card flag for tracking quiz and animation state
                game_state['processing_bonus_card'] = True
                
                # IMPORTANT: Don't end the player's turn yet
                player.has_rolled = True
                increment_stat("bonus_cards_picked")

            else:
                # The player can't pick a new bonus card from the same position while actively processing one
                message = f"Player {player.id + 1} must finish current bonus card first."
                player.has_rolled = True
        else:
            message = f"Player {player.id + 1} has no bonus cards left."
            player.turn_ended = True
            player.has_rolled = True
    elif square_type == 'Q':
        # Determine which quiz deck to use based on the board type
        if game_state.get('selected_board') == "Expert" and cards.expert_quiz_card_index < len(cards.expert_quiz_cards):
            # Use expert quiz cards on the expert board
            question, options, correct = cards.expert_quiz_cards[cards.expert_quiz_card_index]
            game_state['quiz_question'] = (question, options, correct)
            game_state['show_quiz'] = True
            game_state['quiz_state'] = 'growing'
            game_state['quiz_start_time'] = time.time()
            game_state['pop_played'] = False
            audio.drum_machine_sound.play()
            cards.expert_quiz_card_index = (cards.expert_quiz_card_index + 1) % len(cards.expert_quiz_cards)
            message = f"Player {player.id + 1} faces an expert quiz."
        elif cards.quiz_card_index < len(cards.quiz_cards):
            # Use regular quiz cards on the classic board
            question, options, correct = cards.quiz_cards[cards.quiz_card_index]
            game_state['quiz_question'] = (question, options, correct)
            game_state['show_quiz'] = True
            game_state['quiz_state'] = 'growing'
            game_state['quiz_start_time'] = time.time()
            game_state['pop_played'] = False
            audio.drum_machine_sound.play()
            cards.quiz_card_index = (cards.quiz_card_index + 1) % len(cards.quiz_cards)
            message = f"Player {player.id + 1} faces a quiz."
        else:
            message = f"Player {player.id + 1} has no quiz cards left."
        player.turn_ended = True
    elif square_type == 'J':
        player.prev_position = player.position
        # Store the position where the player is sent to jail from
        player.jail_from_x = player.current_x
        player.jail_from_y = player.current_y
        # Set animation start time for jail marker
        player.jail_marker_anim_start = time.time()
        audio.whiz_sound.play()
        
        # Calculate a random position within the jail bounds
        jail_offset_x = random.randint(-int(JAIL_SIZE/3), int(JAIL_SIZE/3))
        jail_offset_y = random.randint(-int(JAIL_SIZE/3), int(JAIL_SIZE/3))
        random_jail_pos = (JAIL_POS[0] + jail_offset_x, JAIL_POS[1] + jail_offset_y)
        
        anim = {
            'player': player,
            'start_pos': (player.current_x, player.current_y),
            'end_pos': random_jail_pos,  # Use random position instead of center
            'steps': 60,
            'current_step': 0,
            'last_time': time.time(),
            'message': "Moving to jail.",
            'is_jail_move': True,
            'delay': 0.0167,  # ~60fps (1/60 second)
            'jail_action': 'enter'
        }
        player.active_animations.append(anim)
        message = f"Player {player.id + 1} sent to jail."
        player.turn_ended = True
        
        # Increment jail landings stat
        increment_stat("jail_landings")
    elif square_type == 'P':
        message = f"Player {player.id + 1} chooses a path."
        # Check if the player has zero spaces remaining (ended their turn on the P square)
        if game_state.get('spaces_remaining', 0) == 0:
            message = f"Player {player.id + 1} stops at the path choice."
            player.turn_ended = True
            chain = False
        else:
            game_state['show_path_choice_after_roll'] = True
            game_state['roll_for_path_choice'] = game_state['dice_roll']
            # Don't reset spaces_remaining here - use the value set by get_movement_path
            chain = True  # Allow turn to continue after path choice
            player.turn_ended = False
    elif square_type == 'F':
        player.finished = True
        player.position = len(squares) - 1
        audio.win_sound.play()
        
        # Record player finish time and calculate elapsed time
        player.finish_time = time.time()
        player.elapsed_time = player.finish_time - player.start_time
        
        message = f"Player {player.id + 1} finished in {format_time(player.elapsed_time)}!"
        player.turn_ended = True
        if game_state.get('finish_order') is None:
            game_state['finish_order'] = []
        game_state['finish_order'].append(player)
        if len(game_state['finish_order']) == len(game_state['players']):
            audio.fairlin_round1_sound.play()
            # Set up victory animation rather than teleporting players
            game_state['victory_cutscene'] = True
            game_state['victory_cutscene_start'] = time.time()
            
            # Define target positions for the victory formation - to the right of the finish tile
            # Finish tile is at (60, ~155), so we'll place victory formation to its right
            finish_x, finish_y = 60, 155 + 2*GAP_BETWEEN_TILES - 5  # Finish tile coordinates
            victory_x = lambda idx: int((finish_x + 80 + idx * 50) * scale)  # Start 80px to the right of finish, then space by 50px
            victory_y = lambda _: int(finish_y * scale)  # Same y-level as the finish tile
            
            # Set up animation data for each player
            for idx, fin_player in enumerate(game_state['finish_order']):
                # Create victory animation for the player
                anim = {
                    'player': fin_player,
                    'start_pos': (fin_player.current_x, fin_player.current_y),
                    'end_pos': (victory_x(idx), victory_y(idx)),
                    'start_time': time.time(),
                    'duration': 2.0,  # 2 seconds for the glide animation
                    'type': 'victory_glide',
                    'scale_factor': 1.5  # Players will be 50% larger in victory pose
                }
                # Initialize the victory_scale_factor attribute for each player
                fin_player.victory_scale_factor = 1.0
                fin_player.active_animations.append(anim)
            
            # Game completed - handle unlocks and progress
            game_progress = load_game_progress()
            
            # Increment completed games counter regardless of board type
            game_progress['completed_games'] = game_progress.get('completed_games', 0) + 1
            
            # Update specific board completion flags
            current_board = game_state.get('selected_board')
            if current_board == 'Classic':
                game_progress['classic_board_completed'] = True
                if 'Expert' not in game_progress.get('unlocked_boards', ['Classic']):
                    game_progress['unlocked_boards'].append('Expert')
            elif current_board == 'Expert':
                game_progress['expert_board_completed'] = True
            elif current_board == 'Secret':
                game_progress['secret_board_completed'] = True

            # Check if we should unlock the secret board (100+ completed games)
            if game_progress['completed_games'] >= 100 and 'Secret' not in game_progress.get('unlocked_boards', []):
                game_progress['unlocked_boards'].append('Secret')
                logger.info("Secret board unlocked!")
            
            # Check if a human player defeated a Hard CPU
            winner = game_state['finish_order'][0]
            if not winner.is_computer:
                for p in game_state['players']:
                    if p.is_computer and p.difficulty == 'hard':
                        game_progress['stats']['hard_cpu_defeats'] = game_progress['stats'].get('hard_cpu_defeats', 0) + 1
                        break
            
            # Check for newly completed achievements
            newly_completed = check_achievement_completion(game_progress)
            if newly_completed:
                if 'completed_achievements' not in game_progress:
                    game_progress['completed_achievements'] = []
                
                for a_id in newly_completed:
                    game_progress['completed_achievements'].append(a_id)
                    achievement = get_achievement_by_id(a_id)
                    if achievement and "reward" in achievement:
                        if 'unlocked_gallery_items' not in game_progress:
                            game_progress['unlocked_gallery_items'] = []
                        game_progress['unlocked_gallery_items'].append(achievement["reward"])
                        logger.info(f"Achievement Accomplished: {achievement['title']}! Reward: {achievement['reward']}")
                        # Also show on screen
                        game_state['message'] = f"ACHIEVEMENT ACCOMPLISHED: {achievement['title']}!"
            
            save_game_progress(game_progress)
    elif square_type == 'Go':
        message = f"Player {player.id + 1} at start."
        player.turn_ended = True
    elif square_type == 'FP':
        message = f"Player {player.id + 1} on Free Parking."
        player.turn_ended = True
        audio.car_horn_sound.play()
        
        # Add visual feedback animation for Free Parking
        game_state['free_parking_effect'] = True
        game_state['free_parking_start_time'] = time.time()
        game_state['free_parking_duration'] = 1.0  # Reduced from 1.5 to 1.0 seconds
        game_state['free_parking_player'] = player
        # Store the position of the FP square for correct effect positioning
        game_state['free_parking_position'] = player.position
    return message, chain

def move_player(player, game_state):
    """Handle a player rolling the die."""
    if player.finished:
        return "Player has finished.", False
    if game_state.get('rolling_dice', False):
        return "", False
    
    if game_state.get('selected_board') == 'Expert':
        # On Expert board, roll two dice
        if player.is_computer:
            roll1 = roll_die(player.difficulty)
            roll2 = roll_die(player.difficulty)
        else:
            roll1 = roll_die()
            roll2 = roll_die()
        
        total_roll = roll1 + roll2
        game_state['dice_roll'] = total_roll
        game_state['dice_roll_1'] = roll1
        game_state['dice_roll_2'] = roll2
        game_state['is_doubles'] = (roll1 == roll2)
        
        game_state['rolling_dice'] = True
        game_state['dice_start_time'] = time.time()
        audio.roll_sound.play()
        return f"Player {player.id + 1} rolled {roll1} and {roll2} for a total of {total_roll}.", True
    else:
        # Classic board - single die roll
        if player.is_computer:
            roll = roll_die(player.difficulty)
        else:
            roll = roll_die()
        game_state['dice_roll'] = roll
        game_state['rolling_dice'] = True
        game_state['dice_start_time'] = time.time()
        audio.roll_sound.play()
        return f"Player {player.id + 1} rolled {roll}.", True

def apply_quiz_effect(player, correct, game_state, scale):
    """Apply effects based on quiz answer correctness."""
    if correct:
        game_state['message'] = f"Player {player.id + 1} answered correctly!"
        audio.mac_os_dinbg_sound.play()
        increment_stat("quiz_correct")

        player.turn_ended = True
        game_state['quiz_state'] = 'answered'
        game_state['quiz_answer_delay_start'] = time.time()
        if 'quiz_buttons' in game_state:
            del game_state['quiz_buttons']
        
        # Set has_rolled to true to ensure turn ends properly
        player.has_rolled = True
        
        # If this quiz came from a bonus card, make sure the bonus processing is completed
        if game_state.get('processing_bonus_card', False):
            # Mark that a quiz from a bonus card was answered correctly
            game_state['quiz_from_bonus_completed'] = True
    else:
        game_state['message'] = f"Player {player.id + 1} answered wrong. Moving back 2 spaces."
        audio.bing_bong_sound.play()
        
        # Move back 2 spaces (or to the start)
        num_back = 2
        target_pos = max(0, player.position - num_back)
        
        # Create movement path
        movement_path = [player.position]
        
        # If position is 2 or greater, go back 2 spaces
        if player.position >= num_back:
            for i in range(1, num_back + 1):
                movement_path.append(player.position - i)
        # Otherwise go back to the start
        else:
            for i in range(1, player.position + 1):
                movement_path.append(player.position - i)
        
        anim = {
            'player': player,
            'path': movement_path,
            'index': 0,
            'last_time': time.time(),
            'message': "Moving back 2 spaces.",
            'is_backwards': True,
            'delay': 0.5
        }
        player.active_animations.append(anim)
        game_state['quiz_state'] = 'answered'
        game_state['quiz_answer_delay_start'] = time.time()
        if 'quiz_buttons' in game_state:
            del game_state['quiz_buttons']
        player.turn_ended = True  # Ensure turn ends even on wrong answer
        
        # If this quiz came from a bonus card, make sure the bonus processing is completed
        if game_state.get('processing_bonus_card', False):
            # Mark that a quiz from a bonus card was answered (incorrectly)
            game_state['quiz_from_bonus_completed'] = True

def update_animation(game_state, scale):
    """Update all active animations in the game."""
    any_animations = False
    # Special handling for victory cutscene animation
    if game_state.get('victory_cutscene', False):
        any_animations = True
    
    # Smoothly interpolate camera state
    factor = 0.1 # Interpolation factor for smooth movement
    
    # Update camera zoom
    current_zoom = game_state.get('camera_zoom', 1.0)
    target_zoom = game_state.get('camera_target_zoom', 1.0)
    if abs(current_zoom - target_zoom) > 0.001:
        game_state['camera_zoom'] = current_zoom + (target_zoom - current_zoom) * factor
        any_animations = True
    else:
        game_state['camera_zoom'] = target_zoom
        
    # Update camera focus
    current_x = game_state.get('camera_focus_x', 400.0)
    target_x = game_state.get('camera_target_focus_x', 400.0)
    if abs(current_x - target_x) > 0.1:
        game_state['camera_focus_x'] = current_x + (target_x - current_x) * factor
        any_animations = True
    else:
        game_state['camera_focus_x'] = target_x
        
    current_y = game_state.get('camera_focus_y', 300.0)
    target_y = game_state.get('camera_target_focus_y', 300.0)
    if abs(current_y - target_y) > 0.1:
        game_state['camera_focus_y'] = current_y + (target_y - current_y) * factor
        any_animations = True
    else:
        game_state['camera_focus_y'] = target_y

    
    # Handle Free Parking effect animation
    if game_state.get('free_parking_effect', False):
        current_time = time.time()
        elapsed_time = current_time - game_state['free_parking_start_time']
        
        if elapsed_time >= game_state['free_parking_duration']:
            # Animation complete - remove the effect
            game_state.pop('free_parking_effect')
            game_state.pop('free_parking_start_time')
            game_state.pop('free_parking_duration')
            game_state.pop('free_parking_player')
        else:
            # Animation still running
            any_animations = True
    
    for player in game_state['players']:
        if player.active_animations:
            any_animations = True
            anim = player.active_animations[0]
            current_time = time.time()
            
            # Check if we need to play the jail movement sound after the delay
            if 'is_jail_move' in anim and 'sound_delay' in anim and not anim.get('sound_played', False):
                if current_time >= anim['sound_delay']:
                    audio.whiz_sound.play()  # Play the whiz sound for jail movement
                    anim['sound_played'] = True
                    # Start the actual movement only after the sound is played
                    anim['last_time'] = current_time
            
            # Special handling for victory_glide animation type
            if anim.get('type') == 'victory_glide':
                # Calculate animation progress from 0.0 to 1.0
                progress = min(1.0, (current_time - anim['start_time']) / anim['duration'])
                
                # Use easing function for smoother animation (ease-out)
                t = 1.0 - (1.0 - progress) * (1.0 - progress)
                
                # Interpolate position
                start_x, start_y = anim['start_pos']
                end_x, end_y = anim['end_pos']
                
                anim['player'].current_x = start_x + (end_x - start_x) * t
                anim['player'].current_y = start_y + (end_y - start_y) * t
                
                # When animation completes, remove it but save its scale factor and position
                if progress >= 1.0:
                    # Store the final scale factor in the player object
                    # so it can be used for rendering even after animation is removed
                    player.victory_scale_factor = anim.get('scale_factor', 1.5)
                    # Store the final position coordinates for rendering player times
                    player.victory_x = anim['player'].current_x
                    player.victory_y = anim['player'].current_y
                    player.active_animations.pop(0)
            elif 'last_time' in anim and 'delay' in anim and current_time - anim['last_time'] >= anim['delay']:
                if 'is_jail_move' in anim:
                    # Only update animation if the sound delay has passed
                    if anim.get('sound_played', True):
                        anim['current_step'] += 1
                        if anim['current_step'] <= anim['steps']:
                            anim['player'].current_x, anim['player'].current_y = interpolate_position(
                                anim['start_pos'], anim['end_pos'], anim['steps'], anim['current_step']
                            )
                            anim['last_time'] = current_time
                        else:
                            if anim.get('jail_action') == 'enter':
                                anim['player'].position = 10  # Jail position
                                anim['player'].in_jail = True
                                # Store final random position for drawing
                                anim['player'].jail_x = anim['player'].current_x
                                anim['player'].jail_y = anim['player'].current_y
                                
                                # Clean up jail sound delay variables if they exist
                                if anim.get('cleanup_jail_sound', False) and 'jail_sound_delay' in game_state:
                                    if 'jail_sound_played' in game_state:
                                        del game_state['jail_sound_played']
                                    if 'jail_sound_delay' in game_state:
                                        del game_state['jail_sound_delay']
                            elif anim.get('jail_action') == 'exit':
                                # Sound is now played at animation start instead of completion
                                anim['player'].position = anim['player'].prev_position
                                anim['player'].in_jail = False
                                # Clear the jail marker when player exits jail
                                anim['player'].jail_from_x = None
                                anim['player'].jail_from_y = None
                                anim['player'].jail_marker_anim_start = None
                            player.active_animations.pop(0)
                            player.turn_ended = True
                # Note: Victory glide animation is now handled in the previous condition
                else:
                    anim['index'] += 1
                    if anim['index'] < len(anim['path']):
                        # Get the previous position before updating
                        prev_position = anim['player'].position
                        prev_square_type = squares[prev_position] if prev_position < len(squares) else None
                        
                        # Update player position to match current point in animation path
                        anim['player'].position = anim['path'][anim['index']]
                        anim['player'].current_x, anim['player'].current_y = squares_coords[anim['player'].position]
                        
                        # Special handling for GO square position
                        if anim['player'].position == 0:
                            # Ensure player is exactly at the center of the GO tile
                            anim['player'].current_x = squares_coords[0][0]
                            anim['player'].current_y = squares_coords[0][1]
                        
                        # Check if player moved away from a B square and reset their bonus tracking
                        if prev_square_type == 'B' and prev_position != anim['player'].position:
                            # Player has moved away from a B square, so allow them to pick up a bonus there again
                            if 'last_bonus_position' in game_state and str(anim['player'].id) in game_state['last_bonus_position']:
                                if game_state['last_bonus_position'][str(anim['player'].id)] == prev_position:
                                    del game_state['last_bonus_position'][str(anim['player'].id)]
                        
                        # Handle position history differently for forwards vs backwards movement
                        if 'is_backwards' not in anim:
                            # For forward movement, add positions to history if not already there
                            if anim['player'].position not in anim['player'].position_history:
                                anim['player'].position_history.append(anim['player'].position)
                        else:
                            # For backward movement, we're moving to a position we were in before,
                            # so we remove positions from history until we match our current position
                            while (len(anim['player'].position_history) > 0 and 
                                   anim['player'].position_history[-1] > anim['player'].position):
                                anim['player'].position_history.pop()
                        
                        anim['last_time'] = current_time
                        if 'is_initial_move' in anim and anim['is_initial_move']:
                            # Play CPU or human glug sound based on player type
                            if anim['player'].is_computer:
                                audio.glug_cpu_sound.play()
                            else:
                                audio.glug_sound.play()
                        elif 'is_backwards' in anim:
                            # Play CPU or human wobble sound based on player type
                            if anim['player'].is_computer:
                                audio.wobble_cpu_sound.play()
                            else:
                                audio.wobble_sound.play()
                        else:
                            # Play CPU or human jump sound based on player type
                            if anim['player'].is_computer:
                                audio.jump_cpu_sound.play()
                            else:
                                audio.jump_sound.play()
                        game_state['message'] = anim['message'] + f" Moved to {squares[anim['player'].position]}."
                    else:
                        # If this was a backwards movement, end turn without applying square effects
                        if 'is_backwards' in anim:
                            player.active_animations.pop(0)
                            square_type = squares[anim['player'].position]
                            # Apply effects for the square the player landed on after moving backwards
                            message, chain = apply_effect(anim['player'], square_type, game_state, scale)
                            if message:
                                game_state['message'] = message
                            if not chain:
                                player.turn_ended = True
                            else:
                                player.turn_ended = False
                        else:
                            square_type = squares[anim['player'].position]
                            message, chain = apply_effect(anim['player'], square_type, game_state, scale)
                            game_state['message'] = anim['message'] + f" Landed on {square_type}. {message}"
                            player.active_animations.pop(0)
                            # Only end the turn if this wasn't a B square or there's a quiz to show
                            # This allows players to get multiple bonus cards in one turn
                            if (not chain or game_state.get('show_quiz', False)) and square_type != 'B':
                                player.turn_ended = True
                            else:
                                any_animations = True
    return any_animations

from src.ui.menus import toggle_player_state, cycle_difficulty
from src.ui.renderer import format_time, get_player_position_text, render_player_text, display_player_timers, render_coloured_message, render_wrapped_text
def draw_board(players, game_state, scale, offset_x, offset_y, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, achievement_button_scaled, magnify_button_scaled, bonus_result_images_scaled):
    """Draw the game board and all its elements with card-flipping animations for button and squish for squares."""
    camera_zoom = game_state.get('camera_zoom', 1.0)
    
    # Pre-scale tile images for the current camera zoom level if needed
    if abs(camera_zoom - 1.0) > 0.001:
        current_tile_images = {
            key: pygame.transform.smoothscale(img, (int(img.get_width() * camera_zoom), int(img.get_height() * camera_zoom)))
            for key, img in tile_images_scaled.items()
        }
        current_player_images = [
            pygame.transform.smoothscale(img, (int(img.get_width() * camera_zoom), int(img.get_height() * camera_zoom)))
            for img in player_images_scaled
        ]
        # Handle CPU images
        current_cpu_difficulty_images = {
            key: pygame.transform.smoothscale(img, (int(img.get_width() * camera_zoom), int(img.get_height() * camera_zoom)))
            for key, img in cpu_difficulty_images_scaled.items()
        }
        current_dice_images = [
            pygame.transform.smoothscale(img, (int(img.get_width() * camera_zoom), int(img.get_height() * camera_zoom)))
            for img in dice_images_scaled
        ]
    else:
        current_tile_images = tile_images_scaled
        current_player_images = player_images_scaled
        current_cpu_difficulty_images = cpu_difficulty_images_scaled
        current_dice_images = dice_images_scaled


    # Use dull pink background for Expert board, gray for Classic
    if game_state.get('selected_board') == 'Expert':
        screen.fill(DULL_PINK)
    elif game_state.get('selected_board') == 'Secret':
        # Use a dark green background for the Secret board
        screen.fill(DARK_GREEN)
        
        # For Secret board, draw arrow connections between spaces to show direction
        # This ensures they appear underneath the tiles
        if len(squares_coords) > 1:  # Make sure we have coordinates to work with
            arrow_color = (255, 255, 255)  # White arrows
            
            # Draw arrows connecting each space to the next
            for i in range(len(squares_coords) - 1):
                x1, y1 = transform_coords(squares_coords[i][0], squares_coords[i][1], scale, game_state)
                x2, y2 = transform_coords(squares_coords[i+1][0], squares_coords[i+1][1], scale, game_state)

                
                # Calculate direction and length
                dx = x2 - x1
                dy = y2 - y1
                length = max(1, math.sqrt(dx*dx + dy*dy))
                
                # Normalize direction vector
                dx /= length
                dy /= length
                
                # Get midpoint between the two points
                mid_x = (x1 + x2) // 2
                mid_y = (y1 + y2) // 2
                
                # Set arrow size based on scale
                arrow_size = max(4, int(8 * scale))
                
                # Calculate arrow points
                # Main line of the arrow - shortened to just be the middle section
                line_start_x = int(mid_x - dx * arrow_size)
                line_start_y = int(mid_y - dy * arrow_size)
                line_end_x = int(mid_x + dx * arrow_size)
                line_end_y = int(mid_y + dy * arrow_size)
                
                # Calculate perpendicular vector for arrowhead
                perp_dx = -dy
                perp_dy = dx
                
                # Calculate the arrowhead points
                arrow_head_size = max(3, int(6 * scale))
                arrow_p1_x = int(line_end_x - dx * arrow_head_size + perp_dx * arrow_head_size * 0.5)
                arrow_p1_y = int(line_end_y - dy * arrow_head_size + perp_dy * arrow_head_size * 0.5)
                arrow_p2_x = int(line_end_x - dx * arrow_head_size - perp_dx * arrow_head_size * 0.5)
                arrow_p2_y = int(line_end_y - dy * arrow_head_size - perp_dy * arrow_head_size * 0.5)
                
                # Draw the main line of the arrow
                pygame.draw.line(screen, arrow_color, (line_start_x, line_start_y), 
                                (line_end_x, line_end_y), max(1, int(2 * scale)))
                
                # Draw the arrowhead
                pygame.draw.polygon(screen, arrow_color, 
                                  [(line_end_x, line_end_y), (arrow_p1_x, arrow_p1_y), (arrow_p2_x, arrow_p2_y)])
    else:
        screen.fill(GRAY)
        
    # Store the free parking position and image for later rendering on top layer
    free_parking_x = None
    free_parking_y = None
    free_parking_img = None

    # Draw board spaces with pulsing squish animation during restart
    for i, square in enumerate(squares):
        # Ensure we don't try to access out of bounds coordinates
        if i >= len(squares_coords):
            break
            
        # Use camera transformation for tile position
        x, y = transform_coords(squares_coords[i][0], squares_coords[i][1], scale, game_state)


        # No need for special handling of '1' spaces in Expert mode anymore
        # since the squares array now has the correct layout for each board
        display_square = square
        
        # Determine the correct image for '1' and '-2' based on position
        if display_square in ['Go', 'B', 'Q', 'J', '0', 'P', 'F', 'FP']:
            img = current_tile_images[display_square]
            
            # Store free parking info for later if this is the active free parking square
            if display_square == 'FP' and game_state.get('free_parking_effect', False) and i == game_state.get('free_parking_position', -1):
                free_parking_x = x
                free_parking_y = y
                free_parking_img = img
                
        elif display_square == '1':
            # Check if we're on the expert board
            if game_state.get('selected_board') == 'Expert':
                # First row (east direction) - indices 1-15
                if 1 <= i <= 15:
                    img = current_tile_images['1_East']
                # Right column (south direction) - indices 16-22
                elif 16 <= i <= 22:
                    img = current_tile_images['1_South']
                # Bottom rows going west - west path or south path west segments
                elif (23 <= i <= 27) or (i >= 29 and i <= 37) or (i >= 52 and i <= 66):
                    img = current_tile_images['1_West']
                # Vertical segments going north - end of paths
                elif (i >= 38 and i <= 48) or (i >= 67 and i <= 77):
                    img = current_tile_images['1_North']
                # Default east direction for any other segments
                else:
                    img = current_tile_images['1_East']
            else:
                # Original classic board logic
                if i in [1, 6]:
                    img = current_tile_images['1_East']
                elif i in [12, 14]:
                    img = current_tile_images['1_North']
                elif i == 24:
                    img = current_tile_images['1_West']
                elif i == 31:
                    img = current_tile_images['1_West']
                else:
                    img = current_tile_images['1_East']
        elif display_square == '-2':
            # Check if we're on the expert board
            if game_state.get('selected_board') == 'Expert':
                # First row (east direction) - should point west (opposite)
                if 1 <= i <= 15:
                    img = current_tile_images['-2_West']
                # Right column (south direction) - should point north (opposite)
                elif 16 <= i <= 22:
                    img = current_tile_images['-2_North']
                # Bottom rows going west - should point east (opposite)
                elif (23 <= i <= 27) or (i >= 29 and i <= 37) or (i >= 52 and i <= 66):
                    img = current_tile_images['-2_East']
                # Vertical segments going north - should point south (opposite)
                elif (i >= 38 and i <= 48) or (i >= 67 and i <= 77):
                    img = current_tile_images['-2_South']
                # Default west direction for any other segments (opposite of east)
                else:
                    img = current_tile_images['-2_West']
            else:
                # Original classic board logic
                if i == 4:
                    img = current_tile_images['-2_West']
                elif i in [13, 15]:
                    img = current_tile_images['-2_South']
                elif i == 19:
                    img = current_tile_images['-2_East']
                elif i in [28, 33, 35]:
                    img = current_tile_images['-2_North']
                else:
                    img = current_tile_images['-2_West']

        tile_rect = pygame.Rect(x - img.get_width() // 2, 
                                y - img.get_height() // 2, 
                                img.get_width(), 
                                img.get_height())

        if 'fade_start' in game_state:
            fade_time = time.time() - game_state['fade_start']
            if fade_time < 1.0:  # Animation lasts 1 second
                number_of_cycles = 6
                cycle_duration = 1.0 / number_of_cycles  # 0.1667 seconds per cycle
                width_scale = (1 + math.sin(2 * math.pi * (fade_time / cycle_duration))) / 2
                squished_tile = pygame.transform.smoothscale(img, 
                                                             (int(img.get_width() * width_scale), 
                                                              img.get_height()))
                squished_rect = squished_tile.get_rect(center=tile_rect.center)
                screen.blit(squished_tile, squished_rect.topleft)
        else:
            # Draw the tile
            tile_pos = (x - img.get_width() // 2, y - img.get_height() // 2)
            screen.blit(img, tile_pos)
            
            # Add black outline for Expert board
            if game_state.get('selected_board') == 'Expert':
                # Create rectangle for the outline (slightly larger than the image)
                outline_thickness = 2
                outline_rect = pygame.Rect(
                    tile_pos[0] - outline_thickness,
                    tile_pos[1] - outline_thickness,
                    img.get_width() + (outline_thickness * 2),
                    img.get_height() + (outline_thickness * 2)
                )
                # Draw the outline (not filled)
                pygame.draw.rect(screen, (0, 0, 0), outline_rect, outline_thickness)
                
            # Draw the Free Parking animation effects AFTER the tile is drawn, so it appears on top
            if display_square == 'FP' and game_state.get('free_parking_effect', False) and i == game_state.get('free_parking_position', -1):
                # Get the current animation progress
                current_time = time.time()
                elapsed = current_time - game_state['free_parking_start_time']
                duration = game_state['free_parking_duration']
                progress = elapsed / duration
                
                # Calculate pulsing effect (0.0 to 1.0 to 0.0)
                pulse = abs(math.sin(progress * math.pi * 4))  # Faster pulsing with 4 cycles
                
                # Create a larger surface for the glow effect
                glow_size = int(img.get_width() * 2.0)  # Increased from 1.5 to 2.0 for a bigger glow
                glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                
                # Draw expanding circles with decreasing opacity
                for radius in range(5, int(glow_size/2), 4):
                    # Yellow glow with higher opacity (increased from 150 to 220)
                    opacity = int(220 * (1 - radius/(glow_size/2)) * pulse)
                    if opacity > 0:
                        pygame.draw.circle(glow_surface, (255, 255, 0, opacity), 
                                         (glow_size//2, glow_size//2), radius)
                
                # Draw the glow surface centered on the tile
                screen.blit(glow_surface, 
                           (x - glow_surface.get_width()//2, 
                            y - glow_surface.get_height()//2))
                            
                # Draw car icons orbiting around the Free Parking space (not the player)
                for j in range(4):
                    angle = progress * 4 * math.pi + (j * math.pi / 2)  # Rotate around center
                    
                    # Calculate position on the circle in world space
                    target_car_x = squares_coords[i][0] + (30 * (0.8 + 0.2 * pulse)) * math.cos(angle)
                    target_car_y = squares_coords[i][1] + (30 * (0.8 + 0.2 * pulse)) * math.sin(angle)
                    
                    car_x, car_y = transform_coords(target_car_x, target_car_y, scale, game_state)

                    
                    # Draw a car emoji (using a small yellow circle as placeholder)
                    car_size = int(20 * scale * camera_zoom * (0.8 + 0.2 * pulse))

                    car_surface = pygame.Surface((car_size, car_size), pygame.SRCALPHA)
                    # Increased opacity from 200 to 240 for more visibility
                    pygame.draw.circle(car_surface, (255, 255, 0, 240), (car_size//2, car_size//2), car_size//2)
                    
                    # Draw black outline with higher opacity
                    pygame.draw.circle(car_surface, (0, 0, 0, 240), (car_size//2, car_size//2), car_size//2, 2)
                    
                    # Blit to the screen
                    screen.blit(car_surface, (car_x - car_size//2, car_y - car_size//2))

    # Draw jail with pulsing squish animation during restart
    jail_x, jail_y = transform_coords(JAIL_POS[0], JAIL_POS[1], scale, game_state)
    jail_img = current_tile_images['Jail']
    jail_rect = pygame.Rect(jail_x - jail_img.get_width() // 2, 
                            jail_y - jail_img.get_height() // 2, 
                            jail_img.get_width(), 
                            jail_img.get_height())

    
    if 'fade_start' in game_state:
        fade_time = time.time() - game_state['fade_start']
        if fade_time < 1.0:  # Animation lasts 1 second
            number_of_cycles = 6
            cycle_duration = 1.0 / number_of_cycles  # 0.1667 seconds per cycle
            width_scale = (1 + math.sin(2 * math.pi * (fade_time / cycle_duration))) / 2
            squished_jail = pygame.transform.smoothscale(jail_img, 
                                                         (int(jail_img.get_width() * width_scale), 
                                                          jail_img.get_height()))
            squished_rect = squished_jail.get_rect(center=jail_rect.center)
            screen.blit(squished_jail, squished_rect.topleft)
    else:
        screen.blit(jail_img, (jail_x - jail_img.get_width() // 2, 
                               jail_y - jail_img.get_height() // 2))

    # ---------------------------------------------------------------------------
    # Draw card decks, animated bonus card, and quiz BEFORE players so that
    # players are always rendered on top of flying/sliding cards.
    # ---------------------------------------------------------------------------

    # Draw static card decks next to the die
    die_pos_x, die_pos_y = DIE_POS
    if game_state.get('selected_board') == 'Secret':
        if 'die_pos' in game_state:
            die_pos_x, die_pos_y = game_state['die_pos']
            
    die_center_x, die_center_y = transform_coords(die_pos_x + 25, die_pos_y + 25, scale, game_state) # Offset by half die size (50/2)



    deck_scale_factor = 0.45 * camera_zoom  # Scale down the decks on the board
    deck_offset = int(110 * scale * camera_zoom)  # Distance from the die center


    # Static Bonus Deck (Left)
    # Rotate 90 so the base faces the die (right)
    bonus_deck_img = pygame.transform.smoothscale(cover_bonus_scaled,
                                                (int(cover_bonus_scaled.get_width() * deck_scale_factor),
                                                 int(cover_bonus_scaled.get_height() * deck_scale_factor)))
    bonus_deck_rotated = pygame.transform.rotate(bonus_deck_img, 90)
    bonus_deck_rect = bonus_deck_rotated.get_rect(center=(die_center_x - deck_offset, die_center_y))
    screen.blit(bonus_deck_rotated, bonus_deck_rect.topleft)

    # Static Quiz Deck (Right)
    # Rotate -90 so the base faces the die (left)
    quiz_deck_img = pygame.transform.smoothscale(cover_quiz_scaled,
                                               (int(cover_quiz_scaled.get_width() * deck_scale_factor),
                                                int(cover_quiz_scaled.get_height() * deck_scale_factor)))
    quiz_deck_rotated = pygame.transform.rotate(quiz_deck_img, -90)
    quiz_deck_rect = quiz_deck_rotated.get_rect(center=(die_center_x + deck_offset, die_center_y))
    screen.blit(quiz_deck_rotated, quiz_deck_rect.topleft)

    # ---------------------------------------------------------------------------
    # Draw dice — Moved here to be below players (rendered later) and above
    # static card decks (rendered above), but below active cards (rendered below).
    # ---------------------------------------------------------------------------
    # Draw dice - single die for classic board, two dice for expert
    
    die_screen_x, die_screen_y = transform_coords(die_pos_x, die_pos_y, scale, game_state)

    dice_rect = pygame.Rect(die_screen_x, die_screen_y, int(50 * scale * camera_zoom), int(50 * scale * camera_zoom))
    
    # For expert board, define second die position and total text position
    is_expert_board = game_state.get('selected_board') == 'Expert'
    if is_expert_board:
        dice_rect1 = pygame.Rect(die_screen_x - int(35 * scale * camera_zoom), die_screen_y, int(50 * scale * camera_zoom), int(50 * scale * camera_zoom))
        dice_rect2 = pygame.Rect(die_screen_x + int(35 * scale * camera_zoom), die_screen_y, int(50 * scale * camera_zoom), int(50 * scale * camera_zoom))
        total_text_pos = (die_screen_x, die_screen_y + int(60 * scale * camera_zoom))


    
    if game_state.get('rolling_dice', False):
        if time.time() - game_state['dice_start_time'] < 1:
            # Animation phase
            if is_expert_board:
                # For expert board, show two random dice during animation
                for _ in range(2):  # Show multiple dice during animation
                    dice_face = random.choice(current_dice_images)
                    rand_x, rand_y = transform_coords(random.randint(100, ORIGINAL_WIDTH - 100), random.randint(100, ORIGINAL_HEIGHT - 100), scale, game_state)
                    screen.blit(dice_face, (rand_x, rand_y))
            else:
                # Classic board - single die
                dice_face = random.choice(current_dice_images)
                rand_x, rand_y = transform_coords(random.randint(100, ORIGINAL_WIDTH - 100), random.randint(100, ORIGINAL_HEIGHT - 100), scale, game_state)
                screen.blit(dice_face, (rand_x, rand_y))
        else:
            # End of animation, show final dice values
            roll = game_state['dice_roll']
            if is_expert_board:
                # Expert board - display both dice and total
                roll1 = game_state['dice_roll_1']
                roll2 = game_state['dice_roll_2']
                
                # Draw first die
                dice_face1 = current_dice_images[roll1 - 1]
                screen.blit(dice_face1, dice_rect1.topleft)
                
                # Draw second die
                dice_face2 = current_dice_images[roll2 - 1]
                screen.blit(dice_face2, dice_rect2.topleft)
                
                # Draw total
                total_font = pygame.font.SysFont(None, int(30 * scale * camera_zoom))
                total_text = total_font.render(f"Total: {roll}", True, BLACK)
                screen.blit(total_text, (total_text_pos[0] - total_text.get_width() // 2, total_text_pos[1]))
                
                # Store both dice values for later use
                game_state['final_dice_roll_1'] = roll1
                game_state['final_dice_roll_2'] = roll2
                
                # If doubles were rolled, play the special sound
                if game_state.get('is_doubles') and not game_state.get('doubles_sound_played', False):
                    # Play the Stylish sound for doubles
                    stylish_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Stylish.opus"))
                    stylish_sound.set_volume(0.5)  # Set to 50% volume to make it softer
                    stylish_sound.play()
                    game_state['doubles_sound_played'] = True
            else:
                # Classic board - single die
                dice_face = current_dice_images[roll - 1]
                screen.blit(dice_face, dice_rect.topleft)
            
            game_state['final_dice_roll'] = roll
            game_state['movement_delay_start'] = time.time()
            game_state['rolling_dice'] = False
    elif 'movement_delay_start' in game_state:
        current_time = time.time()
        roll = game_state['dice_roll']
        
        if is_expert_board:
            # Expert board - show both dice and total
            roll1 = game_state.get('final_dice_roll_1', 1)
            roll2 = game_state.get('final_dice_roll_2', 1)
            
            # Draw first die
            dice_face1 = current_dice_images[roll1 - 1]
            screen.blit(dice_face1, dice_rect1.topleft)
            
            # Draw second die
            dice_face2 = current_dice_images[roll2 - 1]
            screen.blit(dice_face2, dice_rect2.topleft)
            
            # Draw total
            total_font = pygame.font.SysFont(None, int(30 * scale * camera_zoom))
            total_text = total_font.render(f"Total: {roll}", True, BLACK)
            screen.blit(total_text, (total_text_pos[0] - total_text.get_width() // 2, total_text_pos[1]))
        else:
            # Classic board - single die
            dice_face = current_dice_images[roll - 1]
            screen.blit(dice_face, dice_rect.topleft)

        
        if current_time - game_state['movement_delay_start'] >= 0.5:
            del game_state['movement_delay_start']
            current_player = players[game_state['current_player']]
            current_player.position_history.append(current_player.position)
            if current_player.in_jail:
                # First check if player has a Get Out of Jail Free card
                if current_player.has_jail_free_card:
                    current_player.in_jail = False
                    current_player.has_jail_free_card = False  # Use up the card
                    # Clear the jail marker when player escapes jail
                    current_player.jail_from_x = None
                    current_player.jail_from_y = None
                    current_player.jail_marker_anim_start = None
                    
                    anim = {
                        'player': current_player,
                        'start_pos': JAIL_POS,
                        'end_pos': squares_coords[current_player.prev_position],
                        'steps': 60,
                        'current_step': 0,
                        'last_time': time.time(),
                        'message': f"Player {current_player.id + 1} used Get Out of Jail Free card!",
                        'is_jail_move': True,
                        'delay': 0.0167,  # ~60fps (1/60 second)
                        'jail_action': 'exit'
                    }
                    # Play the sound when animation starts
                    if current_player.is_computer:
                        audio.head_shake_cpu_sound.play()
                    else:
                        audio.head_shake_sound.play()
                    current_player.active_animations.append(anim)
                    game_state['message'] = f"Player {current_player.id + 1} used Get Out of Jail Free card!"
                    current_player.turn_ended = True
                elif roll % 2 == 0:
                    current_player.in_jail = False
                    # Clear the jail marker when player escapes jail
                    current_player.jail_from_x = None
                    current_player.jail_from_y = None
                    current_player.jail_marker_anim_start = None
                    anim = {
                        'player': current_player,
                        'start_pos': JAIL_POS,
                        'end_pos': squares_coords[current_player.prev_position],
                        'steps': 60,
                        'current_step': 0,
                        'last_time': time.time(),
                        'message': f"Player {current_player.id + 1} rolled {roll} (even). Escaping jail.",
                        'is_jail_move': True,
                        'delay': 0.0167,  # ~60fps (1/60 second)
                        'jail_action': 'exit'
                    }
                    # Play the sound when animation starts
                    if current_player.is_computer:
                        audio.head_shake_cpu_sound.play()
                    else:
                        audio.head_shake_sound.play()
                    current_player.active_animations.append(anim)
                    current_player.turn_ended = True
                else:
                    audio.bonk_sound.play()
                    game_state['message'] = f"Player {current_player.id + 1} rolled {roll} (odd). Still in jail."
                    current_player.turn_ended = True
            else:
                if isinstance(next_positions[current_player.position], list):
                    game_state['show_path_choice_after_roll'] = True
                    game_state['roll_for_path_choice'] = roll
                    game_state['spaces_remaining'] = roll  # Set remaining spaces to full roll
                    game_state['message'] = f"Player {current_player.id + 1} rolled {roll}. Choose a path."
                else:
                    movement_path = get_movement_path(current_player.position, roll, game_state, squares, next_positions)
                    anim = {
                        'player': current_player,
                        'path': movement_path,
                        'index': 0,
                        'last_time': time.time(),
                        'message': f"Player {current_player.id + 1} rolled {roll}. Moving {roll} spaces.",
                        'is_initial_move': True,
                        'delay': 0.5
                    }
                    current_player.active_animations.append(anim)
            current_player.has_rolled = True
    elif 'final_dice_roll' in game_state:
        if game_state.get('selected_board') == 'Expert':
            # Expert board - show both dice and total
            roll1 = game_state.get('final_dice_roll_1', 1)
            roll2 = game_state.get('final_dice_roll_2', 1)
            roll = game_state['final_dice_roll']
            
            # Define positions for expert board dice
            dice_rect1 = pygame.Rect(int((die_pos_x - 35) * scale + offset_x), int(die_pos_y * scale + offset_y), int(50 * scale), int(50 * scale))
            dice_rect2 = pygame.Rect(int((die_pos_x + 35) * scale + offset_x), int(die_pos_y * scale + offset_y), int(50 * scale), int(50 * scale))
            total_text_pos = (int(die_pos_x * scale + offset_x), int((die_pos_y + 60) * scale + offset_y))  # Moved further down to avoid collision
            
            # Draw first die
            dice_face1 = dice_images_scaled[roll1 - 1]
            screen.blit(dice_face1, dice_rect1.topleft)
            
            # Draw second die
            dice_face2 = dice_images_scaled[roll2 - 1]
            screen.blit(dice_face2, dice_rect2.topleft)
            
            # Draw total
            total_font = pygame.font.SysFont(None, int(30 * scale))
            total_text = total_font.render(f"Total: {roll}", True, BLACK)
            screen.blit(total_text, (total_text_pos[0] - total_text.get_width() // 2, total_text_pos[1]))
        else:
            # Classic board - single die
            dice_face = dice_images_scaled[game_state['final_dice_roll'] - 1]
            screen.blit(dice_face, dice_rect.topleft)





    position_counts = {}
    
    # Define current_player before drawing players
    current_player = players[game_state['current_player']]
    
    for player in players:
        if not player.finished or player.position == len(squares) - 1:
            key = None
            if player.in_jail:
                key = "jail"
            else:
                # Use a tuple of player's position coordinates as the key
                key = (player.current_x, player.current_y)
            
            if key in position_counts:
                position_counts[key].append(player)
            else:
                position_counts[key] = [player]

    # Draw players with offsets if multiple players are at the same position
    for position, players_at_position in position_counts.items():
        for idx, player in enumerate(players_at_position):
            if player.in_jail:
                # Use player-specific jail position if available, otherwise use center
                if player.jail_x is not None and player.jail_y is not None:
                    x, y = transform_coords(player.jail_x, player.jail_y, scale, game_state)
                else:
                    # Generate random position if somehow not set
                    jail_focus_x, jail_focus_y = JAIL_POS
                    jail_offset_x = random.randint(-int(JAIL_SIZE/3), int(JAIL_SIZE/3))
                    jail_offset_y = random.randint(-int(JAIL_SIZE/3), int(JAIL_SIZE/3))
                    player.jail_x = jail_focus_x + jail_offset_x
                    player.jail_y = jail_focus_y + jail_offset_y
                    x, y = transform_coords(player.jail_x, player.jail_y, scale, game_state)
            else:
                # Get base coordinates for the player
                target_x = player.current_x
                target_y = player.current_y
                
                # Special handling for GO square (position 0) to ensure player is centered
                if player.position == 0:
                    target_x = squares_coords[0][0]
                    target_y = squares_coords[0][1]
                
                # Apply offset if there are multiple players at this position
                if len(players_at_position) > 1:
                    # Calculate offset based on index
                    # First player stays centered, subsequent players get offset in a spiral pattern
                    if idx > 0:
                        # Offset amount (in world coordinates)
                        offset_amount = 15
                        
                        # Simple pattern: down and right for 2nd player, other directions for more players
                        if idx == 1:
                            target_x += offset_amount
                            target_y += offset_amount
                        elif idx == 2:
                            target_x -= offset_amount
                            target_y += offset_amount
                        elif idx == 3:
                            target_x -= offset_amount
                            target_y -= offset_amount
                        else:
                            # For more than 4 players, increase offset slightly for each additional player
                            angle = 2 * math.pi * (idx / 4)
                            distance = offset_amount * (1 + (idx // 4) * 0.5)
                            target_x += math.cos(angle) * distance
                            target_y += math.sin(angle) * distance
                
                x, y = transform_coords(target_x, target_y, scale, game_state)
            
            if player.is_computer:
                # Use the correct CPU image based on difficulty level
                img = current_cpu_difficulty_images.get(player.difficulty, current_cpu_difficulty_images.get('normal'))
            else:
                img = current_player_images[player.colour_index]

            
            # Scale up players during victory cutscene
            if game_state.get('victory_cutscene', False) and player.finished:
                # Use the stored victory scale factor if available, or check active animations
                scale_factor = getattr(player, 'victory_scale_factor', 1.0)
                
                # If no stored scale factor, check active animations
                if scale_factor == 1.0:
                    for anim in player.active_animations:
                        if anim.get('type') == 'victory_glide':
                            # Calculate scale factor based on animation progress
                            progress = min(1.0, (time.time() - anim['start_time']) / anim['duration'])
                            # Start at 1.0 and grow to the target scale_factor
                            scale_factor = 1.0 + (anim['scale_factor'] - 1.0) * progress
                            break
                
                if scale_factor > 1.0:
                    # Scale up the player image
                    orig_width, orig_height = img.get_width(), img.get_height()
                    new_width = int(orig_width * scale_factor)
                    new_height = int(orig_height * scale_factor)
                    img = pygame.transform.smoothscale(img, (new_width, new_height))
                    
                # Add drop shadow for players in victory cutscene
                if game_state.get('victory_cutscene', False) and player.finished:
                    # Create a surface for the shadow with same dimensions as the scaled image
                    shadow_surface = pygame.Surface((img.get_width(), img.get_height()), pygame.SRCALPHA)
                    
                    # Shadow offset and color
                    shadow_offset_x = 4
                    shadow_offset_y = 4
                    shadow_color = (20, 20, 20, 120)  # Dark with alpha
                    
                    # Create shadow by filling in the shape of the player image
                    for px in range(img.get_width()):
                        for py in range(img.get_height()):
                            try:
                                # Only add shadow where the player image has visible pixels
                                if img.get_at((px, py))[3] > 50:  # Check alpha channel
                                    shadow_surface.set_at((px, py), shadow_color)
                            except IndexError:
                                pass  # Skip any out of bounds pixels
                    
                    # Apply a slight blur effect to soften the shadow edges
                    shadow_img_width = img.get_width()
                    shadow_img_height = img.get_height()
                    smaller = pygame.transform.smoothscale(shadow_surface, (shadow_img_width // 2, shadow_img_height // 2))
                    shadow_surface = pygame.transform.smoothscale(smaller, (shadow_img_width, shadow_img_height))
                    
                    # Draw the shadow beneath and offset from the player
                    shadow_pos_x = x - img.get_width() // 2 + shadow_offset_x
                    shadow_pos_y = y - img.get_height() // 2 + shadow_offset_y
                    screen.blit(shadow_surface, (shadow_pos_x, shadow_pos_y))
                    
                    # Create a copy of the image with slight transparency (only if not in victory cutscene)
                    if not (game_state.get('victory_cutscene', False) and player.finished):
                        transparent_img = img.copy()
                        transparent_img.set_alpha(243)  # 95% of 255
                        screen.blit(transparent_img, (x - img.get_width() // 2, y - img.get_height() // 2))
                    else:
                        # Ensure 100% opacity for players in victory cutscene
                        screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))
            else:
                # Regular rendering for players (not in victory cutscene)
                # Check if this is the active player and there are multiple players
                if len(players) > 1 and player.id == current_player.id:
                    # Create a surface for the shadow with same dimensions as the image
                    shadow_surface = pygame.Surface((img.get_width(), img.get_height()), pygame.SRCALPHA)
                    
                    # Shadow offset and color
                    shadow_offset_x = 3
                    shadow_offset_y = 3
                    shadow_color = (20, 20, 20, 120)  # Dark with alpha
                    
                    # Create shadow by filling in the shape of the player image
                    for px in range(img.get_width()):
                        for py in range(img.get_height()):
                            try:
                                # Only add shadow where the player image has visible pixels
                                if img.get_at((px, py))[3] > 50:  # Check alpha channel
                                    shadow_surface.set_at((px, py), shadow_color)
                            except IndexError:
                                pass  # Skip any out of bounds pixels
                    
                    # Apply a slight blur effect to soften the shadow edges
                    shadow_img_width = img.get_width()
                    shadow_img_height = img.get_height()
                    smaller = pygame.transform.smoothscale(shadow_surface, (shadow_img_width // 2, shadow_img_height // 2))
                    shadow_surface = pygame.transform.smoothscale(smaller, (shadow_img_width, shadow_img_height))
                    
                    # Draw the shadow beneath and offset from the player
                    shadow_pos_x = x - img.get_width() // 2 + shadow_offset_x
                    shadow_pos_y = y - img.get_height() // 2 + shadow_offset_y
                    screen.blit(shadow_surface, (shadow_pos_x, shadow_pos_y))
                    
                    # Create a copy of the image with slight transparency for active player
                    transparent_img = img.copy()
                    transparent_img.set_alpha(243)  # 95% of 255
                    screen.blit(transparent_img, (x - img.get_width() // 2, y - img.get_height() // 2))
                else:
                    # Regular rendering for non-active players
                    screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))

    # current_player is already defined before drawing players
    next_id = (game_state['current_player'] + 1) % len(players)
    while next_id < len(players) and players[next_id].finished and len(game_state.get('finish_order', [])) < len(players):
        next_id = (next_id + 1) % len(players)
    
    # Only show the original status display if the modern one is disabled
    if not game_state.get('use_modern_status_display', True):
        if next_id < len(players):
            next_player = players[next_id]
            render_player_text(screen, font, "Current Turn: ", current_player, int(50 * scale), scale, offset_y, player_colours)
            render_player_text(screen, font, "Next Turn: ", next_player, int(80 * scale), scale, offset_y, player_colours)
    
        if 'message' in game_state:
            render_coloured_message(screen, font, game_state['message'], int(50 * scale), int(500 * scale), offset_x, offset_y, players, player_colours)


    # (Path choice dialog is drawn after the quiz section, below, so it
    #  renders on top of bonus cards and quiz — see "Draw path choice" below.)


    button_size = int(50 * scale)
    # Positioning buttons: Restart, Achievement, Settings
    # Positioning buttons: Restart, Achievement, Settings, Magnify
    restart_button_rect = pygame.Rect(int(610 * scale + offset_x), int(540 * scale + offset_y), button_size, button_size)
    achievement_button_rect = pygame.Rect(int(670 * scale + offset_x), int(540 * scale + offset_y), button_size, button_size)
    settings_button_rect = pygame.Rect(int(730 * scale + offset_x), int(540 * scale + offset_y), button_size, button_size)
    magnify_button_rect = pygame.Rect(int(790 * scale + offset_x), int(540 * scale + offset_y), button_size, button_size)

    
    if 'fade_start' in game_state:
        fade_time = time.time() - game_state['fade_start']
        if fade_time < 0.7:  # Spinning phase: 3 spins in 0.7 seconds
            angle = (fade_time * 1080 / 0.7) % 360
            rotated_button = pygame.transform.rotate(restart_button_scaled, angle)
            rotated_rect = rotated_button.get_rect(center=restart_button_rect.center)
            screen.blit(rotated_button, rotated_rect.topleft)
        elif fade_time < 1.0:  # Fade-out phase: 0.3 seconds
            alpha = int(255 * (1 - (fade_time - 0.7) / 0.3))
            faded_button = restart_button_scaled.copy()
            faded_button.set_alpha(alpha)
            screen.blit(faded_button, restart_button_rect.topleft)
    elif game_state.get('restart_hold_start') is not None:
        hold_time = time.time() - game_state['restart_hold_start']
        progress = min(hold_time / 1.5, 1.0)
        shake_offset = int(5 * math.sin(hold_time * 10))
        draw_pos = (restart_button_rect.x + shake_offset, restart_button_rect.y)
        screen.blit(restart_button_scaled, draw_pos)
        
        # Adjust bar width and position to ensure it reaches the end of the button
        # Make sure the bar width exactly matches the button width when progress is 100%
        bar_width = int(restart_button_scaled.get_width() * progress)
        bar_height = int(5 * scale)
        bar_rect = pygame.Rect(draw_pos[0], draw_pos[1] + restart_button_scaled.get_height(), bar_width, bar_height)
        pygame.draw.rect(screen, GREEN, bar_rect)
    else:
        screen.blit(restart_button_scaled, restart_button_rect.topleft)
    
    # Achievement button between restart and settings
    screen.blit(achievement_button_scaled, achievement_button_rect.topleft)
    
    # Settings button
    screen.blit(settings_button_scaled, settings_button_rect.topleft)
    
    # Magnify button to the right of settings button
    screen.blit(magnify_button_scaled, magnify_button_rect.topleft)

    
    # Draw settings menu if active
    if game_state.get('show_settings_menu', False):
        # Create menu background
        menu_width = int(200 * scale)
        menu_height = int(280 * scale)  # Increased to fit the timer toggle and fix volume slider
        
        # Calculate initial position (centered above settings button)
        menu_x = settings_button_rect.x + (settings_button_rect.width // 2) - (menu_width // 2)
        menu_y = settings_button_rect.y - menu_height - int(10 * scale)  # Position menu above button with 10px gap
        
        # Get window size to ensure menu stays within bounds
        window_width, window_height = screen.get_size()
        
        # Ensure menu doesn't go outside window boundaries
        # Check right edge
        if menu_x + menu_width > window_width:
            menu_x = window_width - menu_width - int(5 * scale)  # 5px padding from edge
        
        # Check left edge
        if menu_x < 0:
            menu_x = int(5 * scale)  # 5px padding from edge
            
        # Check top edge
        if menu_y < 0:
            menu_y = int(5 * scale)  # 5px padding from edge
            
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        
        # Draw menu background with border
        pygame.draw.rect(screen, (240, 240, 240), menu_rect)  # Light gray background
        pygame.draw.rect(screen, (40, 40, 40), menu_rect, 2)  # Dark gray border
        
        # Draw title
        title_font = pygame.font.SysFont(None, int(28 * scale))
        title_text = title_font.render("Settings", True, (0, 0, 0))
        screen.blit(title_text, (menu_x + int(10 * scale), menu_y + int(10 * scale)))
        
        # Horizontal separator line
        pygame.draw.line(screen, (150, 150, 150), 
                         (menu_x + int(5 * scale), menu_y + int(40 * scale)),
                         (menu_x + menu_width - int(5 * scale), menu_y + int(40 * scale)), 
                         1)
        
        # Game status toggle
        status_font = pygame.font.SysFont(None, int(22 * scale))
        status_text = status_font.render("Show Game Status:", True, (0, 0, 0))
        screen.blit(status_text, (menu_x + int(10 * scale), menu_y + int(55 * scale)))
        
        # Toggle button for game status
        toggle_width = int(40 * scale)
        toggle_height = int(20 * scale)
        status_toggle_rect = pygame.Rect(menu_x + menu_width - toggle_width - int(10 * scale), 
                                        menu_y + int(55 * scale), toggle_width, toggle_height)
        
        # Draw toggle background (green if enabled, gray if disabled)
        toggle_color = (100, 200, 100) if game_state.get('show_game_status', False) else (150, 150, 150)
        pygame.draw.rect(screen, toggle_color, status_toggle_rect, border_radius=int(10 * scale))
        
        # Draw toggle handle
        handle_pos = status_toggle_rect.right - int(18 * scale) if game_state.get('show_game_status', False) else status_toggle_rect.left + int(2 * scale)
        handle_rect = pygame.Rect(handle_pos, status_toggle_rect.y + int(2 * scale), int(16 * scale), int(16 * scale))
        pygame.draw.rect(screen, (240, 240, 240), handle_rect, border_radius=int(8 * scale))
        
        game_state['status_toggle_rect'] = status_toggle_rect
        
        # Status display toggle (renamed from "Modern Display" to just "Status Display")
        style_text = status_font.render("Status Display:", True, (0, 0, 0))
        screen.blit(style_text, (menu_x + int(10 * scale), menu_y + int(85 * scale)))
        
        # Toggle button for display style
        style_toggle_rect = pygame.Rect(menu_x + menu_width - toggle_width - int(10 * scale), 
                                      menu_y + int(85 * scale), toggle_width, toggle_height)
        
        # Draw toggle background (green if enabled, gray if disabled)
        # Fix the inconsistency - toggle should be ON (green) when the feature is enabled
        toggle_color = (100, 200, 100) if game_state.get('use_modern_status_display', True) else (150, 150, 150)
        pygame.draw.rect(screen, toggle_color, style_toggle_rect, border_radius=int(10 * scale))
        
        # Draw toggle handle - also fix the handle position to match the state
        handle_pos = style_toggle_rect.right - int(18 * scale) if game_state.get('use_modern_status_display', True) else style_toggle_rect.left + int(2 * scale)
        handle_rect = pygame.Rect(handle_pos, style_toggle_rect.y + int(2 * scale), int(16 * scale), int(16 * scale))
        pygame.draw.rect(screen, (240, 240, 240), handle_rect, border_radius=int(8 * scale))
        
        game_state['style_toggle_rect'] = style_toggle_rect
        
        # Show timer toggle
        timer_text = status_font.render("Show Timers:", True, (0, 0, 0))
        screen.blit(timer_text, (menu_x + int(10 * scale), menu_y + int(115 * scale)))
        
        # Toggle button for timer display
        timer_toggle_rect = pygame.Rect(menu_x + menu_width - toggle_width - int(10 * scale), 
                                      menu_y + int(115 * scale), toggle_width, toggle_height)
        
        # Draw toggle background (green if enabled, gray if disabled)
        toggle_color = (100, 200, 100) if game_state.get('show_timers', True) else (150, 150, 150)
        pygame.draw.rect(screen, toggle_color, timer_toggle_rect, border_radius=int(10 * scale))
        
        # Draw toggle handle
        handle_pos = timer_toggle_rect.right - int(18 * scale) if game_state.get('show_timers', True) else timer_toggle_rect.left + int(2 * scale)
        handle_rect = pygame.Rect(handle_pos, timer_toggle_rect.y + int(2 * scale), int(16 * scale), int(16 * scale))
        pygame.draw.rect(screen, (240, 240, 240), handle_rect, border_radius=int(8 * scale))
        
        game_state['timer_toggle_rect'] = timer_toggle_rect
        
        # Volume control
        volume_text = status_font.render("Master Volume:", True, (0, 0, 0))
        screen.blit(volume_text, (menu_x + int(10 * scale), menu_y + int(145 * scale)))
        
        # Volume slider
        slider_width = int(150 * scale)
        slider_height = int(10 * scale)
        slider_rect = pygame.Rect(menu_x + int(25 * scale), menu_y + int(170 * scale), slider_width, slider_height)
        
        # Draw slider track
        pygame.draw.rect(screen, (150, 150, 150), slider_rect, border_radius=int(5 * scale))
        
        # Draw slider handle based on volume value
        volume = game_state.get('master_volume', 1.0)  # Default to 1.0 (100%)
        handle_pos = slider_rect.left + int(volume * slider_width)
        handle_rect = pygame.Rect(handle_pos - int(8 * scale), slider_rect.y - int(5 * scale), 
                                int(16 * scale), int(20 * scale))
        pygame.draw.rect(screen, (80, 80, 230), handle_rect, border_radius=int(8 * scale))
        
        # Store slider rect for interaction
        game_state['volume_slider_rect'] = slider_rect
        game_state['volume_slider_width'] = slider_width
        
        # Add Reset to Default button
        reset_button_width = int(150 * scale)
        reset_button_height = int(30 * scale)
        reset_button_x = menu_x + (menu_width - reset_button_width) // 2
        reset_button_y = menu_y + int(210 * scale)
        reset_button_rect = pygame.Rect(reset_button_x, reset_button_y, reset_button_width, reset_button_height)
        
        # Draw button
        pygame.draw.rect(screen, (220, 220, 220), reset_button_rect, border_radius=int(5 * scale))
        pygame.draw.rect(screen, (100, 100, 100), reset_button_rect, 2, border_radius=int(5 * scale))
        
        # Button text
        reset_text = status_font.render("Reset to Default", True, (0, 0, 0))
        text_x = reset_button_rect.x + (reset_button_rect.width - reset_text.get_width()) // 2
        text_y = reset_button_rect.y + (reset_button_rect.height - reset_text.get_height()) // 2
        screen.blit(reset_text, (text_x, text_y))
        
        # Store button rect for interaction
        game_state['reset_button_rect'] = reset_button_rect
        
    # Draw game status if enabled
    if game_state.get('show_game_status', True) and game_state.get('use_modern_status_display', False):
        # Display the current turn and next turn information
        current_player = players[game_state['current_player']]
        next_player_idx = (game_state['current_player'] + 1) % len(players)
        while next_player_idx < len(players) and players[next_player_idx].finished and len(game_state['finish_order']) < len(players) - 1:
            next_player_idx = (next_player_idx + 1) % len(players)
        next_player = players[next_player_idx]
        
        status_font = pygame.font.SysFont(None, int(20 * scale))
        message_font = pygame.font.SysFont(None, int(18 * scale))
        
        # Position the status display to the right side of the board
        # Use coordinates that are less likely to overlap with game elements
        right_panel_x = int(650 * scale + offset_x)  # Position to the right side of the board
        right_panel_y = int(100 * scale + offset_y)  # Position down from the top edge
        max_panel_width = int(200 * scale)  # Limit width of panel
        
        # Current player info
        current_player_text = f"Current: Player {current_player.id + 1}"
        if current_player.finished:
            current_player_text += " (Finished)"
        elif current_player.in_jail:
            current_player_text += " (In Jail)"
        
        # Display current player info
        color = player_colours[current_player.colour_index]
        current_text = status_font.render(current_player_text, True, color)
        screen.blit(current_text, (right_panel_x, right_panel_y))
        
        # Next player info if not all finished
        next_y = right_panel_y + status_font.get_height() + int(5 * scale)
        if len(game_state['finish_order']) < len(players) - 1:
            next_player_text = f"Next: Player {next_player.id + 1}"
            if next_player.in_jail:
                next_player_text += " (In Jail)"
                
            next_color = player_colours[next_player.colour_index]
            next_text = status_font.render(next_player_text, True, next_color)
            screen.blit(next_text, (right_panel_x, next_y))
        
        # Display game message if present, using proper text wrapping
        if game_state.get('message'):
            # Improved message positioning with wrapping
            message_y = next_y + status_font.get_height() + int(10 * scale)
            
            # Use render_wrapped_text to wrap long messages properly
            message_text = game_state['message']
            
            # Improved rendering to handle colored player references in wrapped text
            parts = message_text.split("Player ")
            
            if len(parts) == 1:
                # No player references, just render the whole message
                render_wrapped_text(screen, message_font, message_text, max_panel_width, 
                                   right_panel_x, message_y, (50, 50, 50))
            else:
                # There are player references, need to handle coloring
                # We'll build a simpler version that at least works for messages at the beginning
                
                # Start with any text before the first "Player" mention
                current_y = message_y
                current_x = right_panel_x
                line_height = message_font.get_height() + int(2 * scale)
                
                # Draw prefix (if any)
                if parts[0]:
                    # Use wrapped text for the first part too
                    height = render_wrapped_text(screen, message_font, parts[0], max_panel_width, 
                                               current_x, current_y, (50, 50, 50))
                    current_y += height + int(2 * scale)
                    current_x = right_panel_x
                
                # For each "Player N" mention
                for i, part in enumerate(parts[1:], 1):
                    # Extract player number
                    player_num = ""
                    j = 0
                    while j < len(part) and part[j].isdigit():
                        player_num += part[j]
                        j += 1
                    
                    remainder = part[j:] if j < len(part) else ""
                    
                    if player_num:
                        try:
                            player_idx = int(player_num) - 1
                            if 0 <= player_idx < len(players):
                                # Render "Player" in black
                                player_text = message_font.render("Player ", True, (50, 50, 50))
                                # Check if we need to wrap to next line
                                if current_x + player_text.get_width() > right_panel_x + max_panel_width:
                                    current_x = right_panel_x
                                    current_y += line_height
                                
                                screen.blit(player_text, (current_x, current_y))
                                current_x += player_text.get_width()
                                
                                # Render player number in player's color
                                player_color = player_colours[players[player_idx].colour_index]
                                number_text = message_font.render(player_num, True, player_color)
                                screen.blit(number_text, (current_x, current_y))
                                current_x += number_text.get_width()
                                
                                # Render remainder
                                if remainder:
                                    # Wrap the remainder text properly
                                    if current_x > right_panel_x:
                                        # Check if there's enough space for at least a few chars
                                        if current_x + message_font.size(remainder[:5])[0] > right_panel_x + max_panel_width:
                                            current_x = right_panel_x
                                            current_y += line_height
                                    
                                    # Use wrapped text for the remainder too
                                    height = render_wrapped_text(screen, message_font, remainder, 
                                                                max_panel_width - (current_x - right_panel_x),
                                                                current_x, current_y, (50, 50, 50))
                                    current_y += height
                                    current_x = right_panel_x
                            else:
                                # Invalid player number, render whole part
                                full_text = message_font.render(f"Player {part}", True, (50, 50, 50))
                                if current_x + full_text.get_width() > right_panel_x + max_panel_width:
                                    current_x = right_panel_x
                                    current_y += line_height
                                
                                screen.blit(full_text, (current_x, current_y))
                                current_x += full_text.get_width()
                        except ValueError:
                            # Not a valid number, render the whole part
                            full_text = message_font.render(f"Player {part}", True, (50, 50, 50))
                            if current_x + full_text.get_width() > right_panel_x + max_panel_width:
                                current_x = right_panel_x
                                current_y += line_height
                            
                            screen.blit(full_text, (current_x, current_y))
                            current_x += full_text.get_width()
                    else:
                        # No player number found, render the whole part
                        full_text = message_font.render(f"Player {part}", True, (50, 50, 50))
                        if current_x + full_text.get_width() > right_panel_x + max_panel_width:
                            current_x = right_panel_x
                            current_y += line_height
                        
                        screen.blit(full_text, (current_x, current_y))
                        current_x += full_text.get_width()

    # ---------------------------------------------------------------------------
    # Draw active bonus image and activated cards — Moved here to be ABOVE 
    # players (rendered earlier), satisfying the "except when activated" rule.
    # ---------------------------------------------------------------------------
    # Helper for drawing card with shadow
    def draw_card_with_shadow(surf, pos, rot, scale_val):
        # Calculate shadow offset based on lift (scale_val)
        shadow_offset = int(12 * scale * scale_val)

        # Create shadow surface
        rotated_surf = pygame.transform.rotate(surf, rot)
        shadow_surf = rotated_surf.copy()
        shadow_surf.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)

        # Draw shadow
        shadow_rect = shadow_surf.get_rect(center=(pos[0] + shadow_offset, pos[1] + shadow_offset))
        screen.blit(shadow_surf, shadow_rect.topleft)

        # Draw card
        card_rect = rotated_surf.get_rect(center=pos)
        screen.blit(rotated_surf, card_rect.topleft)

    # Helper for drawing player badge on quiz card
    def draw_player_badge(surface, player, badge_pos, badge_size):
        # Calculate sizes
        outer_radius = badge_size // 2
        inner_radius = int(outer_radius * 0.85)
        icon_size = int(badge_size * 0.75)
        
        # Shadow for the badge
        shadow_surf = pygame.Surface((badge_size + 4, badge_size + 4), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, (0, 0, 0, 80), (outer_radius + 2, outer_radius + 2), outer_radius)
        surface.blit(shadow_surf, (badge_pos[0] - outer_radius - 2, badge_pos[1] - outer_radius - 2))
        
        # Outer white ring
        pygame.draw.circle(surface, WHITE, badge_pos, outer_radius)
        
        # Inner coloured circle
        badge_colour = player_colours[player.colour_index]
        pygame.draw.circle(surface, badge_colour, badge_pos, inner_radius)
        
        # Player icon
        if player.is_computer:
            # Use difficulty-specific CPU icon if available
            icon_img = cpu_difficulty_images_scaled.get(player.difficulty, cpu_image_scaled)
        else:
            icon_img = player_images_scaled[player.colour_index]
            
        scaled_icon = pygame.transform.smoothscale(icon_img, (icon_size, icon_size))
        scaled_icon.set_alpha(255)  # Ensure 100% opacity
        surface.blit(scaled_icon, (badge_pos[0] - icon_size // 2, badge_pos[1] - icon_size // 2))

    # Draw active bonus image
    if 'bonus_image_key' in game_state and 'bonus_image_state' in game_state:
        image = bonus_result_images_scaled[game_state['bonus_image_key']]
        state = game_state['bonus_image_state']

        if state == 'growing':
            elapsed = time.time() - game_state['bonus_grow_start']
            scale_factor = min(1.0, elapsed / 1.0)
            rotation = 90 * (1.0 - scale_factor)

            start_x = die_center_x - deck_offset
            current_x = start_x + (die_center_x - start_x) * scale_factor
            current_y = die_center_y

            anim_scale = 0.45 + (1.0 - 0.45) * scale_factor
            scaled_width = int(cover_bonus_scaled.get_width() * anim_scale)
            scaled_height = int(cover_bonus_scaled.get_height() * anim_scale)
            scaled_image = pygame.transform.smoothscale(cover_bonus_scaled, (scaled_width, scaled_height))
            draw_card_with_shadow(scaled_image, (current_x, current_y), rotation, scale_factor)
        elif state == 'flipping':
            elapsed = time.time() - game_state['bonus_flip_start']
            t = elapsed / 0.5
            if t < 0.5:
                width_scale = 1 - 2 * t
                img = cover_bonus_scaled
            else:
                width_scale = 2 * (t - 0.5)
                img = image
            scaled_width = max(1, int(img.get_width() * width_scale))
            scaled_image = pygame.transform.smoothscale(img, (scaled_width, img.get_height()))
            draw_card_with_shadow(scaled_image, (die_center_x, die_center_y), 0, 1.0)
        elif state == 'showing':
            draw_card_with_shadow(image, (die_center_x, die_center_y), 0, 1.0)
        elif state == 'flipping_back':
            elapsed = time.time() - game_state['bonus_flip_back_start']
            t = elapsed / 0.5
            if t < 0.5:
                width_scale = 1 - 2 * t
                img = image
            else:
                width_scale = 2 * (t - 0.5)
                img = cover_bonus_scaled
            scaled_width = max(1, int(img.get_width() * width_scale))
            scaled_image = pygame.transform.smoothscale(img, (scaled_width, img.get_height()))
            draw_card_with_shadow(scaled_image, (die_center_x, die_center_y), 0, 1.0)
        elif state == 'shrinking':
            elapsed = time.time() - game_state['bonus_shrink_start']
            scale_factor = max(0.0, 1.0 - elapsed / 1.0)
            rotation = 90 * (1.0 - scale_factor)

            end_x = die_center_x - deck_offset
            current_x = die_center_x + (end_x - die_center_x) * (1.0 - scale_factor)
            current_y = die_center_y

            anim_scale = 0.45 + (1.0 - 0.45) * scale_factor
            scaled_width = int(cover_bonus_scaled.get_width() * anim_scale)
            scaled_height = int(cover_bonus_scaled.get_height() * anim_scale)
            scaled_image = pygame.transform.smoothscale(cover_bonus_scaled, (scaled_width, scaled_height))
            draw_card_with_shadow(scaled_image, (current_x, current_y), rotation, scale_factor)


    # Draw quiz last to ensure it's always on top
    if game_state.get('show_quiz', False) and game_state.get('quiz_question'):
        # Build a label string identifying the current player
        _quiz_player = players[game_state['current_player']]
        if _quiz_player.is_computer:
            _quiz_player_label = f"CPU Player {_quiz_player.id + 1}"
        else:
            _quiz_player_label = f"Player {_quiz_player.id + 1}"
        _quiz_label_colour = player_colours[_quiz_player.colour_index]
        _quiz_label_font = pygame.font.SysFont(None, int(18 * scale), bold=True)
        current_time = time.time()
        elapsed = current_time - game_state['quiz_start_time']
        # Update quiz dimensions to match bonus cards with 4:3 aspect ratio
        quiz_width = int(320 * scale)  # Increased width to provide more height at 4:3 ratio
        quiz_height = int(quiz_width * 3 / 4)  # Restored correct 4:3 aspect ratio
        if game_state['quiz_state'] == 'growing':
            scale_factor = min(1.0, elapsed / 1.0)
            rotation = -90 * (1.0 - scale_factor)
            
            start_x = die_center_x + deck_offset
            current_x = start_x + (die_center_x - start_x) * scale_factor
            current_y = die_center_y
            
            anim_scale = 0.45 + (1.0 - 0.45) * scale_factor
            width = int(quiz_width * anim_scale)
            height = int(quiz_height * anim_scale)
            
            scaled_cover = pygame.transform.smoothscale(cover_quiz_scaled, (width, height))
            draw_card_with_shadow(scaled_cover, (current_x, current_y), rotation, scale_factor)
            
            if elapsed >= 1.0:
                game_state['quiz_state'] = 'flipping'
                game_state['quiz_flip_start'] = current_time
        elif game_state['quiz_state'] == 'flipping':
            elapsed_flip = current_time - game_state['quiz_flip_start']
            t = elapsed_flip / 0.5
            if t < 0.5:
                width_scale = 1 - 2 * t
                scaled_width = max(1, int(quiz_width * width_scale))
                scaled_img = pygame.transform.smoothscale(cover_quiz_scaled, (scaled_width, quiz_height))
                draw_card_with_shadow(scaled_img, (die_center_x, die_center_y), 0, 1.0)
            else:
                width_scale = 2 * (t - 0.5)
                scaled_width = max(1, int(quiz_width * width_scale))
                rect = pygame.Rect(die_center_x - scaled_width // 2, die_center_y - quiz_height // 2, scaled_width, quiz_height)
                # Shadow for the white rectangle is simpler
                shadow_offset = int(12 * scale)
                shadow_rect = rect.copy()
                shadow_rect.x += shadow_offset
                shadow_rect.y += shadow_offset
                pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
                pygame.draw.rect(screen, WHITE, rect)
            if elapsed_flip >= 0.5:
                game_state['quiz_state'] = 'waiting'
                game_state['quiz_timer'] = current_time + 1.0
        elif game_state['quiz_state'] == 'waiting':
            rect = pygame.Rect(die_center_x - quiz_width // 2, die_center_y - quiz_height // 2, quiz_width, quiz_height)
            # Shadow
            shadow_offset = int(12 * scale)
            shadow_rect = rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
            pygame.draw.rect(screen, WHITE, rect)
            text_margin = int(10 * scale)
            # Draw the player badge hovering over the top-left corner
            badge_size = int(48 * scale)
            badge_pos = (rect.left, rect.top)
            draw_player_badge(screen, _quiz_player, badge_pos, badge_size)
            
            # Render player label inside the card, offset for the badge
            _label_surf = _quiz_label_font.render(_quiz_player_label, True, _quiz_label_colour)
            screen.blit(_label_surf, (rect.x + text_margin + int(20 * scale), rect.y + text_margin))
            _label_h = _label_surf.get_height() + int(4 * scale)
            question, options, _ = game_state['quiz_question']
            max_text_width = quiz_width - 2 * text_margin
            render_wrapped_text(screen, font, question, max_text_width,
                               rect.x + text_margin, rect.y + text_margin + _label_h)
            if current_time >= game_state['quiz_timer']:
                game_state['quiz_state'] = 'buttons'
                game_state['pop_played'] = False
        elif game_state['quiz_state'] == 'buttons':
            if not game_state['pop_played']:
                audio.pop_sound.play()
                game_state['pop_played'] = True
            rect = pygame.Rect(die_center_x - quiz_width // 2, die_center_y - quiz_height // 2, quiz_width, quiz_height)
            # Shadow
            shadow_offset = int(12 * scale)
            shadow_rect = rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
            pygame.draw.rect(screen, WHITE, rect)
            text_margin = int(10 * scale)
            # Draw the player badge hovering over the top-left corner
            badge_size = int(48 * scale)
            badge_pos = (rect.left, rect.top)
            draw_player_badge(screen, _quiz_player, badge_pos, badge_size)
            
            # Render player label inside the card, offset for the badge
            _label_surf = _quiz_label_font.render(_quiz_player_label, True, _quiz_label_colour)
            screen.blit(_label_surf, (rect.x + text_margin + int(20 * scale), rect.y + text_margin))
            _label_h = _label_surf.get_height() + int(4 * scale)
            question, options, _ = game_state['quiz_question']
            max_text_width = quiz_width - 2 * text_margin
            question_height = render_wrapped_text(screen, font, question, max_text_width,
                                                rect.x + text_margin, rect.y + text_margin + _label_h)
            question_height += _label_h
            quiz_buttons = []
            min_button_height = int(25 * scale)
            button_spacing = int(5 * scale)
            button_start_y = rect.y + text_margin + question_height + button_spacing
            current_y = button_start_y
            for i, option in enumerate(options):
                option_margin = int(5 * scale)
                max_option_width = quiz_width - 2 * text_margin - 2 * option_margin
                option_length = len(option)
                if option_length > 80:
                    option_font = pygame.font.SysFont(None, int(14 * scale))
                elif option_length > 50:
                    option_font = pygame.font.SysFont(None, int(16 * scale))
                else:
                    option_font = font
                temp_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
                text_height = render_wrapped_text(temp_surface, option_font, option, max_option_width, 0, 0, WHITE, return_height_only=True)
                button_height = max(min_button_height, text_height + 2 * option_margin)
                button = pygame.Rect(rect.x + text_margin, current_y, quiz_width - 2 * text_margin, button_height)
                current_y += button_height + button_spacing
                button_color = BLUE
                if 'clicked_quiz_button' in game_state and game_state['clicked_quiz_button'] == i:
                    click_elapsed = current_time - game_state['button_click_time']
                    if click_elapsed < 0.3:
                        button_color = (100, 100, 200)
                    else:
                        del game_state['clicked_quiz_button']
                        del game_state['button_click_time']
                pygame.draw.rect(screen, button_color, button)
                number_text = f"{i+1}."
                number_surface = option_font.render(number_text, True, YELLOW)
                number_rect = number_surface.get_rect()
                number_rect.left = button.x + option_margin
                number_rect.top = button.y + option_margin
                screen.blit(number_surface, number_rect)
                option_text_x = button.x + option_margin + number_surface.get_width() + 5
                render_wrapped_text(screen, option_font, option, max_option_width - number_surface.get_width() - 5, 
                                   option_text_x, button.y + option_margin, WHITE)
                quiz_buttons.append((button, i))
            game_state['quiz_buttons'] = quiz_buttons
        elif game_state['quiz_state'] == 'answered':
            rect = pygame.Rect(die_center_x - quiz_width // 2, die_center_y - quiz_height // 2, quiz_width, quiz_height)
            # Shadow
            shadow_offset = int(12 * scale)
            shadow_rect = rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
            pygame.draw.rect(screen, WHITE, rect)
            text_margin = int(10 * scale)
            # Draw the player badge hovering over the top-left corner
            badge_size = int(48 * scale)
            badge_pos = (rect.left, rect.top)
            draw_player_badge(screen, _quiz_player, badge_pos, badge_size)
            
            # Render player label inside the card, offset for the badge
            _label_surf = _quiz_label_font.render(_quiz_player_label, True, _quiz_label_colour)
            screen.blit(_label_surf, (rect.x + text_margin + int(20 * scale), rect.y + text_margin))
            _label_h = _label_surf.get_height() + int(4 * scale)
            question, _, _ = game_state['quiz_question']
            max_text_width = quiz_width - 2 * text_margin
            render_wrapped_text(screen, font, question, max_text_width,
                               rect.x + text_margin, rect.y + text_margin + _label_h)
            if current_time - game_state['quiz_answer_delay_start'] >= 2.0:
                game_state['quiz_state'] = 'flipping_back'
                game_state['quiz_flip_back_start'] = current_time
                audio.disconnect_sound.play()
        elif game_state['quiz_state'] == 'flipping_back':
            elapsed_flip = current_time - game_state['quiz_flip_back_start']
            t = elapsed_flip / 0.5
            if t < 0.5:
                width_scale = 1 - 2 * t
                scaled_width = max(1, int(quiz_width * width_scale))
                rect = pygame.Rect(die_center_x - scaled_width // 2, die_center_y - quiz_height // 2, scaled_width, quiz_height)
                # Shadow
                shadow_offset = int(12 * scale)
                shadow_rect = rect.copy()
                shadow_rect.x += shadow_offset
                shadow_rect.y += shadow_offset
                pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
                pygame.draw.rect(screen, WHITE, rect)
            else:
                width_scale = 2 * (t - 0.5)
                scaled_width = max(1, int(quiz_width * width_scale))
                scaled_img = pygame.transform.smoothscale(cover_quiz_scaled, (scaled_width, quiz_height))
                draw_card_with_shadow(scaled_img, (die_center_x, die_center_y), 0, 1.0)
            if elapsed_flip >= 0.5:
                game_state['quiz_state'] = 'shrinking'
                game_state['quiz_shrink_start'] = current_time
        elif game_state['quiz_state'] == 'shrinking':
            elapsed_shrink = current_time - game_state['quiz_shrink_start']
            scale_factor = max(0.0, 1.0 - elapsed_shrink / 1.0)
            rotation = -90 * (1.0 - scale_factor)
            
            end_x = die_center_x + deck_offset
            current_x = die_center_x + (end_x - die_center_x) * (1.0 - scale_factor)
            current_y = die_center_y
            
            anim_scale = 0.45 + (1.0 - 0.45) * scale_factor
            width = int(quiz_width * anim_scale)
            height = int(quiz_height * anim_scale)
            
            scaled_cover = pygame.transform.smoothscale(cover_quiz_scaled, (width, height))
            draw_card_with_shadow(scaled_cover, (current_x, current_y), rotation, scale_factor)
            
            if elapsed_shrink >= 1.0:
                game_state['show_quiz'] = False
                del game_state['quiz_question']
                del game_state['quiz_shrink_start']
                if 'quiz_answer_delay_start' in game_state:
                    del game_state['quiz_answer_delay_start']

    # Draw path choice on top of everything (bonus cards, quiz, players)
    if game_state.get('show_path_choice_after_roll', False):
        current_player = players[game_state['current_player']]
        current_pos = current_player.position
        choices = next_positions[current_pos]
        remaining_spaces = game_state.get('spaces_remaining', 0)

        # Show ghost players at potential end positions
        for choice in choices:
            full_path = get_movement_path_with_choice(current_pos, choice, remaining_spaces, squares, next_positions)
            ending_pos = full_path[-1]

            x, y = squares_coords[ending_pos]
            x = int(x * scale + offset_x)
            y = int(y * scale + offset_y)

            # Draw a special marker for the end position
            pygame.draw.circle(screen, (255, 255, 0), (x, y), int(20 * scale), 3)

            # Draw the ghost player
            img = player_images_scaled[current_player.colour_index]
            img_copy = img.copy()
            img_copy.set_alpha(150)
            screen.blit(img_copy, (x - img_copy.get_width() // 2, y - img_copy.get_height() // 2))

        # Draw path choice dialog centered on die position
        dialog_width = int(300 * scale)
        dialog_height = int(180 * scale)
        rect = pygame.Rect(die_center_x - dialog_width // 2, die_center_y - dialog_height // 2, dialog_width, dialog_height)

        # Draw dialog background with border
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, (0, 0, 100), rect, 3)  # Dark blue border

        # Build player label for who is choosing
        _path_label_font = pygame.font.SysFont(None, int(18 * scale))
        if current_player.is_computer:
            _path_player_label = f"CPU Player {current_player.id + 1} — Choose a Path!"
        else:
            _path_player_label = f"Player {current_player.id + 1} — Choose Your Path!"
        _path_label_colour = player_colours[current_player.colour_index]

        # Draw player label (with shadow) at the top
        _path_label_shadow = _path_label_font.render(_path_player_label, True, (100, 100, 100))
        screen.blit(_path_label_shadow, (rect.x + int(12 * scale), rect.y + int(12 * scale)))
        _path_label_surf = _path_label_font.render(_path_player_label, True, _path_label_colour)
        screen.blit(_path_label_surf, (rect.x + int(10 * scale), rect.y + int(10 * scale)))

        # Draw remaining spaces info
        spaces_text = font.render(f"Remaining Spaces: {remaining_spaces}", True, (100, 0, 0))
        screen.blit(spaces_text, (rect.x + int(10 * scale), rect.y + int(32 * scale)))

        labels = ["North", "West"]
        button_height = int(35 * scale)
        button_spacing = int(15 * scale)

        game_state['path_buttons'] = []

        for i, (label, choice) in enumerate(zip(labels, choices)):
            full_path = get_movement_path_with_choice(current_pos, choice, remaining_spaces, squares, next_positions)
            ending_pos = full_path[-1]
            end_square_type = squares[ending_pos]

            button = pygame.Rect(
                rect.x + int(20 * scale),
                rect.y + int(80 * scale) + i * (button_height + button_spacing),
                int(260 * scale),
                button_height
            )

            button_color = (200, 230, 255) if i == 0 else (255, 230, 200)

            if 'clicked_path_button' in game_state and game_state['clicked_path_button'] == i:
                current_time = time.time()
                click_elapsed = current_time - game_state['path_button_click_time']
                if click_elapsed < 0.3:
                    button_color = (180, 210, 235) if i == 0 else (235, 210, 180)
                else:
                    del game_state['clicked_path_button']
                    del game_state['path_button_click_time']

            pygame.draw.rect(screen, button_color, button)
            pygame.draw.rect(screen, (0, 0, 100), button, 2)

            direction_text = font.render(f"{label} Path", True, BLACK)
            screen.blit(direction_text, (button.x + int(10 * scale), button.y + int(5 * scale)))

            dest_text = font.render(f"Ends on: {end_square_type}", True, (100, 0, 0))
            screen.blit(dest_text, (button.x + int(130 * scale), button.y + int(5 * scale)))

            game_state['path_buttons'].append((button, choice))

    # Draw jail standee markers for players in jail
    # First, collect standee positions to handle staggering
    standee_positions = {}  # Tracks positions and counts players at each position

    # First pass - identify standee positions and group players
    for player in players:
        if player.jail_from_x is not None and player.jail_from_y is not None:
            # Find the original tile position
            square_x = int(player.jail_from_x * scale + offset_x)
            square_y = int(player.jail_from_y * scale + offset_y)
            
            tile_found = False
            for i, coord in enumerate(squares_coords):
                scaled_x = int(coord[0] * scale + offset_x)
                scaled_y = int(coord[1] * scale + offset_y)
                
                # If the player was on this tile
                if abs(scaled_x - square_x) < 10 and abs(scaled_y - square_y) < 10:
                    position_key = str(i)  # Use tile index as the key
                    if position_key in standee_positions:
                        standee_positions[position_key].append(player)
                    else:
                        standee_positions[position_key] = [player]
                    tile_found = True
                    break

    # Second pass - draw standees with proper staggering
    for position_key, players_at_position in standee_positions.items():
        tile_index = int(position_key)
        scaled_x = int(squares_coords[tile_index][0] * scale + offset_x)
        scaled_y = int(squares_coords[tile_index][1] * scale + offset_y)
        
        # Get the tile image to position markers correctly
        square_type = squares[tile_index]
        if square_type in tile_images_scaled:
            img = tile_images_scaled[square_type]
        elif square_type == '1':
            # Check if we're on the expert board
            if game_state.get('selected_board') == 'Expert':
                # First row (east direction) - indices 1-15
                if 1 <= tile_index <= 15:
                    img = tile_images_scaled['1_East']
                # Right column (south direction) - indices 16-22
                elif 16 <= tile_index <= 22:
                    img = tile_images_scaled['1_South']
                # Bottom rows going west - west path or south path west segments
                elif (23 <= tile_index <= 27) or (tile_index >= 29 and tile_index <= 37) or (tile_index >= 52 and tile_index <= 66):
                    img = tile_images_scaled['1_West']
                # Vertical segments going north - end of paths
                elif (tile_index >= 38 and tile_index <= 48) or (tile_index >= 67 and tile_index <= 77):
                    img = tile_images_scaled['1_North']
                # Default east direction for any other segments
                else:
                    img = tile_images_scaled['1_East']
            else:
                # Original classic board logic
                if tile_index in [1, 6]:
                    img = tile_images_scaled['1_East']
                elif tile_index in [12, 14]:
                    img = tile_images_scaled['1_North']
                elif tile_index == 24:
                    img = tile_images_scaled['1_West']
                elif tile_index == 31:
                    img = tile_images_scaled['1_West']
                else:
                    img = tile_images_scaled['1_East']
        elif square_type == '-2':
            # Check if we're on the expert board
            if game_state.get('selected_board') == 'Expert':
                # First row (east direction) - should point west (opposite)
                if 1 <= tile_index <= 15:
                    img = tile_images_scaled['-2_West']
                # Right column (south direction) - should point north (opposite)
                elif 16 <= tile_index <= 22:
                    img = tile_images_scaled['-2_North']
                # Bottom rows going west - should point east (opposite)
                elif (23 <= tile_index <= 27) or (tile_index >= 29 and tile_index <= 37) or (tile_index >= 52 and tile_index <= 66):
                    img = tile_images_scaled['-2_East']
                # Vertical segments going north - should point south (opposite)
                elif (tile_index >= 38 and tile_index <= 48) or (tile_index >= 67 and tile_index <= 77):
                    img = tile_images_scaled['-2_South']
                # Default west direction for any other segments (opposite of east)
                else:
                    img = tile_images_scaled['-2_West']
            else:
                # Original classic board logic
                if tile_index == 4:
                    img = tile_images_scaled['-2_West']
                elif tile_index in [13, 15]:
                    img = tile_images_scaled['-2_South']
                elif tile_index == 19:
                    img = tile_images_scaled['-2_East']
                elif tile_index in [28, 33, 35]:
                    img = tile_images_scaled['-2_North']
                else:
                    img = tile_images_scaled['-2_West']
        else:
            continue
        
        # Position at the top right of the tile
        offset_val = int(5 * scale)  # Small offset from edge
        tile_width = img.get_width()
        tile_height = img.get_height()
        
        # Draw each player's standee with staggering
        for i, player in enumerate(players_at_position):
            # Stagger the markers to prevent overlapping
            stagger_offset = i * int(8 * scale)
            marker_x = scaled_x + tile_width // 2 - offset_val
            marker_y = scaled_y - tile_height // 2 + offset_val + stagger_offset
            
            # Choose color based on if player is CPU or not
            if player.is_computer:
                marker_color = GRAY  # Grey for CPU players
            else:
                marker_color = player_colours[player.colour_index]  # Player's color for normal players
            
            # Get the current time for animation
            current_time = time.time()
            
            # Set base marker size - smaller for better visibility
            marker_radius = int(6 * scale)  # Smaller size to match regular markers
            
            # Apply animation effects if animation start time is set
            if player.jail_marker_anim_start:
                anim_duration = 0.25  # Animation duration in seconds
                elapsed = current_time - player.jail_marker_anim_start
                
                if elapsed < anim_duration:
                    # Grow from 0% to 100% size over 0.25 seconds
                    anim_progress = elapsed / anim_duration
                    # Ensure we start from a very small size and grow to full size
                    animated_radius = int(marker_radius * anim_progress)
                    # Different opacity based on color
                    if player.colour_index in [4, 5]:  # Blue and Purple
                        alpha = int(242 * anim_progress)  # 95% opacity for blue/purple
                    else:
                        alpha = int(200 * anim_progress)  # Original max opacity for others
                    
                    # Ensure the surface is large enough even for small circles
                    surface_size = max(2, marker_radius * 2)  # Use max marker size for surface
                    marker_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
                    
                    # Draw circle centered in the surface
                    center = surface_size // 2
                    pygame.draw.circle(marker_surface, marker_color + (alpha,), (center, center), animated_radius)
                    if animated_radius > 0:  # Only draw border if radius is positive
                        pygame.draw.circle(marker_surface, BLACK + (alpha,), (center, center), animated_radius, 1)
                    
                    # Blit the surface
                    screen.blit(marker_surface, (marker_x - center, marker_y - center))
                else:
                    # After animation completes, draw the circle normally
                    marker_surface = pygame.Surface((marker_radius * 2, marker_radius * 2), pygame.SRCALPHA)
                    # Different opacity based on color
                    if player.colour_index in [4, 5]:  # Blue and Purple
                        opacity = 242  # 95% opacity for blue/purple
                    else:
                        opacity = 128  # 50% opacity for others (original)
                    
                    pygame.draw.circle(marker_surface, marker_color + (opacity,), (marker_radius, marker_radius), marker_radius)
                    pygame.draw.circle(marker_surface, BLACK + (opacity,), (marker_radius, marker_radius), marker_radius, 1)
                    
                    # Blit the surface
                    screen.blit(marker_surface, (marker_x - marker_radius, marker_y - marker_radius))
            else:
                # Draw the regular circle if no animation
                marker_surface = pygame.Surface((marker_radius * 2, marker_radius * 2), pygame.SRCALPHA)
                # Different opacity based on color
                if player.colour_index in [4, 5]:  # Blue and Purple
                    opacity = 242  # 95% opacity for blue/purple
                else:
                    opacity = 128  # 50% opacity for others (original)
                
                pygame.draw.circle(marker_surface, marker_color + (opacity,), (marker_radius, marker_radius), marker_radius)
                pygame.draw.circle(marker_surface, BLACK + (opacity,), (marker_radius, marker_radius), marker_radius, 1)
                
                # Blit the surface
                screen.blit(marker_surface, (marker_x - marker_radius, marker_y - marker_radius))

    # Draw the Free Parking effect at the VERY END to ensure it's on top of everything
    if free_parking_x is not None and free_parking_y is not None and free_parking_img is not None and game_state.get('free_parking_effect', False):
        # Get the current animation progress
        current_time = time.time()
        elapsed = current_time - game_state['free_parking_start_time']
        duration = game_state['free_parking_duration']
        progress = elapsed / duration
        
        # Calculate pulsing effect (0.0 to 1.0 to 0.0)
        pulse = abs(math.sin(progress * math.pi * 4))  # Faster pulsing with 4 cycles
        
        # Create a larger surface for the glow effect
        glow_size = int(free_parking_img.get_width() * 2.5)  # Even bigger glow for better visibility
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        
        # Draw expanding circles with decreasing opacity
        for radius in range(5, int(glow_size/2), 4):
            # Yellow glow with higher opacity (increased from 150 to 220)
            opacity = int(250 * (1 - radius/(glow_size/2)) * pulse)
            if opacity > 0:
                pygame.draw.circle(glow_surface, (255, 255, 0, opacity), 
                                 (glow_size//2, glow_size//2), radius)
        
        # Draw the glow surface centered on the tile
        screen.blit(glow_surface, 
                   (free_parking_x - glow_surface.get_width()//2, 
                    free_parking_y - glow_surface.get_height()//2))
                    
        # Draw car icons orbiting around the Free Parking space (not the player)
        for j in range(4):
            angle = progress * 4 * math.pi + (j * math.pi / 2)  # Rotate around center
            radius = 32 * scale * (0.8 + 0.2 * pulse)  # Pulsing radius, slightly larger
            
            # Calculate position on the circle
            car_x = free_parking_x + radius * math.cos(angle)
            car_y = free_parking_y + radius * math.sin(angle)
            
            # Draw a car emoji (using a small yellow circle as placeholder)
            car_size = int(22 * scale * (0.8 + 0.2 * pulse))  # Increased size for better visibility
            car_surface = pygame.Surface((car_size, car_size), pygame.SRCALPHA)
            # Full opacity for maximum visibility
            pygame.draw.circle(car_surface, (255, 255, 0, 255), (car_size//2, car_size//2), car_size//2)
            
            # Draw black outline with full opacity
            pygame.draw.circle(car_surface, (0, 0, 0, 255), (car_size//2, car_size//2), car_size//2, 2)
            
            # Blit to the screen
            screen.blit(car_surface, (car_x - car_size//2, car_y - car_size//2))

    # Return the rects for interactive elements
    quiz_answer_rects = game_state.get('quiz_buttons', [])
    return dice_rect, restart_button_rect, achievement_button_rect, settings_button_rect, magnify_button_rect, quiz_answer_rects if game_state.get('quiz_buttons') else []


def select_players():
    """Let players choose who's human or CPU."""
    global SCREEN_WIDTH, SCREEN_HEIGHT, scale, offset_x, offset_y, screen, font
    
    # Load game progress to check if Expert board is unlocked
    game_progress = load_game_progress()
    
    player_states = [0, 0, 0, 0, 0, 0]
    difficulties = [None, None, None, None, None, None]
    selected_board = 0  # Default to the first board (Classic)
    
    # Check if player has completed at least one game
    has_completed_game = game_progress.get("classic_board_completed", False)
    
    # Only include boards that have been unlocked
    board_names = ["Classic"]
    if "Expert" in game_progress.get("unlocked_boards", ["Classic"]):
        board_names.append("Expert")
    if "Secret" in game_progress.get("unlocked_boards", ["Classic"]):
        board_names.append("Secret")
        
    # Flag to determine if we should show board selection
    show_board_selection = has_completed_game
    
    # Create a larger font for the title
    title_font = pygame.font.SysFont(None, int(72 * scale))
    
    not_set_image = pygame.image.load(load_asset("Assets/Images/Players/Player Not.png"))
    player_images_scaled = [pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale))) for img in player_images_original]
    
    # Scale CPU difficulty images
    cpu_difficulty_images_scaled = {
        key: pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale)))
        for key, img in cpu_difficulty_images_original.items()
    }
    
    # Default CPU image now just references normal difficulty
    cpu_image_scaled = cpu_difficulty_images_scaled['normal']
    
    not_set_image_scaled = pygame.transform.smoothscale(not_set_image, (int(80 * scale), int(80 * scale)))
    difficulty_images_scaled = {
        key: pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale)))
        for key, img in difficulty_images_original.items()
    }
    
    slot_rects = [pygame.Rect(int(100 * scale + offset_x + i * 100 * scale), int(150 * scale + offset_y), int(80 * scale), int(80 * scale)) for i in range(6)]
    
    # Add board selector buttons
    board_button_width = int(120 * scale)
    board_button_height = int(40 * scale)
    board_selector_rects = []
    for i in range(len(board_names)):
        x_pos = int((ORIGINAL_WIDTH * scale / 2) - (board_button_width * len(board_names) / 2) + (i * board_button_width) + offset_x)
        board_selector_rects.append(pygame.Rect(x_pos, int(350 * scale + offset_y), board_button_width, board_button_height))
    
    start_button_rect = pygame.Rect(int(300 * scale + offset_x), int(400 * scale + offset_y), int(200 * scale), int(50 * scale))
    gallery_button_rect = pygame.Rect(int((ORIGINAL_WIDTH - 160) * scale + offset_x), int((ORIGINAL_HEIGHT - 60) * scale + offset_y), int(150 * scale), int(50 * scale))
    
    show_achievements = False
    achievement_pane_rect = None

    while True:
        # No longer creating difficulty_rects since we're removing those buttons
        # but we still need to track which players are CPU for right-click handling
        cpu_players = [i for i, state in enumerate(player_states) if state == 2]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                scale_x = SCREEN_WIDTH / ORIGINAL_WIDTH
                scale_y = SCREEN_HEIGHT / ORIGINAL_HEIGHT
                scale = min(scale_x, scale_y)
                offset_x = (SCREEN_WIDTH - (ORIGINAL_WIDTH * scale)) / 2
                offset_y = (SCREEN_HEIGHT - (ORIGINAL_HEIGHT * scale)) / 2
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                font = pygame.font.SysFont(None, int(24 * scale))
                title_font = pygame.font.SysFont(None, int(72 * scale))
                player_images_scaled = [pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale))) for img in player_images_original]
                
                # Scale CPU difficulty images
                cpu_difficulty_images_scaled = {
                    key: pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale)))
                    for key, img in cpu_difficulty_images_original.items()
                }
                # Default CPU image for backwards compatibility with existing code
                cpu_image_scaled = cpu_difficulty_images_scaled['normal']
                
                not_set_image_scaled = pygame.transform.smoothscale(not_set_image, (int(80 * scale), int(80 * scale)))
                difficulty_images_scaled = {
                    key: pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale)))
                    for key, img in difficulty_images_original.items()
                }
                slot_rects = [pygame.Rect(int(100 * scale + offset_x + i * 100 * scale), int(150 * scale + offset_y), int(80 * scale), int(80 * scale)) for i in range(6)]
                
                # Recalculate board selector buttons
                board_button_width = int(120 * scale)
                board_button_height = int(40 * scale)
                board_selector_rects = []
                for i in range(len(board_names)):
                    x_pos = int((ORIGINAL_WIDTH * scale / 2) - (board_button_width * len(board_names) / 2) + (i * board_button_width) + offset_x)
                    board_selector_rects.append(pygame.Rect(x_pos, int(350 * scale + offset_y), board_button_width, board_button_height))
                    
                start_button_rect = pygame.Rect(int(300 * scale + offset_x), int(400 * scale + offset_y), int(200 * scale), int(50 * scale))
                gallery_button_rect = pygame.Rect(int((ORIGINAL_WIDTH - 160) * scale + offset_x), int((ORIGINAL_HEIGHT - 60) * scale + offset_y), int(150 * scale), int(50 * scale))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button == 1:  # Left click
                    # Check for board selection only if unlocked
                    if show_board_selection and len(board_names) > 1:
                        for i, rect in enumerate(board_selector_rects):
                            if rect.collidepoint(pos):
                                selected_board = i
                                audio.connect_sound.play()  # Play a sound when board is selected
                                break
                    # No longer checking for difficulty selection button clicks
                    # Check for player selection
                    for i, rect in enumerate(slot_rects):
                        if rect.collidepoint(pos):
                            toggle_player_state(i, player_states, difficulties)
                            break
                elif event.button == 3:  # Right click
                    # Check for player slots to cycle difficulty if it's a CPU
                    for i, rect in enumerate(slot_rects):
                        if rect.collidepoint(pos) and player_states[i] == 2:  # Right-clicked on a CPU player
                            cycle_difficulty(i, difficulties)
                            break
                            
                if gallery_button_rect.collidepoint(pos):
                    show_achievements = not show_achievements
                    audio.connect_sound.play()
                
                # Close achievements if clicking outside
                if show_achievements and achievement_pane_rect and not achievement_pane_rect.collidepoint(pos) and not gallery_button_rect.collidepoint(pos):
                    show_achievements = False
                    
                if start_button_rect.collidepoint(pos) and any(state > 0 for state in player_states):
                    selected_players = []
                    for i, state in enumerate(player_states):
                        if state == 1:
                            selected_players.append((i, False, None))
                        elif state == 2:
                            selected_players.append((i, True, difficulties[i]))
                    audio.super_mario_sound.play()
                    return selected_players, board_names[selected_board]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_achievements:
                        show_achievements = False
                    else:
                        pass
                elif event.key >= pygame.K_1 and event.key <= pygame.K_6:
                    index = event.key - pygame.K_1
                    if index < len(player_states):
                        toggle_player_state(index, player_states, difficulties)
                # Board selection with arrow keys (only if unlocked)
                elif event.key == pygame.K_LEFT and show_board_selection and len(board_names) > 1:
                    selected_board = max(0, selected_board - 1)  # Move left, with minimum 0
                    audio.connect_sound.play()
                elif event.key == pygame.K_RIGHT and show_board_selection and len(board_names) > 1:
                    selected_board = min(len(board_names) - 1, selected_board + 1)  # Move right, with maximum at last board
                    audio.connect_sound.play()
                elif event.key == pygame.K_SPACE and any(state > 0 for state in player_states):
                    # Space bar acts like clicking the start button, but only when it's active
                    selected_players = []
                    for i, state in enumerate(player_states):
                        if state == 1:
                            selected_players.append((i, False, None))
                        elif state == 2:
                            selected_players.append((i, True, difficulties[i]))
                    audio.super_mario_sound.play()
                    return selected_players, board_names[selected_board]

        screen.fill(GRAY)
        
        # Draw the Rock-Sickle title at the top of the screen
        title_text = title_font.render("Rock-Sickle", True, BLACK)
        title_shadow = title_font.render("Rock-Sickle", True, DARK_GREY)
        # Draw shadow slightly offset for a 3D effect
        screen.blit(title_shadow, (int((ORIGINAL_WIDTH * scale / 2) - (title_text.get_width() / 2) + offset_x + 3), int(50 * scale + offset_y + 3)))
        screen.blit(title_text, (int((ORIGINAL_WIDTH * scale / 2) - (title_text.get_width() / 2) + offset_x), int(50 * scale + offset_y)))
        
        for i, (rect, state) in enumerate(zip(slot_rects, player_states)):
            if state == 0:
                screen.blit(not_set_image_scaled, rect.topleft)
            elif state == 1:
                screen.blit(player_images_scaled[i], rect.topleft)
            elif state == 2:
                # Use the correct CPU image based on difficulty
                if difficulties[i] in cpu_difficulty_images_scaled:
                    screen.blit(cpu_difficulty_images_scaled[difficulties[i]], rect.topleft)
                else:
                    # Fallback to normal if difficulty is not recognized
                    screen.blit(cpu_difficulty_images_scaled['normal'], rect.topleft)
                
                # No longer display the difficulty indicator below CPU players
            
            label = font.render(f"P{i+1}", True, player_colours[i])
            screen.blit(label, (rect.centerx - label.get_width() // 2, rect.top - int(20 * scale)))
            
        # Only draw board selector if player has completed at least one game
        if show_board_selection and len(board_names) > 1:
            board_selector_text = font.render("Select Board:", True, BLACK)
            screen.blit(board_selector_text, (int(ORIGINAL_WIDTH * scale / 2 - board_selector_text.get_width() / 2 + offset_x), int(320 * scale + offset_y)))
            
            for i, rect in enumerate(board_selector_rects):
                # Use a different color for the selected board
                button_color = GREEN if i == selected_board else DARK_GREY
                pygame.draw.rect(screen, button_color, rect)
                # Use black text for selected button, white for unselected buttons
                text_color = BLACK if i == selected_board else WHITE
                text = font.render(board_names[i], True, text_color)
                screen.blit(text, text.get_rect(center=rect.center))
                
        # Draw Gallery Button
        pygame.draw.rect(screen, DARK_GREY, gallery_button_rect, border_radius=int(5 * scale))
        gallery_text = font.render("Gallery", True, GOLD)
        screen.blit(gallery_text, gallery_text.get_rect(center=gallery_button_rect.center))

        # Create a desaturated button with 50% opacity when inactive
        if any(state > 0 for state in player_states):
            pygame.draw.rect(screen, GREEN, start_button_rect)
        else:
            # Create a transparent surface for the inactive button
            button_surface = pygame.Surface((start_button_rect.width, start_button_rect.height), pygame.SRCALPHA)
            # Get grayscale (0% saturation) value of GREEN by using its brightness/luminance
            # For simplicity, average the RGB values for grayscale
            r, g, b = GREEN
            gray_value = (r + g + b) // 3
            # Fill with desaturated green at 50% opacity (128 alpha)
            button_surface.fill((gray_value, gray_value, gray_value, 128))
            screen.blit(button_surface, start_button_rect)
        if any(state > 0 for state in player_states):
            # Render text normally for active button
            text = font.render("Start Game", True, BLACK)
            screen.blit(text, text.get_rect(center=start_button_rect.center))
        else:
            # Create a transparent surface for the text
            text = font.render("Start Game", True, BLACK)
            text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
            text_surface.blit(text, (0, 0))
            # Apply 50% opacity to the text
            text_surface.set_alpha(128)
            screen.blit(text_surface, text.get_rect(center=start_button_rect.center))

        # Draw Achievements Pane if active
        if show_achievements:
            achievement_pane_rect = render_achievements_pane(screen, scale, offset_x, offset_y, board_names[selected_board])

        pygame.display.flip()

def resize_assets(scale, board_type='Classic'):
    """Resize all game assets based on screen scale while maintaining aspect ratios where necessary."""
    global player_images_scaled, cpu_image_scaled, bonus_result_images_scaled, cpu_difficulty_images_scaled
    global dice_images_scaled, tile_images_scaled, restart_button_scaled
    global bonus_images_scaled, settings_button_scaled, achievement_button_scaled, board_image_scaled, magnify_button_scaled
    global cover_bonus_scaled, cover_quiz_scaled
    
    # Calculate slightly smaller tile size to account for the gaps
    # Different boards use different tile sizes
    if board_type == 'Expert':
        tile_size = int(40 * scale) - int(GAP_BETWEEN_TILES * scale * 0.3)  # Smaller for expert board
    elif board_type == 'Secret':
        tile_size = int(16 * scale)  # Match the fixed spacing in get_secret_squares_coords
    else:
        tile_size = int(60 * scale) - int(GAP_BETWEEN_TILES * scale * 0.3)  # Regular size for classic board
    
    # Select the appropriate image set based on board type
    tile_images_set = board_tile_images[board_type]
    button_set = board_buttons[board_type]
    
    # Scale the selected tile images
    tile_images_scaled = {
        key: pygame.transform.smoothscale(img, (tile_size, tile_size))
        for key, img in tile_images_set.items() if key not in ['F', 'Jail']
    }
    
    # Expert board has a different finish image orientation than classic
    if board_type == 'Classic':
        finish_rotated = pygame.transform.rotate(tile_images_set['F'], 90)
        finish_height = int(120 * scale) - int(GAP_BETWEEN_TILES * scale * 0.3)  # Increased from 100 to 120
    elif board_type == 'Secret':
        finish_rotated = tile_images_set['F']  # Use the same orientation as Expert
        finish_height = tile_size  # Make it square like the Secret board tiles
    else:  # Expert board
        finish_rotated = tile_images_set['F']  # Expert finish doesn't need rotation
        finish_height = tile_size  # Make it square like other tiles for expert board
    
    tile_images_scaled['F'] = pygame.transform.smoothscale(finish_rotated, (tile_size, finish_height))
    
    # Adjust jail size based on board type
    if board_type == 'Expert':
        jail_size = int(tile_size * 4.1)  # Increased size from 3.7 to 4.1 to make it larger
    elif board_type == 'Secret':
        jail_size = int(tile_size * 2.0)  # Proportional size for Secret board
    else:
        jail_size = int(tile_size * 1.5)  # Regular jail size for classic
        
    tile_images_scaled['Jail'] = pygame.transform.smoothscale(tile_images_set['Jail'], (jail_size, jail_size))
    
    # Make player tokens smaller on expert board due to smaller tiles
    player_size = int(50 * scale)
    if board_type == 'Expert':
        player_size = int(35 * scale)  # Smaller for expert board
    elif board_type == 'Secret':
        player_size = int(14 * scale)  # Much smaller for the 1000-space secret board
        
    player_images_scaled = [pygame.transform.smoothscale(img, (player_size, player_size)) for img in player_images_original]
    for img in player_images_scaled:
        img.set_alpha(191)
    
    # Scale CPU difficulty images
    cpu_difficulty_images_scaled = {
        key: pygame.transform.smoothscale(img, (player_size, player_size))
        for key, img in cpu_difficulty_images_original.items()
    }
    # Set alpha for all CPU difficulty images
    for img in cpu_difficulty_images_scaled.values():
        img.set_alpha(191)
    
    # Default CPU image for backwards compatibility
    cpu_image_scaled = cpu_difficulty_images_scaled['normal']
    
    # Make dice slightly larger
    dice_images_scaled = [pygame.transform.smoothscale(img, (int(55 * scale), int(55 * scale))) for img in dice_images_original]  # Increased from 50 to 55
    
    # Use the appropriate button images based on board type
    restart_button_scaled = pygame.transform.smoothscale(button_set['restart'], (int(55 * scale), int(55 * scale)))  # Increased from 50 to 55
    settings_button_scaled = pygame.transform.smoothscale(button_set['settings'], (int(55 * scale), int(55 * scale)))  # Increased from 50 to 55
    achievement_button_scaled = pygame.transform.smoothscale(button_set['achievement'], (int(55 * scale), int(55 * scale)))
    
    # Load and scale the magnify button (magnifying glass icon)
    magnify_button_original = load_and_convert("Assets/Images/Tiles/Magnifying Glass.png")
    if board_type == 'Expert':
        magnify_button_original = load_and_convert("Assets/Images/Tiles/eMagnifying Glass.png")
    magnify_button_scaled = pygame.transform.smoothscale(magnify_button_original, (int(55 * scale), int(55 * scale)))

    
    # Scale bonus images with a slightly larger size
    target_width = int(280 * scale)  # Increased from 250 to 280
    target_height = int(target_width * 3 / 4)  # Height preserves 4:3 ratio
    bonus_result_images_scaled = {
        key: pygame.transform.smoothscale(img, (target_width, target_height))
        for key, img in bonus_result_images_original.items()
    }
    
    # Scale card covers
    cover_bonus_scaled = pygame.transform.smoothscale(cover_bonus_original, (target_width, target_height))
    cover_quiz_scaled = pygame.transform.smoothscale(cover_quiz_original, (target_width, target_height))
    
    return tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, achievement_button_scaled, bonus_result_images_scaled, magnify_button_scaled

def main():
    """Main game loop and initialization."""
    global SCREEN_WIDTH, SCREEN_HEIGHT, scale, offset_x, offset_y, screen, font
    scale = 1.0
    offset_x = 0
    offset_y = 0
    audio.connect_sound.play()
    
    # Create a list of all sounds in the game for easy volume control
    all_game_sounds = [
        # Regular sounds
        audio.roll_sound, audio.glug_sound, audio.bonk_sound, audio.head_shake_sound, audio.whiz_sound, audio.drip_drop_sound, 
        audio.drum_machine_sound, audio.win_sound, audio.pop_sound, audio.bing_bong_sound, audio.connect_sound, 
        audio.disconnect_sound, audio.indigogo_sound, audio.jump_sound, audio.mac_os_dinbg_sound, audio.mac_os_uh_ohh_sound, 
        audio.super_mario_sound, audio.wobble_sound, audio.fairlin_round1_sound, audio.pong_sound, audio.voltage_easy_sound, 
        audio.voltage_normal_sound, audio.voltage_hard_sound, audio.whit_sound, audio.restart_sound, audio.car_horn_sound,
        # CPU-specific sounds
        audio.bonk_cpu_sound, audio.glug_cpu_sound, audio.head_shake_cpu_sound, audio.jump_cpu_sound, audio.whiz_cpu_sound, audio.wobble_cpu_sound
    ]
    
    # Function to apply master volume to all sounds
        
    # Set default volume for all sounds (will be overridden by settings)
    default_volume = 1.0
    audio.apply_master_volume(default_volume)

    quit_game = False
    while not quit_game:
        selected_data = select_players()
        if selected_data is None:
            break

        selected_players, selected_board = selected_data
        logger.info(f"Selected board type: {selected_board}")
        
        # Load saved game progress and settings
        saved_progress = load_game_progress()
        
        players = [Player(i, colour_idx, is_computer, difficulty, start_coords=squares_coords[0]) for i, (colour_idx, is_computer, difficulty) in enumerate(selected_players)]
        for player in players:
            player.position_history.append(player.position)
            
        # Initialize the game start time
        game_start_time = time.time()
        
        # Set start time for all players
        for player in players:
            player.start_time = game_start_time
        
        # Initialize default game state
        game_state = {
            'current_player': 0,
            'message': "",
            'show_quiz': False,
            'rolling_dice': False,
            'dice_start_time': 0,
            'dice_roll': 0,
            'final_dice_roll': 1,
            'pop_played': False,
            'quiz_state': None,
            'finish_order': [],
            'players': players,
            'last_scale': scale,
            'restart_hold_start': None,
            'restart_ready': False,
         
            'selected_board': selected_board,  # Store the selected board
            'game_start_time': time.time(),  # Add a timestamp for when the game started
            'game_start_buffer': 1.0,  # Add a buffer period (in seconds) after game start
            'show_settings_menu': False,  # Settings menu state
            'last_bonus_position': {},  # Track the last position where each player picked up a bonus card
            'volume_drag_active': False,  # Flag to track if volume slider is being dragged
            'show_achievements_menu': False,  # Achievements menu state
            'camera_mode': 0, # 0: Default, 1: All Players, 2: Current Player
            'camera_zoom': 1.0,
            'camera_focus_x': 400.0,
            'camera_focus_y': 300.0,
            'camera_target_zoom': 1.0,
            'camera_target_focus_x': 400.0,
            'camera_target_focus_y': 300.0,
        }
        
        # For Secret board, set custom die position to avoid overlapping with tiles
        if selected_board == 'Secret':
            game_state['die_pos'] = (700, 150)  # Place die in top-right area
        
        # Set the correct board squares based on the selected board
        global squares, next_positions, squares_coords, JAIL_POS
        squares, next_positions = get_board_squares(selected_board)
        
        # Set the correct board coordinates
        if selected_board == 'Expert':
            squares_coords = get_expert_squares_coords()
            JAIL_POS = EXPERT_JAIL_POS
        elif selected_board == 'Secret':
            squares_coords = get_secret_squares_coords()
            JAIL_POS = SECRET_JAIL_POS
        else:
            squares_coords = get_classic_squares_coords()
            JAIL_POS = CLASSIC_JAIL_POS
        
        # Apply saved settings if they exist, otherwise use defaults
        if 'settings' in saved_progress:
            # Load volume setting
            game_state['master_volume'] = saved_progress['settings'].get('master_volume', 1.0)
            
            # Load show_game_status setting (false by default as requested)
            game_state['show_game_status'] = saved_progress['settings'].get('show_game_status', False)
            
            # Load modern status display setting (true by default as requested)
            game_state['use_modern_status_display'] = saved_progress['settings'].get('use_modern_status_display', True)
            
            # Load show_timers setting (false by default as requested)
            game_state['show_timers'] = saved_progress['settings'].get('show_timers', False)
        else:
            # Set defaults as requested
            game_state['master_volume'] = 1.0  # 100% volume
            game_state['show_game_status'] = False  # Game status off
            game_state['use_modern_status_display'] = True  # Modern status display on
            game_state['show_timers'] = False  # Show timers off by default
        
        # Apply the volume setting
        audio.apply_master_volume(game_state['master_volume'])
        clock = pygame.time.Clock()

        tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, achievement_button_scaled, bonus_result_images_scaled, magnify_button_scaled = resize_assets(scale, selected_board)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Save current settings before closing
                    saved_progress = load_game_progress()
                    
                    # Update settings in the progress data
                    if 'settings' not in saved_progress:
                        saved_progress['settings'] = {}
                    
                    # Save current settings
                    saved_progress['settings']['master_volume'] = game_state.get('master_volume', 1.0)
                    saved_progress['settings']['show_game_status'] = game_state.get('show_game_status', False)
                    saved_progress['settings']['use_modern_status_display'] = game_state.get('use_modern_status_display', True)
                    saved_progress['settings']['show_timers'] = game_state.get('show_timers', False)
                    
                    # Save to file
                    save_game_progress(saved_progress)
                    
                    running = False
                    quit_game = True
                elif event.type == pygame.VIDEORESIZE:
                    SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                    scale_x = SCREEN_WIDTH / ORIGINAL_WIDTH
                    scale_y = SCREEN_HEIGHT / ORIGINAL_HEIGHT
                    scale = min(scale_x, scale_y)
                    offset_x = (SCREEN_WIDTH - (ORIGINAL_WIDTH * scale)) / 2
                    offset_y = (SCREEN_HEIGHT - (ORIGINAL_HEIGHT * scale)) / 2
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                    font = pygame.font.SysFont(None, int(24 * scale))
                    title_font = pygame.font.SysFont(None, int(72 * scale))
                    # Use resize_assets to properly resize all game assets
                    tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, achievement_button_scaled, bonus_result_images_scaled, magnify_button_scaled = resize_assets(scale, game_state['selected_board'])
                    game_state['last_scale'] = scale
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        current_player = players[game_state['current_player']]
                        # Check if we're within the game start buffer period
                        if time.time() - game_state.get('game_start_time', 0) < game_state.get('game_start_buffer', 0):
                            # During buffer period, do nothing when space is pressed
                            pass
                        elif not current_player.is_computer and not game_state.get('show_quiz', False) and \
                           not game_state.get('show_path_choice_after_roll', False) and \
                           not game_state.get('rolling_dice', False) and not current_player.has_rolled and \
                           not game_state.get('bonus_image_state') and not animations_active:
                            message, moved = move_player(current_player, game_state)
                            game_state['message'] = message
                    # Add support for number keys to answer quiz questions
                    elif game_state.get('show_quiz', False) and game_state.get('quiz_state') == 'buttons' and 'quiz_buttons' in game_state:
                        current_player = players[game_state['current_player']]
                        if not current_player.is_computer:  # Only respond to key presses for human players
                            # Check for number keys 1-9
                            if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                                option_index = event.key - pygame.K_1  # Convert to 0-based index (1 key = index 0)
                                
                                # Make sure the option exists
                                if option_index < len(game_state['quiz_buttons']):
                                    # Add splash effect tracking
                                    game_state['clicked_quiz_button'] = option_index
                                    game_state['button_click_time'] = time.time()
                                    
                                    # Check if the answer is correct
                                    _, _, correct = game_state['quiz_question']
                                    if option_index == correct:
                                        apply_quiz_effect(current_player, True, game_state, scale)
                                    else:
                                        apply_quiz_effect(current_player, False, game_state, scale)
                    elif event.key == pygame.K_ESCAPE:
                        if game_state.get('show_achievements_menu', False):
                            game_state['show_achievements_menu'] = False
                        elif game_state.get('show_settings_menu', False):
                            game_state['show_settings_menu'] = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    button_size = int(50 * scale)
                    restart_button_rect = pygame.Rect(int(610 * scale + offset_x), int(540 * scale + offset_y), button_size, button_size)
                    if restart_button_rect.collidepoint(pos):
                        game_state['restart_hold_start'] = time.time()
                    
                    # Handle achievement button click
                    achievement_button_rect = pygame.Rect(int(670 * scale + offset_x), int(540 * scale + offset_y), button_size, button_size)
                    if achievement_button_rect.collidepoint(pos):
                        # Toggle achievements menu
                        game_state['show_achievements_menu'] = not game_state.get('show_achievements_menu', False)
                        audio.connect_sound.play()
                        # Close settings if opening achievements
                        if game_state['show_achievements_menu']:
                            game_state['show_settings_menu'] = False
                    
                    # Close achievements if clicking outside
                    if game_state.get('show_achievements_menu', False):
                        # We'll calculate the pane rect later in rendering, but we can estimate it here 
                        # or just rely on the click handling below
                        pass
                    
                    # Handle settings button click
                    settings_button_rect = pygame.Rect(int(730 * scale + offset_x), int(540 * scale + offset_y), button_size, button_size)
                    if settings_button_rect.collidepoint(pos):
                        # Toggle settings menu
                        game_state['show_settings_menu'] = not game_state.get('show_settings_menu', False)
                    
                    # Handle magnify button click
                    if 'magnify_button_rect' in locals() or 'magnify_button_rect' in globals(): # Ensure it exists if we missed it
                        pass
                    
                    # Wait, magnify_button_rect is returned by draw_board at the end of the loop, but we need it for collision.
                    # I'll calculate it here just like settings_button_rect.
                    magnify_button_rect = pygame.Rect(int(790 * scale + offset_x), int(540 * scale + offset_y), button_size, button_size)
                    if magnify_button_rect.collidepoint(pos):
                        # Cycle camera mode: 0 -> 1 -> 2 -> 0
                        game_state['camera_mode'] = (game_state.get('camera_mode', 0) + 1) % 3
                        audio.connect_sound.play()
                        # Close other menus
                        game_state['show_settings_menu'] = False
                        game_state['show_achievements_menu'] = False

                    
                    # Handle settings menu interactions if menu is open
                    if game_state.get('show_settings_menu', False):
                        # Define menu area
                        menu_width = int(200 * scale)
                        menu_height = int(220 * scale)  # Updated to match the new menu height
                        menu_x = settings_button_rect.x + (settings_button_rect.width // 2) - (menu_width // 2)
                        menu_y = settings_button_rect.y - menu_height - int(10 * scale)  # Position menu above button with 10px gap
                        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
                        
                        # Toggle game status display
                        if 'status_toggle_rect' in game_state and game_state['status_toggle_rect'].collidepoint(pos):
                            game_state['show_game_status'] = not game_state.get('show_game_status', True)
                        
                        # Toggle status display (renamed from modern/classic toggle)
                        if 'style_toggle_rect' in game_state and game_state['style_toggle_rect'].collidepoint(pos):
                            game_state['use_modern_status_display'] = not game_state.get('use_modern_status_display', False)
                        
                        # Toggle timer display
                        if 'timer_toggle_rect' in game_state and game_state['timer_toggle_rect'].collidepoint(pos):
                            game_state['show_timers'] = not game_state.get('show_timers', False)
                            audio.connect_sound.play()
                        
                        # Handle volume slider
                        if 'volume_slider_rect' in game_state and game_state['volume_slider_rect'].collidepoint(pos):
                            game_state['volume_drag_active'] = True
                            # Update volume based on click position
                            slider_rect = game_state['volume_slider_rect']
                            slider_width = game_state['volume_slider_width']
                            relative_x = max(0, min(pos[0] - slider_rect.x, slider_width))
                            volume = relative_x / slider_width
                            game_state['master_volume'] = volume
                            
                            # Apply volume to all sound channels
                            audio.apply_master_volume(volume)
                        
                        # Handle Reset to Default button
                        if 'reset_button_rect' in game_state and game_state['reset_button_rect'].collidepoint(pos):
                            # Reset all settings to default values
                            game_state['master_volume'] = 1.0  # 100% volume
                            game_state['show_game_status'] = False  # Game status off
                            game_state['use_modern_status_display'] = True  # Modern status display on
                            game_state['show_timers'] = False  # Show timers off by default
                            
                            # Apply the volume setting
                            audio.apply_master_volume(game_state['master_volume'])
                            
                            # Play a sound to indicate reset
                            audio.restart_sound.play()
                                
                        # Close menu if clicking outside of menu and settings button
                        if not menu_rect.collidepoint(pos) and not settings_button_rect.collidepoint(pos):
                            game_state['show_settings_menu'] = False
                            game_state['volume_drag_active'] = False
                            
                    # Handle click outside achievements menu to close it
                    if game_state.get('show_achievements_menu', False):
                        pane_width = int(600 * scale)
                        pane_height = int(450 * scale)
                        pane_x = int((screen.get_width() // 2) - (pane_width // 2))
                        pane_y = int((screen.get_height() // 2) - (pane_height // 2))
                        pane_rect = pygame.Rect(pane_x, pane_y, pane_width, pane_height)
                        if not pane_rect.collidepoint(pos) and not achievement_button_rect.collidepoint(pos):
                            game_state['show_achievements_menu'] = False
                    
                    dice_rect = pygame.Rect(int(DIE_POS[0] * scale + offset_x), int(DIE_POS[1] * scale + offset_y), int(50 * scale), int(50 * scale))
                    current_player = players[game_state['current_player']]
                    if not current_player.is_computer and dice_rect.collidepoint(pos) and not game_state.get('show_quiz', False) and \
                           not game_state.get('show_path_choice_after_roll', False) and not game_state.get('rolling_dice', False) and \
                           not current_player.has_rolled and not game_state.get('bonus_image_state') and not animations_active:
                        # Check if we're within the game start buffer period
                        if time.time() - game_state.get('game_start_time', 0) >= game_state.get('game_start_buffer', 0):
                            message, moved = move_player(current_player, game_state)
                            game_state['message'] = message
                    if game_state.get('show_quiz', False) and 'quiz_buttons' in game_state:
                        for button, option_index in game_state['quiz_buttons']:
                            if button.collidepoint(pos):
                                # Add splash effect tracking
                                game_state['clicked_quiz_button'] = option_index
                                game_state['button_click_time'] = time.time()
                                
                                _, _, correct = game_state['quiz_question']
                                if option_index == correct:
                                    apply_quiz_effect(current_player, True, game_state, scale)
                                else:
                                    apply_quiz_effect(current_player, False, game_state, scale)
                    if game_state.get('show_path_choice_after_roll', False) and 'path_buttons' in game_state:
                        for button, choice in game_state['path_buttons']:
                            if button.collidepoint(pos):
                                # Add splash effect tracking for path buttons
                                game_state['clicked_path_button'] = game_state['path_buttons'].index((button, choice))
                                game_state['path_button_click_time'] = time.time()
                                
                                current_player.path_choices[current_player.position] = choice
                                remaining_spaces = game_state.get('spaces_remaining', 0)
                                # Check if the player started their turn on the choice point
                                started_on_choice = isinstance(next_positions[current_player.position], list)
                                movement_path = get_movement_path_with_choice(current_player.position, choice, remaining_spaces, squares, next_positions, started_on_choice)
                                anim = {
                                    'player': current_player,
                                    'path': movement_path,
                                    'index': 0,
                                    'last_time': time.time(),
                                    'message': f"Player {current_player.id + 1} chose path to {choice}. Moving {remaining_spaces if started_on_choice else remaining_spaces - 1} more spaces.",
                                    'is_initial_move': True,
                                    'delay': 0.5
                                }
                                current_player.active_animations.append(anim)
                                audio.indigogo_sound.play()
                                game_state['show_path_choice_after_roll'] = False
                                del game_state['path_buttons']
                                if 'roll_for_path_choice' in game_state:
                                    del game_state['roll_for_path_choice']
                                if 'spaces_remaining' in game_state:
                                    del game_state['spaces_remaining']
                                current_player.has_rolled = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if game_state.get('restart_hold_start') is not None and game_state['restart_ready']:
                        game_state['fade_start'] = time.time()
                        audio.restart_sound.play()
                    game_state['restart_hold_start'] = None
                    game_state['restart_ready'] = False
                    
                    # Stop volume slider dragging when mouse button is released
                    game_state['volume_drag_active'] = False
                
                elif event.type == pygame.MOUSEMOTION:
                    # Handle volume slider dragging
                    if game_state.get('volume_drag_active', False) and 'volume_slider_rect' in game_state:
                        pos = event.pos
                        slider_rect = game_state['volume_slider_rect']
                        slider_width = game_state['volume_slider_width']
                        # Calculate volume based on mouse position relative to slider
                        relative_x = max(0, min(pos[0] - slider_rect.x, slider_width))
                        volume = relative_x / slider_width
                        game_state['master_volume'] = volume
                        
                        # Apply volume to all sound channels
                        audio.apply_master_volume(volume)

            # Update camera targets based on current state
            update_camera_targets(game_state, players)
            
            animations_active = update_animation(game_state, scale)


            if game_state.get('restart_hold_start') is not None:
                hold_time = time.time() - game_state['restart_hold_start']
                if hold_time >= 1.5:
                    game_state['restart_ready'] = True

            if 'fade_start' in game_state:
                fade_time = time.time() - game_state['fade_start']
                if fade_time >= 1.0:
                    running = False

            if 'bonus_image_state' in game_state:
                current_time = time.time()
                if game_state['bonus_image_state'] == 'waiting':
                    if current_time - game_state['bonus_image_start'] >= 0.1:  # Reduced from 0.8s to 0.1s to sync with sound
                        game_state['bonus_image_state'] = 'growing'
                        game_state['bonus_grow_start'] = current_time
                        game_state['bonus_flipped'] = False
                elif game_state['bonus_image_state'] == 'growing':
                    elapsed = current_time - game_state['bonus_grow_start']
                    if elapsed >= 1.0:
                        game_state['bonus_image_state'] = 'flipping'
                        game_state['bonus_flip_start'] = current_time
                        game_state['bonus_flipped'] = False
                elif game_state['bonus_image_state'] == 'flipping':
                    elapsed = current_time - game_state['bonus_flip_start']
                    if elapsed >= 0.5:
                        game_state['bonus_image_state'] = 'showing'
                        # Start the bonus action
                        player = players[game_state['current_player']]
                        effect = game_state['bonus_action']
                        
                        # Add a 2-second timer for bonus card to close after action is started
                        game_state['bonus_action_start_time'] = current_time
                        
                        if effect[0] == "move_forward":
                            num = effect[1]
                            movement_path = get_movement_path(player.position, num, game_state, squares, next_positions)
                            anim = {
                                'player': player,
                                'path': movement_path,
                                'index': 0,
                                'last_time': time.time(),
                                'message': f"Player {player.id + 1} moving forward {num} spaces from bonus card.",
                                'is_initial_move': False,
                                'delay': 0.8
                            }
                            player.active_animations.append(anim)
                        elif effect[0] == "move_back":
                            num = effect[1]
                            if player.position > 0:
                                target_pos = max(0, player.position - num)
                                movement_path = [player.position]
                                if player.position >= num:
                                    for i in range(1, num + 1):
                                        movement_path.append(player.position - i)
                                else:
                                    for i in range(1, player.position + 1):
                                        movement_path.append(player.position - i)
                                
                                anim = {
                                    'player': player,
                                    'path': movement_path,
                                    'index': 0,
                                    'last_time': time.time(),
                                    'message': f"Player {player.id + 1} moving back {num} spaces from bonus card.",
                                    'is_backwards': True,
                                    'delay': 0.8
                                }
                                player.active_animations.append(anim)
                            else:
                                game_state['message'] = f"Player {player.id + 1} can't move back from the start."
                        elif effect[0] == "go_to_jail":
                            player.prev_position = player.position
                            player.jail_from_x = player.current_x
                            player.jail_from_y = player.current_y
                            player.jail_marker_anim_start = time.time()
                            
                            jail_offset_x = random.randint(-int(JAIL_SIZE/3), int(JAIL_SIZE/3))
                            jail_offset_y = random.randint(-int(JAIL_SIZE/3), int(JAIL_SIZE/3))
                            random_jail_pos = (JAIL_POS[0] + jail_offset_x, JAIL_POS[1] + jail_offset_y)
                            
                            audio.whiz_sound.play()
                            anim = {
                                'player': player,
                                'start_pos': (player.current_x, player.current_y),
                                'end_pos': random_jail_pos,
                                'steps': 60,
                                'current_step': 0,
                                'last_time': time.time(),
                                'message': "Moving to jail.",
                                'is_jail_move': True,
                                'delay': 0.0167,
                                'jail_action': 'enter'
                            }
                            player.active_animations.append(anim)
                        elif effect[0] == "jail_free":
                            player.has_jail_free_card = True
                            game_state['message'] = f"Player {player.id + 1} got a Get Out of Jail Free card!"
                        elif effect[0] == "pick_quiz":
                            game_state['pending_quiz'] = True
                elif game_state['bonus_image_state'] == 'showing':
                    player = players[game_state['current_player']]
                    
                    if 'bonus_action_start_time' in game_state and current_time - game_state['bonus_action_start_time'] >= 2.0:
                        if (not player.active_animations or 
                            (game_state['bonus_action'][0] == "pick_quiz" and not game_state.get('show_quiz', False))):
                            game_state['bonus_image_state'] = 'flipping_back'
                            game_state['bonus_flip_back_start'] = current_time
                            game_state['bonus_flipped'] = False
                            if 'bonus_shrink_delay' in game_state:
                                del game_state['bonus_shrink_delay']
                    elif not player.active_animations and not game_state.get('show_quiz', False):
                        if 'bonus_shrink_delay' not in game_state:
                            if game_state['bonus_action'][0] == "pick_quiz":
                                if game_state.get('quiz_from_bonus_completed', False):
                                    game_state['bonus_shrink_delay'] = current_time + 0.5
                                    del game_state['quiz_from_bonus_completed']
                            else:
                                game_state['bonus_shrink_delay'] = current_time + 2.0
                        elif current_time >= game_state['bonus_shrink_delay']:
                            game_state['bonus_image_state'] = 'flipping_back'
                            game_state['bonus_flip_back_start'] = current_time
                            game_state['bonus_flipped'] = False
                            del game_state['bonus_shrink_delay']
                elif game_state['bonus_image_state'] == 'flipping_back':
                    elapsed = current_time - game_state['bonus_flip_back_start']
                    if elapsed >= 0.5:
                        game_state['bonus_image_state'] = 'shrinking'
                        game_state['bonus_shrink_start'] = current_time
                        audio.disconnect_sound.play()
                elif game_state['bonus_image_state'] == 'shrinking':
                    elapsed = current_time - game_state['bonus_shrink_start']
                    if elapsed >= 1.0:
                        del game_state['bonus_image_key']
                        del game_state['bonus_image_state']
                        del game_state['bonus_action']
                        
                        # Check if there's a pending quiz from a bonus card
                        if game_state.get('pending_quiz', False):
                            # Determine which quiz deck to use based on the board type
                            if game_state.get('selected_board') == "Expert" and cards.expert_quiz_card_index < len(cards.expert_quiz_cards):
                                # Use expert quiz cards on the expert board
                                question, options, correct = cards.expert_quiz_cards[cards.expert_quiz_card_index]
                                game_state['quiz_question'] = (question, options, correct)
                                game_state['show_quiz'] = True
                                game_state['quiz_state'] = 'growing'
                                game_state['quiz_start_time'] = time.time()
                                game_state['pop_played'] = False
                                audio.drum_machine_sound.play()
                                cards.expert_quiz_card_index = (cards.expert_quiz_card_index + 1) % len(cards.expert_quiz_cards)
                                game_state['message'] = f"Player {players[game_state['current_player']].id + 1} faces an expert quiz."
                            elif cards.quiz_card_index < len(cards.quiz_cards):
                                # Use regular quiz cards on the classic board
                                question, options, correct = cards.quiz_cards[cards.quiz_card_index]
                                game_state['quiz_question'] = (question, options, correct)
                                game_state['show_quiz'] = True
                                game_state['quiz_state'] = 'growing'
                                game_state['quiz_start_time'] = time.time()
                                game_state['pop_played'] = False
                                audio.drum_machine_sound.play()
                                cards.quiz_card_index = (cards.quiz_card_index + 1) % len(cards.quiz_cards)
                                game_state['message'] = f"Player {players[game_state['current_player']].id + 1} faces a quiz."
                            
                            # Clear the pending quiz flag
                            del game_state['pending_quiz']
                        
                        # We no longer need to clear the processing_bonus_card flag
                        # since we don't set it anymore
                        
                        # End the player's turn only if they have no active animations
                        # This ensures they can potentially get another bonus card if they landed on a B square
                        current_player = players[game_state['current_player']]
                        if not current_player.active_animations:
                            current_player.turn_ended = True

            # Handle CPU player turns
            if not animations_active and not game_state.get('show_quiz', False) and not game_state.get('show_path_choice_after_roll', False) and not game_state.get('rolling_dice', False) and 'movement_delay_start' not in game_state and not game_state.get('processing_bonus_card', False):
                current_player = players[game_state['current_player']]
                if current_player.is_computer and not current_player.has_rolled and not current_player.finished:
                    # Check if player is in jail first
                    if current_player.in_jail:
                        # Check if CPU has a Get Out of Jail Free card
                        if current_player.has_jail_free_card:
                            # Use the card automatically for CPU players
                            current_player.in_jail = False
                            current_player.has_jail_free_card = False  # Use up the card
                            
                            # Clear the jail marker
                            current_player.jail_from_x = None
                            current_player.jail_from_y = None
                            current_player.jail_marker_anim_start = None
                            
                            # Set up the animation to exit jail
                            anim = {
                                'player': current_player,
                                'start_pos': JAIL_POS,
                                'end_pos': squares_coords[current_player.prev_position],
                                'steps': 60,
                                'current_step': 0,
                                'last_time': time.time(),
                                'message': f"CPU Player {current_player.id + 1} used Get Out of Jail Free card!",
                                'is_jail_move': True,
                                'delay': 0.0167,  # ~60fps (1/60 second)
                                'jail_action': 'exit'
                            }
                            
                            # Play the sound
                            audio.head_shake_cpu_sound.play()
                            current_player.active_animations.append(anim)
                            game_state['message'] = f"CPU Player {current_player.id + 1} used Get Out of Jail Free card!"
                            current_player.turn_ended = True
                        else:
                            message, moved = move_player(current_player, game_state)
                            game_state['message'] = message
                            # If player has escaped jail (check after move_player which may clear in_jail)
                            if not current_player.in_jail:
                                # Clear the jail marker
                                current_player.jail_from_x = None
                                current_player.jail_from_y = None
                                current_player.jail_marker_anim_start = None
                    else:
                        message, moved = move_player(current_player, game_state)
                        game_state['message'] = message
                        
                elif current_player.finished:
                    current_player.has_rolled = False
                    current_player.turn_ended = False
                    
                    # Clear dice roll values and doubles flag when a player's turn ends
                    if 'dice_roll_1' in game_state:
                        del game_state['dice_roll_1']
                    if 'dice_roll_2' in game_state:
                        del game_state['dice_roll_2'] 
                    if 'is_doubles' in game_state:
                        del game_state['is_doubles']
                    if 'doubles_sound_played' in game_state:
                        del game_state['doubles_sound_played']
                        
                    game_state['current_player'] = (game_state['current_player'] + 1) % len(players)
                    while players[game_state['current_player']].finished and len(game_state['finish_order']) < len(players):
                        game_state['current_player'] = (game_state['current_player'] + 1) % len(players)
                    # Clear last bonus position at the start of the next player's turn
                    if str(game_state['current_player']) in game_state['last_bonus_position']:
                        del game_state['last_bonus_position'][str(game_state['current_player'])]
                elif current_player.turn_ended and not current_player.active_animations:
                    current_player.has_rolled = False
                    current_player.turn_ended = False
                    
                    # Clear dice roll values and doubles flag when a player's turn ends
                    if 'dice_roll_1' in game_state:
                        del game_state['dice_roll_1']
                    if 'dice_roll_2' in game_state:
                        del game_state['dice_roll_2'] 
                    if 'is_doubles' in game_state:
                        del game_state['is_doubles']
                    if 'doubles_sound_played' in game_state:
                        del game_state['doubles_sound_played']
                        
                    game_state['current_player'] = (game_state['current_player'] + 1) % len(players)
                    while players[game_state['current_player']].finished and len(game_state['finish_order']) < len(players):
                        game_state['current_player'] = (game_state['current_player'] + 1) % len(players)
                    # Clear last bonus position at the start of the next player's turn
                    if str(game_state['current_player']) in game_state['last_bonus_position']:
                        del game_state['last_bonus_position'][str(game_state['current_player'])]
            
            # Check if a bonus card animation has just completed and clear the processing flag
            if not game_state.get('bonus_image_state') and game_state.get('processing_bonus_card', False):
                game_state['processing_bonus_card'] = False
                
            # Handle CPU players automatically answering quiz cards
            if game_state.get('show_quiz', False) and 'quiz_buttons' in game_state:
                current_player = players[game_state['current_player']]
                if current_player.is_computer:
                    # Add a slight delay before CPU answers the quiz to make the game feel more natural
                    if 'cpu_quiz_delay' not in game_state:
                        game_state['cpu_quiz_delay'] = time.time() + 3.0  # 3 second delay to read question
                    elif time.time() > game_state['cpu_quiz_delay']:
                        # CPU player makes a choice based on difficulty
                        _, _, correct = game_state['quiz_question']
                        is_correct = False
                        
                        # Determine if CPU gets answer correct based on difficulty
                        if current_player.difficulty == 'easy':
                            is_correct = random.random() < 0.3  # 30% chance to get it right
                        elif current_player.difficulty == 'normal':
                            is_correct = random.random() < 0.5  # 50% chance to get it right
                        elif current_player.difficulty == 'hard':
                            is_correct = random.random() < 0.7  # 70% chance to get it right
                        else:
                            is_correct = random.random() < 0.5  # Default 50% chance
                        
                        # Select the option index for the CPU (correct or random incorrect)
                        selected_option = correct if is_correct else random.choice([i for i in range(len(game_state['quiz_buttons'])) if i != correct])
                        
                        # Add splash effect tracking
                        game_state['clicked_quiz_button'] = selected_option
                        game_state['button_click_time'] = time.time()
                        
                        # Wait a moment to let the splash effect be visible before applying the effect
                        game_state['cpu_splash_delay'] = time.time() + 1.0  # 1.0 second delay to show splash
                        game_state['cpu_splash_option'] = selected_option
                        game_state['cpu_splash_is_correct'] = is_correct
                        
                        # Remove the CPU quiz delay after it's used
                        del game_state['cpu_quiz_delay']
                    
                    # Check if we need to apply the quiz effect after showing the splash effect
                    if 'cpu_splash_delay' in game_state and time.time() > game_state['cpu_splash_delay']:
                        is_correct = game_state['cpu_splash_is_correct']
                        
                        if is_correct:
                            # Apply quiz effect for correct answer
                            game_state['message'] = f"Player {current_player.id + 1} answered correctly!"
                            audio.mac_os_dinbg_sound.play()
                            game_state['quiz_state'] = 'answered'
                            game_state['quiz_answer_delay_start'] = time.time()
                            if 'quiz_buttons' in game_state:
                                del game_state['quiz_buttons']
                            
                            # Explicitly set both flags to ensure turn ends
                            current_player.turn_ended = True
                            current_player.has_rolled = True
                            
                            # If this quiz came from a bonus card, mark it completed
                            if game_state.get('processing_bonus_card', False):
                                game_state['quiz_from_bonus_completed'] = True
                        else:
                            # For wrong answers, use the regular function
                            apply_quiz_effect(current_player, False, game_state, scale)
                        
                        # Remove the splash delay after it's used
                        del game_state['cpu_splash_delay']
                        del game_state['cpu_splash_option']
                        del game_state['cpu_splash_is_correct']

            # Handle CPU players automatically handling bonus cards
            if 'bonus_image_state' in game_state and game_state['bonus_image_state'] == 'showing':
                current_player = players[game_state['current_player']]
                if current_player.is_computer:
                    # Check if we've hit the 2-second bonus action timer
                    if 'bonus_action_start_time' in game_state and time.time() - game_state['bonus_action_start_time'] >= 2.0:
                        # For "pick_quiz" bonus action, we need to wait until the quiz is complete
                        if game_state['bonus_action'][0] != "pick_quiz" or not game_state.get('show_quiz', False):
                            # Start the bonus action (the actions themselves are already handled in the bonus_image_state section)
                            # We just need to trigger the shrinking animation to complete the bonus card process
                            game_state['bonus_image_state'] = 'flipping_back'
                            game_state['bonus_flip_back_start'] = time.time()
                            game_state['bonus_flipped'] = False
                            
                            # Remove the CPU bonus delay if it exists
                            if 'cpu_bonus_delay' in game_state:
                                del game_state['cpu_bonus_delay']
                            
                            # Make sure has_rolled is set to true to ensure turn ends properly
                            current_player.has_rolled = True
                    # Otherwise, use the standard CPU delay logic
                    elif 'cpu_bonus_delay' not in game_state:
                        game_state['cpu_bonus_delay'] = time.time() + 1.5  # Increased to 1.5 seconds delay
                    elif time.time() > game_state['cpu_bonus_delay']:
                        # For "pick_quiz" bonus action, we need to wait until the quiz is complete
                        if game_state['bonus_action'][0] == "pick_quiz" and game_state.get('show_quiz', False):
                            # Wait for quiz to finish
                            pass
                        else:
                            # Start the bonus action (the actions themselves are already handled in the bonus_image_state section)
                            # We just need to trigger the shrinking animation to complete the bonus card process
                            game_state['bonus_image_state'] = 'shrinking'
                            game_state['bonus_shrink_start'] = time.time()
                            
                            # Remove the CPU bonus delay after it's used
                            del game_state['cpu_bonus_delay']
                            
                            # Make sure has_rolled is set to true to ensure turn ends properly
                            current_player.has_rolled = True

            # Handle CPU players automatically picking paths
            if game_state.get('show_path_choice_after_roll', False) and 'path_buttons' in game_state:
                current_player = players[game_state['current_player']]
                if current_player.is_computer:
                    # Add a slight delay before CPU picks a path to make it feel more natural
                    if 'cpu_path_delay' not in game_state:
                        game_state['cpu_path_delay'] = time.time() + 2.5  # 2.5 second delay to read options
                    elif time.time() > game_state['cpu_path_delay']:
                        # CPU player makes a choice - for now, simple random selection
                        # In the future, this could be more intelligent based on difficulty
                        choice_idx = random.randrange(len(game_state['path_buttons']))
                        _, choice = game_state['path_buttons'][choice_idx]
                        
                        # Add splash effect tracking for path buttons (visual feedback)
                        game_state['clicked_path_button'] = choice_idx
                        game_state['path_button_click_time'] = time.time()
                        
                        # Set a small delay for the splash effect before moving
                        if 'cpu_path_splash_delay' not in game_state:
                            game_state['cpu_path_splash_delay'] = time.time() + 0.8  # 0.8 second splash
                        elif time.time() > game_state['cpu_path_splash_delay']:
                            # Finalise the choice and start the movement animation
                            current_player.path_choices[current_player.position] = choice
                            remaining_spaces = game_state.get('spaces_remaining', 0)
                            
                            # Check if the player started their turn on the choice point
                            started_on_choice = isinstance(next_positions[current_player.position], list)
                            movement_path = get_movement_path_with_choice(current_player.position, choice, remaining_spaces, squares, next_positions, started_on_choice)
                            
                            anim = {
                                'player': current_player,
                                'path': movement_path,
                                'index': 0,
                                'last_time': time.time(),
                                'message': f"CPU Player {current_player.id + 1} chose a path. Moving {remaining_spaces if started_on_choice else remaining_spaces - 1} more spaces.",
                                'is_initial_move': True,
                                'delay': 0.5
                            }
                            current_player.active_animations.append(anim)
                            audio.indigogo_sound.play()
                            
                            # Clean up game state flags
                            game_state['show_path_choice_after_roll'] = False
                            del game_state['path_buttons']
                            if 'roll_for_path_choice' in game_state:
                                del game_state['roll_for_path_choice']
                            if 'spaces_remaining' in game_state:
                                del game_state['spaces_remaining']
                            
                            # Remove CPU-specific delays
                            del game_state['cpu_path_delay']
                            del game_state['cpu_path_splash_delay']
                            
                            current_player.has_rolled = True

            dice_rect, restart_button_rect, achievement_button_rect, settings_button_rect, magnify_button_rect, quiz_answer_rects = draw_board(players, game_state, scale, offset_x, offset_y, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, achievement_button_scaled, magnify_button_scaled, bonus_result_images_scaled)

            # Draw Achievements Pane if active
            if game_state.get('show_achievements_menu', False):
                render_achievements_pane(screen, scale, offset_x, offset_y, game_state['selected_board'])

            
            # Display player timers and positions in the top-right corner if enabled in settings
            if game_state.get('show_timers', False):
                timer_x = SCREEN_WIDTH - 200 * scale  # Right side of screen with padding
                timer_y_start = 30 * scale  # Start near the top
                timer_spacing = 40 * scale  # Space between each player timer
                display_player_timers(game_state, screen, font, timer_x, timer_y_start, timer_spacing, players, player_colours)
            
            # Check if it's time to play the jail sound
            if game_state.get('jail_sound_delay') and not game_state.get('jail_sound_played', False):
                if time.time() > game_state['jail_sound_delay']:
                    audio.mac_os_uh_ohh_sound.play()
                    game_state['jail_sound_played'] = True
            
            pygame.display.flip()
            clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()