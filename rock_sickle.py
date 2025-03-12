import pygame
import random
import time
import sys
import os
import traceback
import logging
import math
import json

# Set up logging for debug purposes
logging.basicConfig(
    filename=os.path.join(os.path.abspath(os.path.dirname(__file__)), "rock_sickle.log"),
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
bonus_result_images_scaled = {}
bonus_images_scaled = {}
board_image_scaled = None

# Game progress file functions
def get_progress_file_path():
    """Get path to the game progress file."""
    # Store in same directory as the script
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "rock_sickle_progress.json")

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

# Work out the base path for assets
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.dirname(__file__))

def load_asset(relative_path):
    """Load an asset from the given relative path."""
    full_path = os.path.join(base_path, relative_path)
    if not os.path.exists(full_path):
        logger.error(f"Asset not found: {full_path}")
        raise FileNotFoundError(f"Asset not found: {full_path}")
    return full_path

# Initialise Pygame
pygame.init()
logger.info("Pygame initialised successfully")

# Set a custom icon for the game window
icon_path = load_asset("Assets/Images/Icons/RockSickle.png")
icon_surface = pygame.image.load(icon_path)
pygame.display.set_icon(icon_surface)
logger.info(f"Custom icon set successfully: {icon_path}")

# Screen settings - keeping it flexible for resizing
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = 800, 600
SCREEN_WIDTH, SCREEN_HEIGHT = ORIGINAL_WIDTH, ORIGINAL_HEIGHT
offset_x, offset_y = 0, 0
scale = 1.0
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Rock-Sickle")
logger.info("Display initialised successfully")

# Define some colours for the game
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
PINK = (255, 192, 203)
DULL_PINK = (219, 172, 183)  # A more muted pink for the expert board background
DARK_GREY = (64, 64, 64)
player_colours = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

# Load image assets - tiles, players, and all that jazz
try:
    # Load classic tile images - convert all to 32-bit RGBA format
    def load_and_convert(path):
        """Load an image and convert it to 32-bit RGBA format for proper scaling"""
        img = pygame.image.load(load_asset(path))
        return img.convert_alpha() if img.get_flags() & pygame.SRCALPHA else img.convert()
    
    forward_one_original = load_and_convert("Assets/Images/Tiles/Forward One.png")
    back_two_original = load_and_convert("Assets/Images/Tiles/Back Two.png")
    restart_button_original = load_and_convert("Assets/Images/Tiles/Restart.png")
    settings_button_original = load_and_convert("Assets/Images/Tiles/Mr Geary.png")
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
    
    # Load expert tile images - convert all to 32-bit RGBA surface format
    def load_and_convert(path):
        """Load an image and convert it to 32-bit RGBA format for proper scaling"""
        img = pygame.image.load(load_asset(path))
        return img.convert_alpha() if img.get_flags() & pygame.SRCALPHA else img.convert()
    
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
            'settings': settings_button_original
        },
        'Expert': {
            'restart': e_restart_button_original,
            'settings': e_settings_button_original
        },
        'Secret': {
            'restart': restart_button_original,  # Reuse Classic buttons for Secret board
            'settings': settings_button_original
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
    player_images_original = [pygame.image.load(load_asset(img)) for img in player_image_paths]
    logger.info("Original player images loaded successfully")
except Exception as e:
    logger.error(f"Error loading player images: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    cpu_image_original = pygame.image.load(load_asset("Assets/Images/Players/Player CPU.png"))
    logger.info("Original CPU image loaded successfully")
except Exception as e:
    logger.error(f"Error loading CPU image: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    dice_images_original = [
        pygame.image.load(load_asset(f"Assets/Images/Dices/{i}.png")) for i in range(1, 7)
    ]
    logger.info("Original dice images loaded successfully")
except Exception as e:
    logger.error(f"Error loading dice images: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    difficulty_images_original = {
        'easy': pygame.image.load(load_asset("Assets/Images/DifficultyButtons/1Baby.png")),
        'normal': pygame.image.load(load_asset("Assets/Images/DifficultyButtons/3Consentrated.png")),
        'hard': pygame.image.load(load_asset("Assets/Images/DifficultyButtons/4Angery.png")),
    }
    logger.info("Original difficulty images loaded successfully")
    
    # Load CPU difficulty images
    cpu_difficulty_images_original = {
        'easy': pygame.image.load(load_asset("Assets/Images/Players/CPUEasy.png")),
        'normal': pygame.image.load(load_asset("Assets/Images/Players/CPUNormal.png")),
        'hard': pygame.image.load(load_asset("Assets/Images/Players/CPUHard.png")),
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
        img = pygame.image.load(load_asset(path))
        new_img = pygame.Surface(img.get_size(), pygame.SRCALPHA, 32)
        new_img.blit(img, (0, 0))
        bonus_result_images_original[key] = new_img
    logger.info("Original bonus result images loaded successfully as 32-bit surfaces")
except Exception as e:
    logger.error(f"Error loading bonus result images: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Load audio assets - sounds to spice things up
try:
    roll_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Drum Roll (Roll the Dice).wav"))
    glug_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Glug (Moving).wav"))
    bonk_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Bonk (Stay In Jail).wav"))
    head_shake_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Head Shake (Exit Jail).wav"))
    whiz_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Whiz2 (Moving to Jail).wav"))
    drip_drop_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Drip Drop (Pick up Bonus Card).wav"))
    drum_machine_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Drum Machine (Pick up Quiz Card).wav"))
    win_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Odesong (Win).wav"))
    pop_sound = pygame.mixer.Sound(load_asset("Assets/Audio/pop (Anser Buttons Appear).wav"))
    bing_bong_sound = pygame.mixer.Sound(load_asset("Assets/Audio/bing_bong (Incorrect Quiz Answer).wav"))
    connect_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Connect.wav"))
    disconnect_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Disconnect (Put Card Away).wav"))
    indigogo_sound = pygame.mixer.Sound(load_asset("Assets/Audio/indigogo (Path Chosen).wav"))
    jump_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Jump (Forward a Space).wav"))
    mac_os_dinbg_sound = pygame.mixer.Sound(load_asset("Assets/Audio/mac_os_dinbg (Quiz Answer Correct).wav"))
    mac_os_uh_ohh_sound = pygame.mixer.Sound(load_asset("Assets/Audio/mac_os_uh_ohh (Sent to Jail by Bonus Card).wav"))
    super_mario_sound = pygame.mixer.Sound(load_asset("Assets/Audio/super_mario_64_soundtrack_correct_solution (Amount of Players has been Chosen).wav"))
    wobble_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Wobble (Back a Space).wav"))
    fairlin_round1_sound = pygame.mixer.Sound(load_asset("Assets/Audio/SE1_EVT_FAIRLIN_ROUND1 (Win).wav"))
    pong_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Pong (Player Not Set).wav"))
    voltage_easy_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Voltage (Easy CPU Player Selected).wav"))
    voltage_normal_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Voltage2 (Normal CPU Player Selected).wav"))
    voltage_hard_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Voltage3 (Hard CPU Player Selected).wav"))
    whit_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Whit (Player Set).wav"))
    restart_sound = pygame.mixer.Sound(load_asset("Assets/Audio/SE4_F_MAWASU_ROUND1.wav"))
    
    # Load car horn sound for Free Parking
    car_horn_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Car Horn.wav"))
    
    # Load CPU-specific sound effects
    bonk_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/BonkCPU.wav"))
    glug_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/GlugCPU.wav"))
    head_shake_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Head ShakeCPU.wav"))
    jump_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/JumpCPU.wav"))
    whiz_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/WhizCPU.wav"))
    wobble_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/WobbleCPU.wav"))
    
    logger.info("Audio assets loaded successfully")
except Exception as e:
    logger.error(f"Error loading audio assets: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Font setup for text rendering
font = pygame.font.SysFont(None, 24)

# Define the game board squares and their coordinates
def get_board_squares(board_type="Classic"):
    if board_type == "Classic":
        return [
            'Go', '1', '0', 'Q', '-2', 'J', '1', 'B', '0', '0',
            'J', '0', '1', '-2', '1', '-2', '0',
            'B', '0', '-2', 'Q', 'B', 'P',
            '0', '1', 'B', 'J', 'Q', '-2', '0',
            '0', '1', 'J', '-2', 'Q', '-2', '0',
            'F'
        ], list(range(1, 23)) + [[23, 30]] + list(range(24, 30)) + [37] + list(range(31, 37)) + [37] + [None]
    elif board_type == "Secret":
        # Create a 1000-space secret board with a winding pattern
        secret_squares = ['Go']
        
        # Fill the board with 998 random spaces (ensuring a good mix of types)
        square_types = ['0', '1', '-2', 'B', 'J', 'Q']
        weights = [3, 3, 3, 2, 2, 2]  # Weights for more balanced distribution
        
        # Generate 998 spaces with weighted random distribution, avoiding problematic sequences
        prev_two_squares = []  # Keep track of the last two squares
        
        for _ in range(998):
            # Prevent problematic sequences like "1, 1, -2" that could cause softlocks
            if len(prev_two_squares) >= 2 and prev_two_squares[-2:] == ['1', '1']:
                # If we have "1, 1", don't allow "-2" next
                valid_types = [t for t in square_types if t != '-2']
                valid_weights = [weights[square_types.index(t)] for t in valid_types]
                space_type = random.choices(valid_types, weights=valid_weights, k=1)[0]
            elif len(prev_two_squares) >= 2 and prev_two_squares[-2:] == ['-2', '-2']:
                # If we have "-2, -2", don't allow another "-2" to avoid excessive backtracking
                valid_types = [t for t in square_types if t != '-2']
                valid_weights = [weights[square_types.index(t)] for t in valid_types]
                space_type = random.choices(valid_types, weights=valid_weights, k=1)[0]
            else:
                # Normal random selection
                space_type = random.choices(square_types, weights=weights, k=1)[0]
            
            # Add the selected space type
            secret_squares.append(space_type)
            
            # Update the history of previous squares
            prev_two_squares.append(space_type)
            if len(prev_two_squares) > 2:
                prev_two_squares.pop(0)
        
        # Add the finish at the end
        secret_squares.append('F')
        
        # Simple sequential next positions (no branching paths)
        secret_next_positions = list(range(1, 1000)) + [None]
        
        return secret_squares, secret_next_positions
    else:  # Expert board
        # Properly structured expert board based on Kong.rtf
        expert_squares = []
        
        # [Direction East] 1, Q, -2, J, 1, B, -2, 1, J, Q, Q, J, 1, Q, -2
        expert_squares.extend(['Go', '1', 'Q', '-2', 'J', '1', 'B', '-2', '1', 'J', 'Q', 'Q', 'J', '1', 'Q', '-2'])
        
        # [Direction South] 1, B, 1, 0, 0, -2, P
        expert_squares.extend(['1', 'B', '1', 'FP', '0', '-2', 'P'])
        
        # Path directions after P - here we need to account for all possible paths
        # (Path West) [Direction West] 0, -2, J, 1, 1
        west_path_1 = ['0', '-2', 'J', '1', '1']
        
        # (Path West) [Direction South] 0
        west_path_2 = ['0']
        
        # (Path West) [Direction West] 1
        west_path_3 = ['1']
        
        # (Path West) [Direction South] -2, 0
        west_path_4 = ['-2', '0']
        
        # (Path West) [Direction East] 0
        west_path_5 = ['0']
        
        # (Path West) [Direction South] 0, 0
        west_path_6 = ['0', '0']
        
        # (Path West) [Direction West] B, 0, 1, -2, 1, -2, J, 1, B, -2
        west_path_7 = ['B', '0', '1', '-2', '1', '-2', 'J', '1', 'B', '-2']
        
        # (Path West) [Direction North] 1, 1, B, Q, 1, 1, J, -2, Q, B, Finish
        west_path_8 = ['1', '1', 'B', 'Q', '1', '1', 'J', '-2', 'Q', 'B', 'F']
        
        # (Path South) [Direction South] 0, 1, Q, -2, B
        # Adjust to end with the B square that should be at the corner
        south_path_1 = ['0', '1', 'Q', '-2', 'B']
        
        # (Path South) [Direction West] 1, J, 1, -2, 0, B, 0, 1, -2, 1, -2, J, 1, B, -2
        # Update to match the requested layout exactly
        south_path_2 = ['1', 'J', '1', '-2', '0', 'B', '0', '1', '-2', '1', '-2', 'J', '1', 'B', '-2']
        
        # (Path South) [Direction North] 1, 1, B, Q, 1, 1, J, -2, Q, B, Finish
        # Update to match the requested layout exactly
        south_path_3 = ['1', '1', 'B', 'Q', '1', '1', 'J', '-2', 'Q', 'B', 'F']
        
        # Now we need to add junction/path selection logic - this will be handled in next_positions
        # For now, we're just creating the complete board
        west_path = west_path_1 + west_path_2 + west_path_3 + west_path_4 + west_path_5 + west_path_6 + west_path_7 + west_path_8
        south_path = south_path_1 + south_path_2 + south_path_3
        
        # Build next_positions for expert board
        # This is complex and needs to account for the multiple paths
        expert_next_positions = []
        
        # First, handle the straight parts (East and South until P)
        main_path_length = len(expert_squares)
        for i in range(main_path_length - 1):  # All but P
            expert_next_positions.append(i + 1)
        
        # At P, we have a choice - west path or south path
        # The choice will be represented as a list of options
        # We'll add path choice at the P position
        pick_path_pos = main_path_length - 1  # P's position
        west_path_start = main_path_length
        south_path_start = main_path_length + len(west_path)
        expert_next_positions.append([west_path_start, south_path_start])
        
        # Add the west path positions
        for i in range(len(west_path) - 1):
            expert_next_positions.append(west_path_start + i + 1)
        # Last position on west path leads to finish
        expert_next_positions.append(None)  # Finish
        
        # Add the south path positions
        for i in range(len(south_path) - 1):
            expert_next_positions.append(south_path_start + i + 1)
        # Last position on south path leads to finish
        expert_next_positions.append(None)  # Finish
        
        # Complete expert board with all paths
        complete_expert_squares = expert_squares + west_path + south_path
        
        return complete_expert_squares, expert_next_positions

# Default to Classic board
squares, next_positions = get_board_squares("Classic")

# Define a small gap between squares (represents 1mm)
GAP_BETWEEN_TILES = 2  # Pixels representing gap between tiles

# Modified squares_coords with gaps between adjacent tiles - this is for the Classic board
def get_classic_squares_coords():
    return [
        (60, 60),                                  # Go - corner
        (120 + GAP_BETWEEN_TILES, 60),             # Horizontal row - top
        (180 + 2*GAP_BETWEEN_TILES, 60),
        (240 + 3*GAP_BETWEEN_TILES, 60),
        (300 + 4*GAP_BETWEEN_TILES, 60),
        (360 + 5*GAP_BETWEEN_TILES, 60),
        (420 + 6*GAP_BETWEEN_TILES, 60),
        (480 + 7*GAP_BETWEEN_TILES, 60),
        (540 + 8*GAP_BETWEEN_TILES, 60),
        (600 + 9*GAP_BETWEEN_TILES, 60),           # Corner
        
        (600 + 9*GAP_BETWEEN_TILES, 120 + GAP_BETWEEN_TILES),    # Vertical column - right
        (600 + 9*GAP_BETWEEN_TILES, 180 + 2*GAP_BETWEEN_TILES),
        (600 + 9*GAP_BETWEEN_TILES, 240 + 3*GAP_BETWEEN_TILES),
        (600 + 9*GAP_BETWEEN_TILES, 300 + 4*GAP_BETWEEN_TILES),
        (600 + 9*GAP_BETWEEN_TILES, 360 + 5*GAP_BETWEEN_TILES),
        (600 + 9*GAP_BETWEEN_TILES, 420 + 6*GAP_BETWEEN_TILES),
        (600 + 9*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),  # Corner
        
        (540 + 8*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),  # Horizontal row - bottom 
        (480 + 7*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        (420 + 6*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        (360 + 5*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        (300 + 4*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        (240 + 3*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        
        (240 + 3*GAP_BETWEEN_TILES, 420 + 6*GAP_BETWEEN_TILES),  # Vertical column - central
        (240 + 3*GAP_BETWEEN_TILES, 360 + 5*GAP_BETWEEN_TILES),
        (180 + 2*GAP_BETWEEN_TILES, 360 + 5*GAP_BETWEEN_TILES),  # Horizontal row - central
        (120 + GAP_BETWEEN_TILES, 360 + 5*GAP_BETWEEN_TILES),
        (60, 360 + 5*GAP_BETWEEN_TILES),
        (60, 300 + 4*GAP_BETWEEN_TILES),           # Vertical column - left (part 1)
        (60, 240 + 3*GAP_BETWEEN_TILES),
        
        (180 + 2*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),  # Another path from bottom
        (120 + GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        (60, 480 + 7*GAP_BETWEEN_TILES),           # Corner
        (60, 420 + 6*GAP_BETWEEN_TILES),           # Vertical column - left (part 2) 
        (60, 360 + 5*GAP_BETWEEN_TILES),
        (60, 300 + 4*GAP_BETWEEN_TILES),
        (60, 240 + 3*GAP_BETWEEN_TILES),
        
        (60, 155 + 2*GAP_BETWEEN_TILES - 5)            # Finish line
    ]

# For the Expert board, we create a more complex layout for the larger board
def get_expert_squares_coords():
    # Make the tile size smaller to fit the larger expert board on screen
    tile_size = 40  # Smaller tiles for expert board to fit everything
    gap = 1  # Smaller gap between tiles to make everything more compact
    
    coords = []
    
    # Starting point (Go) - keep near top-left corner
    base_x = 50
    base_y = 50
    
    # [Direction East] - First row going east - compacted
    east_row_length = 16  # 'Go' + 15 tiles
    for i in range(east_row_length):
        coords.append((base_x + i * (tile_size + gap), base_y))
    
    # [Direction South] - Column going south from the east end
    south_col_length = 7
    last_x = base_x + (east_row_length - 1) * (tile_size + gap)
    for i in range(1, south_col_length + 1):
        coords.append((last_x, base_y + i * (tile_size + gap)))
    
    # P square position - this is where we branch
    p_position = len(coords) - 1
    
    # Path West positions
    # (Path West) [Direction West] - First segment going west
    west_path_1_length = 5
    west_path_start_x = last_x - (tile_size + gap)
    west_path_start_y = base_y + south_col_length * (tile_size + gap)
    for i in range(1, west_path_1_length + 1):
        coords.append((west_path_start_x - (i - 1) * (tile_size + gap), west_path_start_y))
    
    # (Path West) [Direction South] - First southern segment on west path
    west_path_south_1_y = west_path_start_y + (tile_size + gap)
    coords.append((west_path_start_x - (west_path_1_length - 1) * (tile_size + gap), west_path_south_1_y))
    
    # (Path West) [Direction West] - Continue west
    west_path_2_x = west_path_start_x - west_path_1_length * (tile_size + gap)
    coords.append((west_path_2_x, west_path_south_1_y))
    
    # (Path West) [Direction South] - Second southern segment
    west_path_south_2_length = 2
    for i in range(1, west_path_south_2_length + 1):
        coords.append((west_path_2_x, west_path_south_1_y + i * (tile_size + gap)))
    
    # (Path West) [Direction East] - Go east after south
    coords.append((west_path_2_x + (tile_size + gap), west_path_south_1_y + west_path_south_2_length * (tile_size + gap)))
    
    # (Path West) [Direction South] - Third southern segment
    west_path_south_3_start_x = west_path_2_x + (tile_size + gap)
    west_path_south_3_start_y = west_path_south_1_y + west_path_south_2_length * (tile_size + gap)
    west_path_south_3_length = 2
    for i in range(1, west_path_south_3_length + 1):
        coords.append((west_path_south_3_start_x, west_path_south_3_start_y + i * (tile_size + gap)))
    
    # (Path West) [Direction West] - Long segment going west
    west_path_3_length = 10
    west_path_3_start_x = west_path_south_3_start_x
    west_path_3_start_y = west_path_south_3_start_y + west_path_south_3_length * (tile_size + gap)
    for i in range(1, west_path_3_length + 1):
        # Shift one more tile west by adding an extra tile_size to the calculation
        coords.append((west_path_3_start_x - (i - 1) * (tile_size + gap) - (tile_size + gap), west_path_3_start_y))
    
    # (Path West) [Direction North] - Final segment going north to finish
    west_path_north_length = 11
    # Adjust the starting x position based on our shifted western path
    west_path_north_start_x = west_path_3_start_x - (west_path_3_length - 1) * (tile_size + gap) - (tile_size + gap)
    west_path_north_start_y = west_path_3_start_y
    for i in range(1, west_path_north_length + 1):
        # Shift one more tile up by adding an extra tile_size to the calculation
        coords.append((west_path_north_start_x, west_path_north_start_y - (i - 1) * (tile_size + gap) - (tile_size + gap)))
    
    # Path South positions
    # (Path South) [Direction South] - First segment going south
    south_path_1_length = 5  # matching the 5 squares in south_path_1
    south_path_start_x = last_x
    south_path_start_y = base_y + (south_col_length + 1) * (tile_size + gap)
    for i in range(1, south_path_1_length + 1):
        coords.append((south_path_start_x, south_path_start_y + (i - 1) * (tile_size + gap)))
    
    # (Path South) [Direction West] - Going west after south
    south_path_west_length = 15  # matching the 15 squares in south_path_2
    south_path_west_start_x = south_path_start_x
    south_path_west_start_y = south_path_start_y + (south_path_1_length - 1) * (tile_size + gap)
    for i in range(1, south_path_west_length + 1):
        # Shift one more tile west by adding an extra tile_size to the calculation
        coords.append((south_path_west_start_x - (i - 1) * (tile_size + gap) - (tile_size + gap), south_path_west_start_y))
    
    # (Path South) [Direction North] - Final segment going north to finish
    south_path_north_length = 11  # matching the 11 squares in south_path_3
    # Adjust the starting x position based on our shifted western path
    south_path_north_start_x = south_path_west_start_x - (south_path_west_length - 1) * (tile_size + gap) - (tile_size + gap)
    south_path_north_start_y = south_path_west_start_y
    for i in range(1, south_path_north_length + 1):
        # Shift one more tile up by adding an extra tile_size to the calculation
        coords.append((south_path_north_start_x, south_path_north_start_y - (i - 1) * (tile_size + gap) - (tile_size + gap)))
    
    return coords

# Secret board coordinates - create a winding spiral pattern with 1000 spaces
def get_secret_squares_coords():
    # Create a more consistent grid-based spiral pattern for the Secret board
    coordinates = []
    
    # Center point of the pattern
    center_x, center_y = 350, 300
    
    # Use a fixed spacing between tiles to prevent overlaps
    fixed_spacing = 18  # Consistent spacing between points
    
    # Generate coordinates using a spiral pattern with consistent spacing
    # This will create an outward spiral from the center
    
    def generate_consistent_spiral(max_points):
        # Parameters for the spiral
        x, y = center_x, center_y
        # Start with a small step size
        step_size = fixed_spacing
        
        # Direction vectors for movement (right, down, left, up)
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        direction_index = 0
        
        # How many steps to take in the current direction
        steps_in_direction = 1
        
        # Track steps taken in current direction
        steps_taken = 0
        
        # Whether we need to increase the number of steps after changing direction
        increase_steps = False
        
        spiral_points = []
        spiral_points.append((x, y))  # Start at the center
        
        for _ in range(1, max_points):
            # Calculate next position
            dx, dy = directions[direction_index]
            x += dx * step_size
            y += dy * step_size
            
            # Ensure we stay within bounds (prevent going off-screen)
            x = max(20, min(680, x))
            y = max(20, min(580, y))
            
            # Add point to our list
            spiral_points.append((int(x), int(y)))
            
            # Increment steps taken in current direction
            steps_taken += 1
            
            # Check if we need to change direction
            if steps_taken == steps_in_direction:
                steps_taken = 0
                direction_index = (direction_index + 1) % 4
                
                # Increase steps every second direction change
                if increase_steps:
                    steps_in_direction += 1
                
                increase_steps = not increase_steps
        
        return spiral_points
    
    # Generate a consistent spiral with 1000 points
    coordinates = generate_consistent_spiral(1000)
    
    return coordinates[:1000]  # Return exactly 1000 coordinates

# Initialize with classic board coordinates
squares_coords = get_classic_squares_coords()

# Jail position for each board
CLASSIC_JAIL_POS = (510 + 7*GAP_BETWEEN_TILES, 390 + 5*GAP_BETWEEN_TILES)
# Expert board JAIL_POS - positioned southwest of the P square
# P square is at coordinates (last_x, base_y + south_col_length * (tile_size + gap))
# Which is approximately (663, 330) based on the calculation in get_expert_squares_coords
EXPERT_JAIL_POS = (563, 440)  # Perfect position - moved half a millimeter (1 pixel) to the east
# Secret board JAIL_POS - positioned at a reasonable location
SECRET_JAIL_POS = (700, 50)  # Moved to far top-right corner, away from all tiles

# Start with Classic jail position
JAIL_POS = CLASSIC_JAIL_POS

DIE_POS = (300 + 4*GAP_BETWEEN_TILES, 210 + 2*GAP_BETWEEN_TILES)

# Define jail size (will be used for random positioning)
JAIL_SIZE = 60  # Reverted to original size, the visual size is controlled in resize_assets()

# Updated Quiz and Bonus Cards
quiz_cards = [
    ("What type of rock can you find fossils in?", ["Granite", "Sedimentary", "Metamorphic"], 1),
    ("Is granite a metamorphic rock?", ["Yes", "No"], 1),
    ("How are igneous rocks formed?", ["By layers of sediment building up", "When magma cools down", "From the Earth's crust", "When old rocks undergo intense pressure and heat"], 1),
    ("What is molten rock called underground?", ["Magma", "Erupt", "Lava"], 0),
    ("What rock contains lead?", ["Andesite", "Coal", "Gneiss", "Galena"], 3),
    ("What type of rock is formed by pressure and heat?", ["Metamorphic", "Igneous"], 0),
    ("Is air a rock?", ["Yes", "No"], 1),
    ("What are the 3 main types of rock?", ["Molten, Solid, Liquid", "Smooth, Hard, Brittle", "Adhesion, Mohs, Bead", "Sedimentary, Igneous, Metamorphic"], 3),
    ("What is your favorite flavor of math, true or false?", ["Soup", "Croissant", "Anti-Arctician", "Left"], 3),
    ("What type of rock is formed in layers?", ["Sedimentary", "When flowing water touches lava", "Igneous"], 0),
    ("Which process turns sediment into rock?", ["Weathering", "Erosion", "Lithification"], 2)
]
random.shuffle(quiz_cards)
quiz_card_index = 0

# Expert-level quiz cards that only appear on the expert board
expert_quiz_cards = [
    ("What process in the rock cycle is primarily responsible for transforming sedimentary rock into metamorphic rock?", ["Weathering", "Melting", "Compaction and cementation", "Heat and pressure"], 3),
    ("Which factor most directly influences the rate of mineral crystallization in cooling magma?", ["The depth of the magma chamber", "The rate of cooling", "The presence of water vapor", "The color of the resulting rock"], 1),
    ("In the context of the rock cycle, what is the primary source of energy driving the transformation of rocks?", ["Solar radiation", "Earth's internal heat", "Gravitational pull", "Chemical reactions"], 1),
    ("Which type of rock is most likely to form from the rapid cooling of lava on Earth's surface?", ["Sedimentary", "Metamorphic", "Intrusive igneous", "Extrusive igneous"], 3),
    ("What process must occur for an igneous rock to become sediment?", ["Subduction", "Weathering and erosion", "Recrystallization", "Partial melting"], 1),
    ("Which condition is most essential for the formation of foliation in metamorphic rocks?", ["High temperature", "Directed pressure", "Rapid cooling", "Chemical precipitation"], 1),
    ("Why do sedimentary rocks often contain fossils while igneous rocks typically do not?", ["Igneous rocks form too slowly", "Sedimentary rocks form under high pressure", "Igneous rocks form from molten material", "Sedimentary rocks are always older"], 2),
    ("What is the primary mechanism by which clastic sedimentary rocks are formed?", ["Evaporation of seawater", "Compaction and cementation of fragments", "Recrystallization under heat", "Cooling of magma"], 1),
    ("Which rock type is most likely to undergo partial melting if subducted into the mantle?", ["Granite (igneous)", "Limestone (sedimentary)", "Slate (metamorphic)", "Sandstone (sedimentary)"], 0),
    ("How does the presence of water influence metamorphism?", ["It increases the melting point of rocks", "It acts as a catalyst for chemical reactions", "It prevents recrystallization", "It slows down heat transfer"], 1),
    ("What is the main difference between intrusive and extrusive igneous rocks?", ["Mineral composition", "Rate of cooling and crystal size", "Presence of fossils", "Degree of foliation"], 1),
    ("Which process in the rock cycle can lead directly to the formation of magma?", ["Weathering", "Lithification", "Melting", "Deposition"], 2),
    ("Why are metamorphic rocks often found near tectonic plate boundaries?", ["They form from sediment deposition", "They result from intense heat and pressure", "They cool rapidly at the surface", "They are eroded from igneous rocks"], 1),
    ("What type of rock is most likely to form from the evaporation of mineral-rich water?", ["Clastic sedimentary", "Chemical sedimentary", "Foliated metamorphic", "Extrusive igneous"], 1),
    ("Which mineral property is most critical in determining how a rock responds to weathering?", ["Hardness", "Color", "Luster", "Specific gravity"], 0),
    ("How does subduction contribute to the rock cycle?", ["It recycles oceanic crust into magma", "It deposits sediment on the seafloor", "It cools lava into extrusive rocks", "It erodes mountains into sediment"], 0),
    ("What is the primary reason that igneous rocks like basalt lack the layering seen in sedimentary rocks?", ["They form from rapid sediment deposition", "They crystallize from a molten state", "They are subjected to high pressure", "They contain more water"], 1),
    ("Which process can transform a metamorphic rock back into an igneous rock?", ["Erosion", "Melting and cooling", "Compaction", "Chemical weathering"], 1),
    ("Why do some sedimentary rocks exhibit cross-bedding?", ["They form under high heat", "They are deposited by wind or water currents", "They recrystallize under pressure", "They cool slowly underground"], 1),
    ("What role does tectonic uplift play in the rock cycle?", ["It melts rocks into magma", "It exposes rocks to weathering and erosion", "It compacts sediment into rock", "It cools lava into igneous rock"], 1),
    ("Who is \"The Rock\" in popular culture?", ["Arnold Schwarzenegger", "Sylvester Stallone", "Dwayne Johnson", "Mount Rushmore"], 2)
]
random.shuffle(expert_quiz_cards)
expert_quiz_card_index = 0

# Classic bonus cards
bonus_cards = [
    "Go to Jail!",
    "Rok guy is on to you! Go to jail!",
    "Move forward three spaces",
    "Go to jail yay... not",
    "Go back three spaces",
    "Move four spaces forward",
    "Move backwards one space",
    "Oh no! If you are holding this card you have to GO TO JAIL!",
    "Move back one space",
    "Go back five spaces",
    "Go three spaces forward",
    "Move forward two spaces",
    "Pick up a quiz card",
    "Pick up a quiz card",
    "Pick up a quiz card"
]
random.shuffle(bonus_cards)
bonus_card_index = 0

# Expert bonus cards
expert_bonus_cards = [
    "Go back two spaces",
    "Go back two spaces",
    "Go back five spaces",
    "Go back five spaces",
    "Move forward two spaces",
    "Move forward two spaces",
    "Move forward two spaces",
    "Move forward two spaces",
    "Move forward two spaces",
    "Move forward two spaces",
    "Move forward five spaces",
    "Go To Jail",
    "Go To Jail",
    "Go To Jail",
    "Go To Jail",
    "Get Out of Jail Free"
]
random.shuffle(expert_bonus_cards)
expert_bonus_card_index = 0

class Player:
    """Class to represent a player in the game."""
    def __init__(self, id, colour_index, is_computer=False, difficulty=None):
        self.id = id
        self.colour_index = colour_index
        self.is_computer = is_computer
        self.difficulty = difficulty
        self.position = 0
        self.in_jail = False
        self.finished = False
        self.finish_order = None
        self.has_rolled = False
        self.prev_position = 0
        
        # Initialize player position based on the coordinates of GO square (position 0)
        # Add centering adjustment to ensure player is in the center of the GO tile
        self.current_x = squares_coords[0][0]
        self.current_y = squares_coords[0][1]
        
        self.turn_ended = False
        self.position_history = []
        self.active_animations = []
        self.path_choices = {}  # Store path choices for each choice point
        self.jail_x, self.jail_y = None, None  # Store player-specific jail position
        self.quiz_cards = 3
        # Add these new attributes for jail standee markers
        self.jail_from_x = None  # X-coordinate of the position before jail
        self.jail_from_y = None  # Y-coordinate of the position before jail
        self.jail_marker_anim_start = None  # Time when the standee animation begins
        # Add player timer attributes
        self.start_time = None  # Time when player starts the game
        self.finish_time = None  # Time when player finishes the game
        self.elapsed_time = None  # Total time taken to finish the game
        # Add victory cutscene attributes
        self.victory_x = None
        self.victory_y = None  # Final Y position in victory formation
        self.victory_scale_factor = 1.0  # Scale factor for victory pose
        
        # Add jail free card flag
        self.has_jail_free_card = False

def roll_die(difficulty=None):
    """Roll the die based on difficulty level."""
    if difficulty == 'easy':
        return random.choice([1, 1, 2, 2, 3, 4])
    elif difficulty == 'hard':
        return random.choice([3, 4, 5, 6, 6, 6])
    else:
        return random.randint(1, 6)

def interpolate_position(start_pos, end_pos, steps, current_step):
    """Calculate position between start and end for animations."""
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    x = start_x + (end_x - start_x) * current_step / steps
    y = start_y + (end_y - start_y) * current_step / steps
    return x, y

def get_movement_path(start_pos, spaces, game_state, in_jail=False):
    """Get the path for moving a certain number of spaces."""
    path = [start_pos]
    current_pos = start_pos
    if in_jail:
        return path
    for i in range(spaces):
        if current_pos >= len(squares) - 1:
            path.append(len(squares) - 1)
            break
        next_pos = next_positions[current_pos]
        if isinstance(next_pos, list):
            # Move to the choice point and stop
            path.append(current_pos)  # Stop at the choice point
            game_state['spaces_remaining'] = spaces - i  # Remaining spaces after reaching choice point
            break
        else:
            current_pos = next_pos if next_pos is not None else current_pos
            path.append(current_pos)
    else:
        game_state['spaces_remaining'] = 0  # Used all spaces if we didn't break
    return path

def get_movement_path_with_choice(start_pos, choice, remaining_spaces, started_on_choice=False):
    """Get the path when a player chooses a direction at a fork."""
    # If player started on the choice point, the first position is their current position (start_pos)
    # and their first move is from start_pos to the chosen path
    if started_on_choice:
        # Since the player is already on a P square, start_pos is where they are
        # and the first step is to move to the chosen path
        path = [start_pos]
        current_pos = start_pos
    else:
        # Player landed on the choice point during movement, so add both positions
        path = [start_pos, choice]
        current_pos = choice
    
    # Calculate remaining spaces after first move
    # If started on choice point, we use 1 space to move to choice, leaving (remaining_spaces-1)
    # If landed on choice during movement, we also subtract 1 because moving to choice uses 1 space
    spaces_to_move = remaining_spaces - 1
    
    # Move the first step to the chosen path if started on choice point
    if started_on_choice:
        current_pos = choice
        path.append(choice)
    
    # Move remaining spaces from the chosen path
    for _ in range(spaces_to_move):
        if current_pos >= len(squares) - 1:
            path.append(len(squares) - 1)
            break
        next_pos = next_positions[current_pos]
        if isinstance(next_pos, list):
            break
        else:
            current_pos = next_pos if next_pos is not None else current_pos
            path.append(current_pos)
    return path

def get_ending_position_after_choice(start_pos, choice, steps):
    """Determine final position after choosing a path."""
    path = get_movement_path_with_choice(start_pos, choice, steps)
    return path[-1]

def parse_bonus_card(card_text):
    """Parse the bonus card text to determine its effect."""
    lower_text = card_text.lower()
    if "get out of jail free" in lower_text:
        return ("jail_free",)
    elif "jail" in lower_text:
        return ("go_to_jail",)
    elif "pick up a quiz card" in lower_text:
        return ("pick_quiz",)
    else:
        num_words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        for word, num in num_words.items():
            if word in lower_text:
                if "forward" in lower_text:
                    return ("move_forward", num)
                elif "back" in lower_text or "backwards" in lower_text:
                    return ("move_back", num)
        
        # Direct number parsing
        for num in range(1, 6):
            if str(num) in lower_text:
                if "forward" in lower_text:
                    return ("move_forward", num)
                elif "back" in lower_text:
                    return ("move_back", num)
    
    return ("unknown",)

def get_bonus_image_key(effect, board_type="Classic"):
    """Get the image key for the bonus effect with random selection for alternates."""
    # Use expert board images when on expert board
    if board_type == "Expert":
        if effect[0] == "move_forward":
            num = effect[1]
            if num == 2:
                return random.choice(['expert_forward2_1', 'expert_forward2_2', 'expert_forward2_3', 
                                      'expert_forward2_4', 'expert_forward2_5', 'expert_forward2_6'])
            elif num == 5:
                return 'expert_forward5'
        elif effect[0] == "move_back":
            num = effect[1]
            if num == 2:
                return random.choice(['expert_back2_1', 'expert_back2_2'])
            elif num == 5:
                return random.choice(['expert_back5_1', 'expert_back5_2'])
        elif effect[0] == "go_to_jail":
            return random.choice(['expert_jail1', 'expert_jail2', 'expert_jail3', 'expert_jail4'])
        elif effect[0] == "jail_free":
            return 'expert_jail_free'
    else:
        # Original classic board logic
        if effect[0] == "move_forward":
            num = effect[1]
            if num == 2:
                return 'forward2'
            elif num == 3:
                return random.choice(['forward3', 'forward3alt'])
            elif num == 4:
                return 'forward4'
        elif effect[0] == "move_back":
            num = effect[1]
            if num == 1:
                return random.choice(['back1', 'back1alt'])
            elif num == 3:
                return 'back3'
            elif num == 5:
                return 'back5'
        elif effect[0] == "go_to_jail":
            return random.choice(['jail1', 'jail2', 'jail3', 'jail4'])
        elif effect[0] == "pick_quiz":
            return random.choice(['pickquiz', 'pickquizalt', 'pickquizaltalt'])
    
    return None

def apply_effect(player, square_type, game_state, scale):
    """Apply the effect of landing on a square."""
    global quiz_card_index, bonus_card_index, expert_quiz_card_index, expert_bonus_card_index
    
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
        if game_state.get('selected_board') == "Expert" and expert_bonus_card_index < len(expert_bonus_cards):
            # Use expert bonus cards on the expert board
            # Allow picking another bonus card if:
            # 1. No bonus card animation is active, OR
            # 2. Player has moved from a different position since the last bonus card pickup
            current_pos = player.position
            last_bonus_pos = game_state.get('last_bonus_position', {}).get(str(player.id), None)
            can_pick_bonus = not game_state.get('bonus_image_key') or current_pos != last_bonus_pos
            
            if can_pick_bonus:
                bonus = expert_bonus_cards[expert_bonus_card_index]
                expert_bonus_card_index = (expert_bonus_card_index + 1) % len(expert_bonus_cards)
                drip_drop_sound.play()
                effect = parse_bonus_card(bonus)
                image_key = get_bonus_image_key(effect, "Expert")
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
            else:
                # The player can't pick a new bonus card from the same position while actively processing one
                message = f"Player {player.id + 1} must finish current bonus card first."
                player.has_rolled = True
        elif bonus_card_index < len(bonus_cards):
            # Allow picking another bonus card if:
            # 1. No bonus card animation is active, OR
            # 2. Player has moved from a different position since the last bonus card pickup
            current_pos = player.position
            last_bonus_pos = game_state.get('last_bonus_position', {}).get(str(player.id), None)
            can_pick_bonus = not game_state.get('bonus_image_key') or current_pos != last_bonus_pos
            
            if can_pick_bonus:
                bonus = bonus_cards[bonus_card_index]
                bonus_card_index = (bonus_card_index + 1) % len(bonus_cards)
                drip_drop_sound.play()
                effect = parse_bonus_card(bonus)
                image_key = get_bonus_image_key(effect, "Classic")
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
        if game_state.get('selected_board') == "Expert" and expert_quiz_card_index < len(expert_quiz_cards):
            # Use expert quiz cards on the expert board
            question, options, correct = expert_quiz_cards[expert_quiz_card_index]
            game_state['quiz_question'] = (question, options, correct)
            game_state['show_quiz'] = True
            game_state['quiz_state'] = 'growing'
            game_state['quiz_start_time'] = time.time()
            game_state['pop_played'] = False
            drum_machine_sound.play()
            expert_quiz_card_index = (expert_quiz_card_index + 1) % len(expert_quiz_cards)
            message = f"Player {player.id + 1} faces an expert quiz."
        elif quiz_card_index < len(quiz_cards):
            # Use regular quiz cards on the classic board
            question, options, correct = quiz_cards[quiz_card_index]
            game_state['quiz_question'] = (question, options, correct)
            game_state['show_quiz'] = True
            game_state['quiz_state'] = 'growing'
            game_state['quiz_start_time'] = time.time()
            game_state['pop_played'] = False
            drum_machine_sound.play()
            quiz_card_index = (quiz_card_index + 1) % len(quiz_cards)
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
        whiz_sound.play()
        
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
        win_sound.play()
        
        # Record player finish time and calculate elapsed time
        player.finish_time = time.time()
        player.elapsed_time = player.finish_time - player.start_time
        
        message = f"Player {player.id + 1} finished in {format_time(player.elapsed_time)}!"
        player.turn_ended = True
        if game_state.get('finish_order') is None:
            game_state['finish_order'] = []
        game_state['finish_order'].append(player)
        if len(game_state['finish_order']) == len(game_state['players']):
            fairlin_round1_sound.play()
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
            
            # Game completed - if this was the Classic board, unlock Expert board
            # Update game progress
            game_progress = load_game_progress()
            
            # Increment completed games counter regardless of board type
            game_progress['completed_games'] = game_progress.get('completed_games', 0) + 1
            
            # Check if we should unlock the secret board (100+ completed games)
            if game_progress['completed_games'] >= 100 and 'Secret' not in game_progress.get('unlocked_boards', []):
                game_progress['unlocked_boards'].append('Secret')
                logger.info("Secret board unlocked!")
            
            if game_state.get('selected_board') == 'Classic':
                game_progress['classic_board_completed'] = True
                if 'Expert' not in game_progress.get('unlocked_boards', ['Classic']):
                    game_progress['unlocked_boards'].append('Expert')
            
            save_game_progress(game_progress)
    elif square_type == 'Go':
        message = f"Player {player.id + 1} at start."
        player.turn_ended = True
    elif square_type == 'FP':
        message = f"Player {player.id + 1} on Free Parking."
        player.turn_ended = True
        car_horn_sound.play()
        
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
        roll_sound.play()
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
        roll_sound.play()
        return f"Player {player.id + 1} rolled {roll}.", True

def apply_quiz_effect(player, correct, game_state, scale):
    """Apply effects based on quiz answer correctness."""
    if correct:
        game_state['message'] = f"Player {player.id + 1} answered correctly!"
        mac_os_dinbg_sound.play()
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
        bing_bong_sound.play()
        
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
                    whiz_sound.play()  # Play the whiz sound for jail movement
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
                                glug_cpu_sound.play()
                            else:
                                glug_sound.play()
                        elif 'is_backwards' in anim:
                            # Play CPU or human wobble sound based on player type
                            if anim['player'].is_computer:
                                wobble_cpu_sound.play()
                            else:
                                wobble_sound.play()
                        else:
                            # Play CPU or human jump sound based on player type
                            if anim['player'].is_computer:
                                jump_cpu_sound.play()
                            else:
                                jump_sound.play()
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

def render_player_text(screen, font, prefix, player, y, scale, offset_y, player_colours):
    """Render player info text with their colour."""
    prefix_surface = font.render(prefix, True, BLACK)
    player_text = font.render("Player ", True, BLACK)
    number_text = font.render(str(player.id + 1), True, player_colours[player.colour_index])
    cpu_text = font.render(" (CPU)", True, BLACK) if player.is_computer else None

    x = int(600 * scale + offset_x)
    y = int(y + offset_y)
    screen.blit(prefix_surface, (x, y))
    x += prefix_surface.get_width()
    screen.blit(player_text, (x, y))
    x += player_text.get_width()
    screen.blit(number_text, (x, y))
    if cpu_text:
        x += number_text.get_width()
        screen.blit(cpu_text, (x, y))

def format_time(seconds):
    """Format seconds into a readable time string (MM:SS.ms)."""
    minutes = int(seconds // 60)
    seconds_remainder = seconds % 60
    return f"{minutes:02d}:{seconds_remainder:05.2f}"

def get_player_position_text(player, game_state):
    """Get the current position text for a player."""
    if player.finished:
        # Find player's placement in finish order
        try:
            placement = game_state['finish_order'].index(player) + 1
        except ValueError:
            # If player is finished but not in finish_order (shouldn't happen),
            # place them at the end of finished players
            placement = len(game_state['finish_order'])
        placement_suffix = 'st' if placement == 1 else 'nd' if placement == 2 else 'rd' if placement == 3 else 'th'
        return f"{placement}{placement_suffix} Place"
    else:
        # For players still in the game, show their current board position
        # Find how many players are ahead of this player
        ahead_count = 0
        for other_player in game_state['players']:
            if other_player.position > player.position:
                ahead_count += 1
        position = ahead_count + 1
        position_suffix = 'st' if position == 1 else 'nd' if position == 2 else 'rd' if position == 3 else 'th'
        return f"{position_suffix} Position"

def display_player_timers(game_state, screen, x, y_start, spacing, players, player_colours):
    """Display timers and position text for all players."""
    # Only display timers if the setting is enabled
    if not game_state.get('show_timers', True):
        return
        
    timer_font = pygame.font.SysFont(None, int(18 * scale))
    position_font = pygame.font.SysFont(None, int(16 * scale))
    current_time = time.time()
    
    # Sort players by position (finished first, then by board position)
    # Use try/except to handle cases where a player might not be in finish_order yet
    def sort_key(p):
        if p.finished:
            try:
                return (-1, -game_state['finish_order'].index(p))
            except ValueError:
                # If player is finished but not in finish_order (shouldn't happen), 
                # place them at the end of finished players
                return (-1, 0)
        else:
            return (0, -p.position)
            
    sorted_players = sorted(players, key=sort_key)
    
    for i, player in enumerate(sorted_players):
        y = y_start + i * spacing
        
        # Draw player color indicator
        player_color = player_colours[player.colour_index]
        pygame.draw.rect(screen, player_color, (x - 20, y, 15, 15))
        pygame.draw.rect(screen, BLACK, (x - 20, y, 15, 15), 1)  # Border
        
        # Calculate player's elapsed time
        if player.finished and player.elapsed_time is not None:
            elapsed = player.elapsed_time
        else:
            elapsed = current_time - player.start_time
        
        # Draw timer text with shadow
        timer_text = timer_font.render(f"Time: {format_time(elapsed)}", True, BLACK)
        shadow_offset = 1
        shadow = timer_font.render(f"Time: {format_time(elapsed)}", True, (100, 100, 100))
        
        # Draw position text
        position_text = position_font.render(get_player_position_text(player, game_state), True, player_color)
        position_shadow = position_font.render(get_player_position_text(player, game_state), True, (100, 100, 100))
        
        # Draw shadows then text
        screen.blit(shadow, (x + shadow_offset, y + shadow_offset))
        screen.blit(timer_text, (x, y))
        screen.blit(position_shadow, (x + shadow_offset, y + 20 + shadow_offset))
        screen.blit(position_text, (x, y + 20))

def render_coloured_message(screen, font, message, x, y, offset_x, offset_y, players, player_colours):
    # Render a message with player-colored text
    parts = message.split('Player ')
    current_x = x
    if parts[0]:
        text = font.render(parts[0], True, BLACK)
        screen.blit(text, (current_x, y))
        current_x += text.get_width()
    
    for i, part in enumerate(parts[1:], 1):
        if ' ' in part:
            player_number, rest = part.split(' ', 1)
            try:
                player_idx = int(player_number) - 1
                if 0 <= player_idx < len(players):
                    text = font.render(f"Player {player_number}", True, player_colours[players[player_idx].colour_index])
                    screen.blit(text, (current_x, y))
                    current_x += text.get_width()
                    
                    text = font.render(f" {rest}", True, BLACK)
                    screen.blit(text, (current_x, y))
                    current_x += text.get_width()
                else:
                    text = font.render(f"Player {player_number} {rest}", True, BLACK)
                    screen.blit(text, (current_x, y))
                    current_x += text.get_width()
            except ValueError:
                text = font.render(f"Player {part}", True, BLACK)
                screen.blit(text, (current_x, y))
                current_x += text.get_width()
        else:
            text = font.render(f"Player {part}", True, BLACK)
            screen.blit(text, (current_x, y))
            current_x += text.get_width()

def render_wrapped_text(screen, font, text, max_width, x, y, color=BLACK, line_spacing=5, return_height_only=False):
    """
    Renders text wrapped to fit within max_width.
    Returns the total height of rendered text.
    If return_height_only is True, calculates height without rendering text to screen.
    """
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        # Try adding this word to the current line
        test_line = ' '.join(current_line + [word])
        test_width = font.size(test_line)[0]
        
        if test_width <= max_width:
            # Word fits, add it to the current line
            current_line.append(word)
        else:
            # Word doesn't fit, start a new line
            if current_line:  # Only add the current line if it's not empty
                lines.append(' '.join(current_line))
            current_line = [word]
    
    # Add the last line if it's not empty
    if current_line:
        lines.append(' '.join(current_line))
    
    # Calculate total height
    total_height = 0
    
    # Render each line (or just calculate height if return_height_only is True)
    for i, line in enumerate(lines):
        rendered_text = font.render(line, True, color)
        if not return_height_only:
            screen.blit(rendered_text, (x, y + total_height))
        total_height += rendered_text.get_height() + line_spacing
    
    return total_height - line_spacing if lines else 0  # Subtract the last line_spacing

def draw_board(players, game_state, scale, offset_x, offset_y, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, bonus_result_images_scaled):
    """Draw the game board and all its elements with card-flipping animations for button and squish for squares."""
    # Use dull pink background for Expert board, gray for Classic
    if game_state.get('selected_board') == 'Expert':
        screen.fill(DULL_PINK)
    elif game_state.get('selected_board') == 'Secret':
        # Use a dark green background for the Secret board
        screen.fill((0, 100, 0))  # Dark green
        
        # For Secret board, draw arrow connections between spaces to show direction
        # This ensures they appear underneath the tiles
        if len(squares_coords) > 1:  # Make sure we have coordinates to work with
            arrow_color = (255, 255, 255)  # White arrows
            
            # Draw arrows connecting each space to the next
            for i in range(len(squares_coords) - 1):
                x1 = int(squares_coords[i][0] * scale + offset_x)
                y1 = int(squares_coords[i][1] * scale + offset_y)
                x2 = int(squares_coords[i+1][0] * scale + offset_x)
                y2 = int(squares_coords[i+1][1] * scale + offset_y)
                
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
            
        x = int(squares_coords[i][0] * scale + offset_x)
        y = int(squares_coords[i][1] * scale + offset_y)

        # No need for special handling of '1' spaces in Expert mode anymore
        # since the squares array now has the correct layout for each board
        display_square = square
        
        # Determine the correct image for '1' and '-2' based on position
        if display_square in ['Go', 'B', 'Q', 'J', '0', 'P', 'F', 'FP']:
            img = tile_images_scaled[display_square]
            
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
                    img = tile_images_scaled['1_East']
                # Right column (south direction) - indices 16-22
                elif 16 <= i <= 22:
                    img = tile_images_scaled['1_South']
                # Bottom rows going west - west path or south path west segments
                elif (23 <= i <= 27) or (i >= 29 and i <= 37) or (i >= 52 and i <= 66):
                    img = tile_images_scaled['1_West']
                # Vertical segments going north - end of paths
                elif (i >= 38 and i <= 48) or (i >= 67 and i <= 77):
                    img = tile_images_scaled['1_North']
                # Default east direction for any other segments
                else:
                    img = tile_images_scaled['1_East']
            else:
                # Original classic board logic
                if i in [1, 6]:
                    img = tile_images_scaled['1_East']
                elif i in [12, 14]:
                    img = tile_images_scaled['1_North']
                elif i == 24:
                    img = tile_images_scaled['1_West']
                elif i == 31:
                    img = tile_images_scaled['1_West']
                else:
                    img = tile_images_scaled['1_East']
        elif display_square == '-2':
            # Check if we're on the expert board
            if game_state.get('selected_board') == 'Expert':
                # First row (east direction) - should point west (opposite)
                if 1 <= i <= 15:
                    img = tile_images_scaled['-2_West']
                # Right column (south direction) - should point north (opposite)
                elif 16 <= i <= 22:
                    img = tile_images_scaled['-2_North']
                # Bottom rows going west - should point east (opposite)
                elif (23 <= i <= 27) or (i >= 29 and i <= 37) or (i >= 52 and i <= 66):
                    img = tile_images_scaled['-2_East']
                # Vertical segments going north - should point south (opposite)
                elif (i >= 38 and i <= 48) or (i >= 67 and i <= 77):
                    img = tile_images_scaled['-2_South']
                # Default west direction for any other segments (opposite of east)
                else:
                    img = tile_images_scaled['-2_West']
            else:
                # Original classic board logic
                if i == 4:
                    img = tile_images_scaled['-2_West']
                elif i in [13, 15]:
                    img = tile_images_scaled['-2_South']
                elif i == 19:
                    img = tile_images_scaled['-2_East']
                elif i in [28, 33, 35]:
                    img = tile_images_scaled['-2_North']
                else:
                    img = tile_images_scaled['-2_West']

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
                    radius = 30 * scale * (0.8 + 0.2 * pulse)  # Pulsing radius
                    
                    # Calculate position on the circle
                    car_x = x + radius * math.cos(angle)
                    car_y = y + radius * math.sin(angle)
                    
                    # Draw a car emoji (using a small yellow circle as placeholder)
                    car_size = int(20 * scale * (0.8 + 0.2 * pulse))  # Increased from 15 to 20 for bigger circles
                    car_surface = pygame.Surface((car_size, car_size), pygame.SRCALPHA)
                    # Increased opacity from 200 to 240 for more visibility
                    pygame.draw.circle(car_surface, (255, 255, 0, 240), (car_size//2, car_size//2), car_size//2)
                    
                    # Draw black outline with higher opacity
                    pygame.draw.circle(car_surface, (0, 0, 0, 240), (car_size//2, car_size//2), car_size//2, 2)
                    
                    # Blit to the screen
                    screen.blit(car_surface, (car_x - car_size//2, car_y - car_size//2))

    # Draw jail with pulsing squish animation during restart
    jail_x = int(JAIL_POS[0] * scale + offset_x)
    jail_y = int(JAIL_POS[1] * scale + offset_y)
    jail_img = tile_images_scaled['Jail']
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

    # Create a dictionary to track occupied positions and how many players are at each position
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
                    x = int(player.jail_x * scale + offset_x)
                    y = int(player.jail_y * scale + offset_y)
                else:
                    # Generate random position if somehow not set
                    jail_offset_x = random.randint(-int(JAIL_SIZE/3 * scale), int(JAIL_SIZE/3 * scale))
                    jail_offset_y = random.randint(-int(JAIL_SIZE/3 * scale), int(JAIL_SIZE/3 * scale))
                    x = jail_x + jail_offset_x
                    y = jail_y + jail_offset_y
                    # Store for consistency
                    player.jail_x = (x - offset_x) / scale
                    player.jail_y = (y - offset_y) / scale
            else:
                # Get base coordinates for the player
                x = int(player.current_x * scale + offset_x)
                y = int(player.current_y * scale + offset_y)
                
                # Special handling for GO square (position 0) to ensure player is centered
                if player.position == 0:
                    # Get the GO tile image to find its dimensions
                    go_img = tile_images_scaled['Go']
                    # Calculate the exact center of the GO tile
                    x = int(squares_coords[0][0] * scale + offset_x)
                    y = int(squares_coords[0][1] * scale + offset_y)
                
                # Apply offset if there are multiple players at this position
                if len(players_at_position) > 1:
                    # Calculate offset based on index
                    # First player stays centered, subsequent players get offset in a spiral pattern
                    if idx > 0:
                        # Offset amount (proportional to scale)
                        offset_amount = int(10 * scale)
                        
                        # Simple pattern: down and right for 2nd player, other directions for more players
                        if idx == 1:
                            x += offset_amount
                            y += offset_amount
                        elif idx == 2:
                            x -= offset_amount
                            y += offset_amount
                        elif idx == 3:
                            x -= offset_amount
                            y -= offset_amount
                        else:
                            # For more than 4 players, increase offset slightly for each additional player
                            angle = 2 * math.pi * (idx / 4)
                            distance = offset_amount * (1 + (idx // 4) * 0.5)
                            x += int(math.cos(angle) * distance)
                            y += int(math.sin(angle) * distance)
            
            if player.is_computer:
                # Use the correct CPU image based on difficulty level
                if player.difficulty in cpu_difficulty_images_scaled:
                    img = cpu_difficulty_images_scaled[player.difficulty]
                else:
                    # Fallback to normal difficulty if not recognized
                    img = cpu_difficulty_images_scaled['normal']
            else:
                img = player_images_scaled[player.colour_index]
            
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

    # Draw dice - single die for classic board, two dice for expert
    die_pos_x, die_pos_y = DIE_POS
    
    # For Secret board, use custom die position to avoid overlapping tiles
    if game_state.get('selected_board') == 'Secret':
        if 'die_pos' in game_state:
            die_pos_x, die_pos_y = game_state['die_pos']
    
    dice_rect = pygame.Rect(int(die_pos_x * scale + offset_x), int(die_pos_y * scale + offset_y), int(50 * scale), int(50 * scale))
    
    # For expert board, define second die position and total text position
    is_expert_board = game_state.get('selected_board') == 'Expert'
    if is_expert_board:
        dice_rect1 = pygame.Rect(int((die_pos_x - 35) * scale + offset_x), int(die_pos_y * scale + offset_y), int(50 * scale), int(50 * scale))
        dice_rect2 = pygame.Rect(int((die_pos_x + 35) * scale + offset_x), int(die_pos_y * scale + offset_y), int(50 * scale), int(50 * scale))
        total_text_pos = (int(die_pos_x * scale + offset_x), int((die_pos_y + 60) * scale + offset_y))  # Moved further down to avoid collision
    
    if game_state.get('rolling_dice', False):
        if time.time() - game_state['dice_start_time'] < 1:
            # Animation phase
            if is_expert_board:
                # For expert board, show two random dice during animation
                for _ in range(2):  # Show multiple dice during animation
                    dice_face = random.choice(dice_images_scaled)
                    rand_x = int(random.randint(100, ORIGINAL_WIDTH - 100) * scale + offset_x)
                    rand_y = int(random.randint(100, ORIGINAL_HEIGHT - 100) * scale + offset_y)
                    screen.blit(dice_face, (rand_x, rand_y))
            else:
                # Classic board - single die
                dice_face = random.choice(dice_images_scaled)
                rand_x = int(random.randint(100, ORIGINAL_WIDTH - 100) * scale + offset_x)
                rand_y = int(random.randint(100, ORIGINAL_HEIGHT - 100) * scale + offset_y)
                screen.blit(dice_face, (rand_x, rand_y))
        else:
            # End of animation, show final dice values
            roll = game_state['dice_roll']
            if is_expert_board:
                # Expert board - display both dice and total
                roll1 = game_state['dice_roll_1']
                roll2 = game_state['dice_roll_2']
                
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
                dice_face = dice_images_scaled[roll - 1]
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
            dice_face = dice_images_scaled[roll - 1]
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
                        head_shake_cpu_sound.play()
                    else:
                        head_shake_sound.play()
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
                        head_shake_cpu_sound.play()
                    else:
                        head_shake_sound.play()
                    current_player.active_animations.append(anim)
                    current_player.turn_ended = True
                else:
                    bonk_sound.play()
                    game_state['message'] = f"Player {current_player.id + 1} rolled {roll} (odd). Still in jail."
                    current_player.turn_ended = True
            else:
                if isinstance(next_positions[current_player.position], list):
                    game_state['show_path_choice_after_roll'] = True
                    game_state['roll_for_path_choice'] = roll
                    game_state['spaces_remaining'] = roll  # Set remaining spaces to full roll
                    game_state['message'] = f"Player {current_player.id + 1} rolled {roll}. Choose a path."
                else:
                    movement_path = get_movement_path(current_player.position, roll, game_state)
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

    # Draw path choice if active
    if game_state.get('show_path_choice_after_roll', False):
        current_player = players[game_state['current_player']]
        current_pos = current_player.position
        choices = next_positions[current_pos]
        remaining_spaces = game_state.get('spaces_remaining', 0)
        
        # Show ghost players at potential end positions
        for choice in choices:
            # Calculate the full path for this choice including all remaining moves
            full_path = get_movement_path_with_choice(current_pos, choice, remaining_spaces)
            ending_pos = full_path[-1]
            
            # Draw a ghost player at the ending position
            x, y = squares_coords[ending_pos]
            x = int(x * scale + offset_x)
            y = int(y * scale + offset_y)
            
            # Draw a special marker for the end position
            pygame.draw.circle(screen, (255, 255, 0), (x, y), int(20 * scale), 3)
            
            # Draw the ghost player
            img = player_images_scaled[current_player.colour_index]
            img_copy = img.copy()
            img_copy.set_alpha(150)  # Increased transparency for better visibility
            screen.blit(img_copy, (x - img_copy.get_width() // 2, y - img_copy.get_height() // 2))
        
        # Draw path choice dialog centered on die position
        die_center_x = int(DIE_POS[0] * scale + offset_x)
        die_center_y = int(DIE_POS[1] * scale + offset_y)
        dialog_width = int(300 * scale)
        dialog_height = int(180 * scale)
        rect = pygame.Rect(die_center_x - dialog_width // 2, die_center_y - dialog_height // 2, dialog_width, dialog_height)
        
        # Draw dialog background with border
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, (0, 0, 100), rect, 3)  # Dark blue border
        
        # Draw title with shadow
        title_shadow = font.render(f"Choose Your Path!", True, (100, 100, 100))
        screen.blit(title_shadow, (rect.x + int(12 * scale), rect.y + int(12 * scale)))
        
        title = font.render(f"Choose Your Path!", True, (0, 0, 150))  # Dark blue text
        screen.blit(title, (rect.x + int(10 * scale), rect.y + int(10 * scale)))
        
        # Draw remaining spaces info
        spaces_text = font.render(f"Remaining Spaces: {remaining_spaces}", True, (100, 0, 0))  # Red text for visibility
        screen.blit(spaces_text, (rect.x + int(10 * scale), rect.y + int(40 * scale)))
        
        labels = ["North", "West"]
        button_height = int(35 * scale)
        button_spacing = int(15 * scale)
        
        game_state['path_buttons'] = []
        
        for i, (label, choice) in enumerate(zip(labels, choices)):
            full_path = get_movement_path_with_choice(current_pos, choice, remaining_spaces)
            ending_pos = full_path[-1]
            end_square_type = squares[ending_pos]
            
            # Create a more detailed button
            button = pygame.Rect(
                rect.x + int(20 * scale),
                rect.y + int(80 * scale) + i * (button_height + button_spacing),
                int(260 * scale),
                button_height
            )
            
            # Draw button with gradient effect
            button_color = (200, 230, 255) if i == 0 else (255, 230, 200)
            
            # Add splash effect for path choice buttons
            if 'clicked_path_button' in game_state and game_state['clicked_path_button'] == i:
                # Get elapsed time since click
                current_time = time.time()
                click_elapsed = current_time - game_state['path_button_click_time']
                if click_elapsed < 0.3:  # Show splash effect for 0.3 seconds
                    # Change color for pressed effect
                    button_color = (180, 210, 235) if i == 0 else (235, 210, 180)  # Slightly darker for pressed effect
                else:
                    # Remove click effect after time elapsed
                    del game_state['clicked_path_button']
                    del game_state['path_button_click_time']
            
            pygame.draw.rect(screen, button_color, button)
            pygame.draw.rect(screen, (0, 0, 100), button, 2)  # Dark blue border
            
            # Draw button text with destination info
            direction_text = font.render(f"{label} Path", True, BLACK)
            screen.blit(direction_text, (button.x + int(10 * scale), button.y + int(5 * scale)))
            
            dest_text = font.render(f"Ends on: {end_square_type}", True, (100, 0, 0))
            screen.blit(dest_text, (button.x + int(130 * scale), button.y + int(5 * scale)))
            
            game_state['path_buttons'].append((button, choice))

    # Reset button with hold progress and spinning animation during restart
    restart_button_size = int(50 * scale)
    restart_button_rect = pygame.Rect(int(650 * scale + offset_x), int(540 * scale + offset_y), restart_button_size, restart_button_size)
    
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
    
    # Settings button to the right of restart button
    settings_button_size = int(50 * scale)
    settings_button_rect = pygame.Rect(int(710 * scale + offset_x), int(540 * scale + offset_y), settings_button_size, settings_button_size)
    screen.blit(settings_button_scaled, settings_button_rect.topleft)
    
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

    # Draw bonus image
    if 'bonus_image_key' in game_state and 'bonus_image_state' in game_state:
        image = bonus_result_images_scaled[game_state['bonus_image_key']]
        state = game_state['bonus_image_state']
        die_center_x = int(DIE_POS[0] * scale + offset_x)  # Die center X
        die_center_y = int(DIE_POS[1] * scale + offset_y)  # Die center Y
        
        if state == 'growing':
            elapsed = time.time() - game_state['bonus_grow_start']
            scale_factor = min(1.0, elapsed / 1.0)  # Grows over 1 second
            scaled_width = int(image.get_width() * scale_factor)
            scaled_height = int(image.get_height() * scale_factor)
            scaled_image = pygame.transform.smoothscale(image, (scaled_width, scaled_height))
            rect = scaled_image.get_rect(center=(die_center_x, die_center_y))
            screen.blit(scaled_image, rect.topleft)
        elif state == 'showing':
            # Full size, centered on die position
            rect = image.get_rect(center=(die_center_x, die_center_y))
            screen.blit(image, rect.topleft)
        elif state == 'shrinking':
            elapsed = time.time() - game_state['bonus_shrink_start']
            scale_factor = max(0.0, 1.0 - elapsed / 1.0)  # Shrinks over 1 second
            scaled_width = int(image.get_width() * scale_factor)
            scaled_height = int(image.get_height() * scale_factor)
            scaled_image = pygame.transform.smoothscale(image, (scaled_width, scaled_height))
            rect = scaled_image.get_rect(center=(die_center_x, die_center_y))
            screen.blit(scaled_image, rect.topleft)

    # Draw quiz last to ensure it's always on top
    if game_state.get('show_quiz', False) and game_state.get('quiz_question'):
        current_time = time.time()
        elapsed = current_time - game_state['quiz_start_time']
        die_center_x = int(DIE_POS[0] * scale + offset_x)  # Die center X
        die_center_y = int(DIE_POS[1] * scale + offset_y)  # Die center Y
        # Update quiz dimensions to match bonus cards with 4:3 aspect ratio
        quiz_width = int(280 * scale)  # Match bonus card width (same as in resize_assets)
        quiz_height = int(quiz_width * 3 / 4)  # 4:3 aspect ratio to match bonus cards

        if game_state['quiz_state'] == 'growing':
            scale_factor = min(1.0, elapsed / 1.0)
            width = int(quiz_width * scale_factor)
            height = int(quiz_height * scale_factor)
            rect = pygame.Rect(die_center_x - width // 2, die_center_y - height // 2, width, height)
            pygame.draw.rect(screen, WHITE, rect)
            
            # For growing state, we can optionally show the question with scaling
            if scale_factor > 0.5 and 'quiz_question' in game_state:  # Only show text once the card is half-size
                question = game_state['quiz_question'][0]
                text_margin = int(10 * scale * scale_factor)
                max_text_width = width - 2 * text_margin
                # Use alpha to fade in text as the card grows
                alpha_factor = min(1.0, (scale_factor - 0.5) * 2)  # 0 at 0.5 scale, 1.0 at 1.0 scale
                render_wrapped_text(screen, font, question, max_text_width, 
                                   rect.x + text_margin, rect.y + text_margin, 
                                   BLACK)
                
            if elapsed >= 1.0:
                game_state['quiz_state'] = 'waiting'
                game_state['quiz_timer'] = current_time + 1.0
        elif game_state['quiz_state'] == 'waiting':
            rect = pygame.Rect(die_center_x - quiz_width // 2, die_center_y - quiz_height // 2, quiz_width, quiz_height)
            pygame.draw.rect(screen, WHITE, rect)
            question, options, _ = game_state['quiz_question']
            
            # Render wrapped question text
            text_margin = int(10 * scale)
            max_text_width = quiz_width - 2 * text_margin
            render_wrapped_text(screen, font, question, max_text_width, 
                               rect.x + text_margin, rect.y + text_margin)
                
            if current_time >= game_state['quiz_timer']:
                game_state['quiz_state'] = 'buttons'
                game_state['pop_played'] = False
        elif game_state['quiz_state'] == 'buttons':
            if not game_state['pop_played']:
                pop_sound.play()
                game_state['pop_played'] = True
            rect = pygame.Rect(die_center_x - quiz_width // 2, die_center_y - quiz_height // 2, quiz_width, quiz_height)
            pygame.draw.rect(screen, WHITE, rect)
            question, options, _ = game_state['quiz_question']
            
            # Render wrapped question text
            text_margin = int(10 * scale)
            max_text_width = quiz_width - 2 * text_margin
            question_height = render_wrapped_text(screen, font, question, max_text_width, 
                                                rect.x + text_margin, rect.y + text_margin)
            
            # Position buttons based on question height
            quiz_buttons = []
            min_button_height = int(25 * scale)  # Minimum button height
            button_spacing = int(5 * scale)
            button_start_y = rect.y + text_margin + question_height + button_spacing
            current_y = button_start_y
            
            # Calculate button positions with adequate spacing and adjust height based on text content
            for i, option in enumerate(options):
                option_margin = int(5 * scale)
                max_option_width = quiz_width - 2 * text_margin - 2 * option_margin
                
                # Check if text is long to determine if we need a smaller font
                # Create a temporary surface to calculate text height without rendering
                option_length = len(option)
                
                # Use smaller font for longer text
                if option_length > 80:  # Very long text
                    option_font = pygame.font.SysFont(None, int(14 * scale))
                elif option_length > 50:  # Moderately long text
                    option_font = pygame.font.SysFont(None, int(16 * scale))
                else:  # Normal text
                    option_font = font
                
                # Pre-calculate text height using render_wrapped_text but without actually rendering
                # (using a temporary surface that won't be displayed)
                temp_surface = pygame.Surface((1, 1), pygame.SRCALPHA)  # Tiny temporary surface
                text_height = render_wrapped_text(temp_surface, option_font, option, max_option_width, 0, 0, WHITE, return_height_only=True)
                
                # Set button height based on text height, with a minimum
                button_height = max(min_button_height, text_height + 2 * option_margin)
                
                button = pygame.Rect(
                    rect.x + text_margin,
                    current_y,
                    quiz_width - 2 * text_margin,
                    button_height
                )
                current_y += button_height + button_spacing  # Update Y position for next button
                
                # Check if this button is currently being clicked (splash effect)
                button_color = BLUE
                if 'clicked_quiz_button' in game_state and game_state['clicked_quiz_button'] == i:
                    # Get elapsed time since click
                    click_elapsed = current_time - game_state['button_click_time']
                    if click_elapsed < 0.3:  # Show splash effect for 0.3 seconds
                        # Change color for splash effect
                        button_color = (100, 100, 200)  # Lighter blue for pressed effect
                    else:
                        # Remove click effect after time elapsed
                        del game_state['clicked_quiz_button']
                        del game_state['button_click_time']
                
                pygame.draw.rect(screen, button_color, button)
                
                # Add number indicator for keyboard shortcuts (1, 2, 3, etc.)
                number_text = f"{i+1}."  # i+1 to convert from 0-based to 1-based
                number_surface = option_font.render(number_text, True, YELLOW)
                number_rect = number_surface.get_rect()
                number_rect.left = button.x + option_margin
                number_rect.top = button.y + option_margin
                screen.blit(number_surface, number_rect)
                
                # Add padding to the button text to avoid overlapping with the number indicator
                option_text_x = button.x + option_margin + number_surface.get_width() + 5
                render_wrapped_text(screen, option_font, option, max_option_width - number_surface.get_width() - 5, 
                                   option_text_x, button.y + option_margin, WHITE)
                
                quiz_buttons.append((button, i))
            game_state['quiz_buttons'] = quiz_buttons
        elif game_state['quiz_state'] == 'answered':
            rect = pygame.Rect(die_center_x - quiz_width // 2, die_center_y - quiz_height // 2, quiz_width, quiz_height)
            pygame.draw.rect(screen, WHITE, rect)
            question, _, _ = game_state['quiz_question']
            
            # Render wrapped question text
            text_margin = int(10 * scale)
            max_text_width = quiz_width - 2 * text_margin
            render_wrapped_text(screen, font, question, max_text_width, 
                               rect.x + text_margin, rect.y + text_margin)
                
            if current_time - game_state['quiz_answer_delay_start'] >= 1.0:
                game_state['quiz_state'] = 'shrinking'
                game_state['quiz_shrink_start'] = current_time
                disconnect_sound.play()
        elif game_state['quiz_state'] == 'shrinking':
            elapsed = current_time - game_state['quiz_shrink_start']
            scale_factor = max(0.0, 1.0 - elapsed / 1.0)
            width = int(quiz_width * scale_factor)
            height = int(quiz_height * scale_factor)
            rect = pygame.Rect(die_center_x - width // 2, die_center_y - height // 2, width, height)
            pygame.draw.rect(screen, WHITE, rect)
            
            # Show fading text during shrinking
            if scale_factor > 0.5 and 'quiz_question' in game_state:
                question = game_state['quiz_question'][0]
                text_margin = int(10 * scale * scale_factor)
                max_text_width = width - 2 * text_margin
                # Use alpha to fade out text as the card shrinks
                render_wrapped_text(screen, font, question, max_text_width, 
                                   rect.x + text_margin, rect.y + text_margin, 
                                   BLACK)
                
            if elapsed >= 1.0:
                game_state['show_quiz'] = False
                del game_state['quiz_question']
                del game_state['quiz_shrink_start']
                if 'quiz_answer_delay_start' in game_state:
                    del game_state['quiz_answer_delay_start']

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
    return dice_rect, restart_button_rect, settings_button_rect, quiz_answer_rects if game_state.get('quiz_buttons') else []

def toggle_player_state(index, player_states, difficulties):
    """Toggle a player's state between not set, human, or CPU."""
    player_states[index] = (player_states[index] + 1) % 3
    if player_states[index] == 0:
        pong_sound.play()
        difficulties[index] = None
    elif player_states[index] == 1:
        whit_sound.play()
        difficulties[index] = None
    elif player_states[index] == 2:
        difficulties[index] = 'normal'
        voltage_normal_sound.play()

def cycle_difficulty(index, difficulties):
    """Cycle through CPU difficulty levels."""
    if difficulties[index] == 'easy':
        difficulties[index] = 'normal'
        voltage_normal_sound.play()
    elif difficulties[index] == 'normal':
        difficulties[index] = 'hard'
        voltage_hard_sound.play()
    elif difficulties[index] == 'hard':
        difficulties[index] = 'easy'
        voltage_easy_sound.play()

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button == 1:  # Left click
                    # Check for board selection only if unlocked
                    if show_board_selection and len(board_names) > 1:
                        for i, rect in enumerate(board_selector_rects):
                            if rect.collidepoint(pos):
                                selected_board = i
                                connect_sound.play()  # Play a sound when board is selected
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
                            
                if start_button_rect.collidepoint(pos) and any(state > 0 for state in player_states):
                    selected_players = []
                    for i, state in enumerate(player_states):
                        if state == 1:
                            selected_players.append((i, False, None))
                        elif state == 2:
                            selected_players.append((i, True, difficulties[i]))
                    super_mario_sound.play()
                    return selected_players, board_names[selected_board]
            elif event.type == pygame.KEYDOWN:
                if event.key >= pygame.K_1 and event.key <= pygame.K_6:
                    index = event.key - pygame.K_1
                    if index < len(player_states):
                        toggle_player_state(index, player_states, difficulties)
                # Board selection with arrow keys (only if unlocked)
                elif event.key == pygame.K_LEFT and show_board_selection and len(board_names) > 1:
                    selected_board = max(0, selected_board - 1)  # Move left, with minimum 0
                    connect_sound.play()
                elif event.key == pygame.K_RIGHT and show_board_selection and len(board_names) > 1:
                    selected_board = min(len(board_names) - 1, selected_board + 1)  # Move right, with maximum at last board
                    connect_sound.play()
                elif event.key == pygame.K_SPACE and any(state > 0 for state in player_states):
                    # Space bar acts like clicking the start button, but only when it's active
                    selected_players = []
                    for i, state in enumerate(player_states):
                        if state == 1:
                            selected_players.append((i, False, None))
                        elif state == 2:
                            selected_players.append((i, True, difficulties[i]))
                    super_mario_sound.play()
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
                # Make the buttons slightly wider instead of using arrow indicators
                # (Removing arrows that were causing display issues)

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

        pygame.display.flip()

def resize_assets(scale, board_type='Classic'):
    """Resize all game assets based on screen scale while maintaining aspect ratios where necessary."""
    global player_images_scaled, cpu_image_scaled, bonus_result_images_scaled, cpu_difficulty_images_scaled
    global dice_images_scaled, tile_images_scaled, restart_button_scaled
    global bonus_images_scaled, settings_button_scaled, board_image_scaled
    
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
    
    # Scale bonus images with a slightly larger size
    target_width = int(280 * scale)  # Increased from 250 to 280
    target_height = int(target_width * 3 / 4)  # Height preserves 4:3 ratio
    bonus_result_images_scaled = {
        key: pygame.transform.smoothscale(img, (target_width, target_height))
        for key, img in bonus_result_images_original.items()
    }
    
    return tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, bonus_result_images_scaled

def main():
    """Main game loop and initialization."""
    global SCREEN_WIDTH, SCREEN_HEIGHT, scale, offset_x, offset_y, screen, font, quiz_card_index, bonus_card_index, expert_quiz_card_index
    scale = 1.0
    offset_x = 0
    offset_y = 0
    connect_sound.play()
    
    # Create a list of all sounds in the game for easy volume control
    all_game_sounds = [
        # Regular sounds
        roll_sound, glug_sound, bonk_sound, head_shake_sound, whiz_sound, drip_drop_sound, 
        drum_machine_sound, win_sound, pop_sound, bing_bong_sound, connect_sound, 
        disconnect_sound, indigogo_sound, jump_sound, mac_os_dinbg_sound, mac_os_uh_ohh_sound, 
        super_mario_sound, wobble_sound, fairlin_round1_sound, pong_sound, voltage_easy_sound, 
        voltage_normal_sound, voltage_hard_sound, whit_sound, restart_sound, car_horn_sound,
        # CPU-specific sounds
        bonk_cpu_sound, glug_cpu_sound, head_shake_cpu_sound, jump_cpu_sound, whiz_cpu_sound, wobble_cpu_sound
    ]
    
    # Function to apply master volume to all sounds
    def apply_master_volume(volume):
        for sound in all_game_sounds:
            sound.set_volume(volume)
    
    # Set default volume for all sounds (will be overridden by settings)
    default_volume = 1.0
    apply_master_volume(default_volume)

    quit_game = False
    while not quit_game:
        selected_data = select_players()
        if selected_data is None:
            break

        selected_players, selected_board = selected_data
        logger.info(f"Selected board type: {selected_board}")
        
        # Load saved game progress and settings
        saved_progress = load_game_progress()
        
        players = [Player(i, colour_idx, is_computer, difficulty) for i, (colour_idx, is_computer, difficulty) in enumerate(selected_players)]
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
        apply_master_volume(game_state['master_volume'])
        clock = pygame.time.Clock()

        tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, bonus_result_images_scaled = resize_assets(scale, selected_board)

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
                    tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, bonus_result_images_scaled = resize_assets(scale, game_state['selected_board'])
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
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    restart_button_rect = pygame.Rect(int(650 * scale + offset_x), int(540 * scale + offset_y), int(50 * scale), int(50 * scale))
                    if restart_button_rect.collidepoint(pos):
                        game_state['restart_hold_start'] = time.time()
                    
                    # Handle settings button click
                    settings_button_rect = pygame.Rect(int(710 * scale + offset_x), int(540 * scale + offset_y), int(50 * scale), int(50 * scale))
                    if settings_button_rect.collidepoint(pos):
                        # Toggle settings menu
                        game_state['show_settings_menu'] = not game_state.get('show_settings_menu', False)
                    
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
                            connect_sound.play()
                        
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
                            apply_master_volume(volume)
                        
                        # Handle Reset to Default button
                        if 'reset_button_rect' in game_state and game_state['reset_button_rect'].collidepoint(pos):
                            # Reset all settings to default values
                            game_state['master_volume'] = 1.0  # 100% volume
                            game_state['show_game_status'] = False  # Game status off
                            game_state['use_modern_status_display'] = True  # Modern status display on
                            game_state['show_timers'] = False  # Show timers off by default
                            
                            # Apply the volume setting
                            apply_master_volume(game_state['master_volume'])
                            
                            # Play a sound to indicate reset
                            restart_sound.play()
                                
                        # Close menu if clicking outside of menu and settings button
                        if not menu_rect.collidepoint(pos) and not settings_button_rect.collidepoint(pos):
                            game_state['show_settings_menu'] = False
                            game_state['volume_drag_active'] = False
                    
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
                                movement_path = get_movement_path_with_choice(current_player.position, choice, remaining_spaces, started_on_choice)
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
                                indigogo_sound.play()
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
                        restart_sound.play()
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
                        apply_master_volume(volume)

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
                    if current_time - game_state['bonus_image_start'] >= 0.8:  # Increased from 0.5 to 0.8
                        game_state['bonus_image_state'] = 'growing'
                        game_state['bonus_grow_start'] = current_time
                elif game_state['bonus_image_state'] == 'growing':
                    elapsed = current_time - game_state['bonus_grow_start']
                    if elapsed >= 1.0:
                        game_state['bonus_image_state'] = 'showing'
                        # Start the bonus action
                        player = players[game_state['current_player']]
                        effect = game_state['bonus_action']
                        
                        # Add a 2-second timer for bonus card to close after action is started
                        game_state['bonus_action_start_time'] = current_time
                        
                        if effect[0] == "move_forward":
                            num = effect[1]
                            movement_path = get_movement_path(player.position, num, game_state)
                            anim = {
                                'player': player,
                                'path': movement_path,
                                'index': 0,
                                'last_time': time.time(),
                                'message': f"Player {player.id + 1} moving forward {num} spaces from bonus card.",
                                'is_initial_move': False,
                                'delay': 0.8  # Increased from 0.5 to 0.8
                            }
                            player.active_animations.append(anim)
                        elif effect[0] == "move_back":
                            num = effect[1]
                            if player.position > 0:
                                # Calculate target position (at most back to start)
                                target_pos = max(0, player.position - num)
                                # Create movement path
                                movement_path = [player.position]
                                
                                # If position is num or greater, go back num spaces
                                if player.position >= num:
                                    for i in range(1, num + 1):
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
                                    'message': f"Player {player.id + 1} moving back {num} spaces from bonus card.",
                                    'is_backwards': True,
                                    'delay': 0.8  # Increased from 0.5 to 0.8
                                }
                                player.active_animations.append(anim)
                            else:
                                game_state['message'] = f"Player {player.id + 1} can't move back from the start."
                        elif effect[0] == "go_to_jail":
                            # Set up a jail move
                            player.prev_position = player.position
                            player.jail_from_x = player.current_x
                            player.jail_from_y = player.current_y
                            player.jail_marker_anim_start = time.time()
                            
                            # Calculate random position within jail bounds
                            jail_offset_x = random.randint(-int(JAIL_SIZE/3), int(JAIL_SIZE/3))
                            jail_offset_y = random.randint(-int(JAIL_SIZE/3), int(JAIL_SIZE/3))
                            random_jail_pos = (JAIL_POS[0] + jail_offset_x, JAIL_POS[1] + jail_offset_y)
                            
                            whiz_sound.play()
                            anim = {
                                'player': player,
                                'start_pos': (player.current_x, player.current_y),
                                'end_pos': random_jail_pos,
                                'steps': 60,
                                'current_step': 0,
                                'last_time': time.time(),
                                'message': "Moving to jail.",
                                'is_jail_move': True,
                                'delay': 0.0167,  # ~60fps (1/60 second)
                                'jail_action': 'enter'
                            }
                            player.active_animations.append(anim)
                        elif effect[0] == "jail_free":
                            # Player gets a Get Out of Jail Free card
                            player.has_jail_free_card = True
                            game_state['message'] = f"Player {player.id + 1} got a Get Out of Jail Free card!"
                            # No animation needed for jail_free effect
                        elif effect[0] == "pick_quiz":
                            # Delay showing the quiz until after the bonus card animation finishes
                            game_state['pending_quiz'] = True
                elif game_state['bonus_image_state'] == 'showing':
                    player = players[game_state['current_player']]
                    
                    # Check if the 2-second timer has expired
                    if 'bonus_action_start_time' in game_state and current_time - game_state['bonus_action_start_time'] >= 2.0:
                        # Start shrinking if animations not active or if it's a quiz and the quiz is not showing
                        if (not player.active_animations or 
                            (game_state['bonus_action'][0] == "pick_quiz" and not game_state.get('show_quiz', False))):
                            game_state['bonus_image_state'] = 'shrinking'
                            game_state['bonus_shrink_start'] = current_time
                            disconnect_sound.play()
                            if 'bonus_shrink_delay' in game_state:
                                del game_state['bonus_shrink_delay']
                    # Only process the original bonus card logic if we haven't already triggered shrinking
                    elif not player.active_animations and not game_state.get('show_quiz', False):
                        # Add a delay before shrinking based on bonus action
                        if 'bonus_shrink_delay' not in game_state:
                            # If the bonus action was pick_quiz, wait 0.5 seconds after quiz closes
                            if game_state['bonus_action'][0] == "pick_quiz":
                                # If the quiz has been completed, we can shrink the bonus card
                                if game_state.get('quiz_from_bonus_completed', False):
                                    game_state['bonus_shrink_delay'] = current_time + 0.5
                                    # Clear the flag since we're handling it
                                    del game_state['quiz_from_bonus_completed']
                            else:
                                game_state['bonus_shrink_delay'] = current_time + 2.0  # Changed from 3.0 to 2.0
                        elif current_time >= game_state['bonus_shrink_delay']:
                            game_state['bonus_image_state'] = 'shrinking'
                            game_state['bonus_shrink_start'] = current_time
                            disconnect_sound.play()
                            del game_state['bonus_shrink_delay']
                elif game_state['bonus_image_state'] == 'shrinking':
                    elapsed = current_time - game_state['bonus_shrink_start']
                    if elapsed >= 1.0:
                        del game_state['bonus_image_key']
                        del game_state['bonus_image_state']
                        del game_state['bonus_action']
                        
                        # Check if there's a pending quiz from a bonus card
                        if game_state.get('pending_quiz', False):
                            # Determine which quiz deck to use based on the board type
                            if game_state.get('selected_board') == "Expert" and expert_quiz_card_index < len(expert_quiz_cards):
                                # Use expert quiz cards on the expert board
                                question, options, correct = expert_quiz_cards[expert_quiz_card_index]
                                game_state['quiz_question'] = (question, options, correct)
                                game_state['show_quiz'] = True
                                game_state['quiz_state'] = 'growing'
                                game_state['quiz_start_time'] = time.time()
                                game_state['pop_played'] = False
                                drum_machine_sound.play()
                                expert_quiz_card_index = (expert_quiz_card_index + 1) % len(expert_quiz_cards)
                                game_state['message'] = f"Player {players[game_state['current_player']].id + 1} faces an expert quiz."
                            elif quiz_card_index < len(quiz_cards):
                                # Use regular quiz cards on the classic board
                                question, options, correct = quiz_cards[quiz_card_index]
                                game_state['quiz_question'] = (question, options, correct)
                                game_state['show_quiz'] = True
                                game_state['quiz_state'] = 'growing'
                                game_state['quiz_start_time'] = time.time()
                                game_state['pop_played'] = False
                                drum_machine_sound.play()
                                quiz_card_index = (quiz_card_index + 1) % len(quiz_cards)
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
                            head_shake_cpu_sound.play()
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
                        game_state['cpu_quiz_delay'] = time.time() + 1.0  # 1 second delay
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
                        game_state['cpu_splash_delay'] = time.time() + 0.2  # 0.2 second delay to show splash
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
                            mac_os_dinbg_sound.play()
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
                            game_state['bonus_image_state'] = 'shrinking'
                            game_state['bonus_shrink_start'] = time.time()
                            
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

            dice_rect, restart_button_rect, settings_button_rect, quiz_answer_rects = draw_board(players, game_state, scale, offset_x, offset_y, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, bonus_result_images_scaled)
            
            # Display player timers and positions in the top-right corner
            timer_x = SCREEN_WIDTH - 200 * scale  # Right side of screen with padding
            timer_y_start = 30 * scale  # Start near the top
            timer_spacing = 40 * scale  # Space between each player timer
            display_player_timers(game_state, screen, timer_x, timer_y_start, timer_spacing, players, player_colours)
            
            # Check if it's time to play the jail sound
            if game_state.get('jail_sound_delay') and not game_state.get('jail_sound_played', False):
                if time.time() > game_state['jail_sound_delay']:
                    mac_os_uh_ohh_sound.play()
                    game_state['jail_sound_played'] = True
            
            pygame.display.flip()
            clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()