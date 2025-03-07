import pygame
import random
import time
import sys
import os
import traceback
import logging
import math

# Set up logging for debug purposes
logging.basicConfig(
    filename=os.path.join(os.path.abspath(os.path.dirname(__file__)), "rock_sickle.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

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
DARK_GREY = (64, 64, 64)
player_colours = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

# Load image assets - tiles, players, and all that jazz
try:
    forward_one_original = pygame.image.load(load_asset("Assets/Images/Tiles/Forward One.png"))
    back_two_original = pygame.image.load(load_asset("Assets/Images/Tiles/Back Two.png"))
    restart_button_original = pygame.image.load(load_asset("Assets/Images/Tiles/Restart.png"))
    tile_images_original = {
        'Go': pygame.image.load(load_asset("Assets/Images/Tiles/Go.png")),
        '1_East': forward_one_original,
        '1_South': pygame.transform.rotate(forward_one_original, 90),
        '1_West': pygame.transform.rotate(forward_one_original, 180),
        '1_North': pygame.transform.rotate(forward_one_original, 270),
        '-2_East': pygame.transform.rotate(back_two_original, 180),
        '-2_South': pygame.transform.rotate(back_two_original, 270),
        '-2_West': back_two_original,
        '-2_North': pygame.transform.rotate(back_two_original, 90),
        'B': pygame.image.load(load_asset("Assets/Images/Tiles/Bonus.png")),
        'Q': pygame.image.load(load_asset("Assets/Images/Tiles/Quiz.png")),
        'J': pygame.image.load(load_asset("Assets/Images/Tiles/Go To Jail.png")),
        '0': pygame.image.load(load_asset("Assets/Images/Tiles/Safe Space.png")),
        'P': pygame.image.load(load_asset("Assets/Images/Tiles/Choose Your Path.png")),
        'F': pygame.image.load(load_asset("Assets/Images/Tiles/Finish.png")),
        'Jail': pygame.image.load(load_asset("Assets/Images/Tiles/Jail Location.png")),
    }
    logger.info("Original tile images loaded successfully")
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
squares = [
    'Go', '1', '0', 'Q', '-2', 'J', '1', 'B', '0', '0',
    'J', '0', '1', '-2', '1', '-2', '0',
    'B', '0', '-2', 'Q', 'B', 'P',
    '0', '1', 'B', 'J', 'Q', '-2', '0',
    '0', '1', 'J', '-2', 'Q', '-2', '0',
    'F'
]
next_positions = list(range(1, 23)) + [[23, 30]] + list(range(24, 30)) + [37] + list(range(31, 37)) + [37] + [None]

# Define a small gap between squares (represents 1mm)
GAP_BETWEEN_TILES = 1  # Pixels representing ~1mm gap - reduced from 3 to 1

# Modified squares_coords with gaps between adjacent tiles
squares_coords = [
    (50, 50),                                  # Go - corner
    (100 + GAP_BETWEEN_TILES, 50),             # Horizontal row - top
    (150 + 2*GAP_BETWEEN_TILES, 50),
    (200 + 3*GAP_BETWEEN_TILES, 50),
    (250 + 4*GAP_BETWEEN_TILES, 50),
    (300 + 5*GAP_BETWEEN_TILES, 50),
    (350 + 6*GAP_BETWEEN_TILES, 50),
    (400 + 7*GAP_BETWEEN_TILES, 50),
    (450 + 8*GAP_BETWEEN_TILES, 50),
    (500 + 9*GAP_BETWEEN_TILES, 50),           # Corner
    
    (500 + 9*GAP_BETWEEN_TILES, 100 + GAP_BETWEEN_TILES),    # Vertical column - right
    (500 + 9*GAP_BETWEEN_TILES, 150 + 2*GAP_BETWEEN_TILES),
    (500 + 9*GAP_BETWEEN_TILES, 200 + 3*GAP_BETWEEN_TILES),
    (500 + 9*GAP_BETWEEN_TILES, 250 + 4*GAP_BETWEEN_TILES),
    (500 + 9*GAP_BETWEEN_TILES, 300 + 5*GAP_BETWEEN_TILES),
    (500 + 9*GAP_BETWEEN_TILES, 350 + 6*GAP_BETWEEN_TILES),
    (500 + 9*GAP_BETWEEN_TILES, 400 + 7*GAP_BETWEEN_TILES),  # Corner
    
    (450 + 8*GAP_BETWEEN_TILES, 400 + 7*GAP_BETWEEN_TILES),  # Horizontal row - bottom 
    (400 + 7*GAP_BETWEEN_TILES, 400 + 7*GAP_BETWEEN_TILES),
    (350 + 6*GAP_BETWEEN_TILES, 400 + 7*GAP_BETWEEN_TILES),
    (300 + 5*GAP_BETWEEN_TILES, 400 + 7*GAP_BETWEEN_TILES),
    (250 + 4*GAP_BETWEEN_TILES, 400 + 7*GAP_BETWEEN_TILES),
    (200 + 3*GAP_BETWEEN_TILES, 400 + 7*GAP_BETWEEN_TILES),
    
    (200 + 3*GAP_BETWEEN_TILES, 350 + 6*GAP_BETWEEN_TILES),  # Vertical column - central
    (200 + 3*GAP_BETWEEN_TILES, 300 + 5*GAP_BETWEEN_TILES),
    (150 + 2*GAP_BETWEEN_TILES, 300 + 5*GAP_BETWEEN_TILES),  # Horizontal row - central
    (100 + GAP_BETWEEN_TILES, 300 + 5*GAP_BETWEEN_TILES),
    (50, 300 + 5*GAP_BETWEEN_TILES),
    (50, 250 + 4*GAP_BETWEEN_TILES),           # Vertical column - left (part 1)
    (50, 200 + 3*GAP_BETWEEN_TILES),
    
    (150 + 2*GAP_BETWEEN_TILES, 400 + 7*GAP_BETWEEN_TILES),  # Another path from bottom
    (100 + GAP_BETWEEN_TILES, 400 + 7*GAP_BETWEEN_TILES),
    (50, 400 + 7*GAP_BETWEEN_TILES),           # Corner
    (50, 350 + 6*GAP_BETWEEN_TILES),           # Vertical column - left (part 2) 
    (50, 300 + 5*GAP_BETWEEN_TILES),
    (50, 250 + 4*GAP_BETWEEN_TILES),
    (50, 200 + 3*GAP_BETWEEN_TILES),
    
    (50, 130 + 2*GAP_BETWEEN_TILES - 5)            # Finish line (moved up by 5px instead of 10px)
]

# Update JAIL_POS to match the new spacing
JAIL_POS = (425 + 7*GAP_BETWEEN_TILES, 325 + 5*GAP_BETWEEN_TILES)
DIE_POS = (250 + 4*GAP_BETWEEN_TILES, 175 + 2*GAP_BETWEEN_TILES)

# Define jail size (will be used for random positioning)
JAIL_SIZE = 60  # Approximate size of jail square, will be scaled later

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
        self.current_x = squares_coords[0][0]
        self.current_y = squares_coords[0][1]
        self.turn_ended = False
        self.position_history = []
        self.active_animations = []
        self.path_choices = {}  # Store path choices for each choice point
        self.jail_x, self.jail_y = None, None  # Store player-specific jail position
        self.quiz_cards = 3

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

def get_movement_path_with_choice(start_pos, choice, remaining_spaces):
    """Get the path when a player chooses a direction at a fork."""
    path = [start_pos, choice]  # Start from choice point to chosen path
    current_pos = choice
    # Move remaining spaces from the chosen path
    for _ in range(remaining_spaces - 1):  # -1 because moving to choice uses 1 space
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
    if "jail" in lower_text:
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
    return ("unknown",)

def get_bonus_image_key(effect):
    """Get the image key for the bonus effect with random selection for alternates."""
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
    global bonus_card_index, quiz_card_index
    message = ""
    chain = False
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
        if bonus_card_index < len(bonus_cards):
            # Only proceed with picking a card if we haven't picked one yet
            if not game_state.get('bonus_image_key'):
                bonus = bonus_cards[bonus_card_index]
                bonus_card_index = (bonus_card_index + 1) % len(bonus_cards)
                drip_drop_sound.play()
                effect = parse_bonus_card(bonus)
                image_key = get_bonus_image_key(effect)
                if image_key:
                    game_state['bonus_image_key'] = image_key
                    game_state['bonus_image_start'] = time.time()
                    game_state['bonus_image_state'] = 'waiting'
                    game_state['bonus_action'] = effect
                    message = f"Player {player.id + 1} picks bonus card: {bonus}."
                else:
                    message = f"Player {player.id + 1} picks unknown bonus card."
                # Set the processing_bonus_card flag to prevent re-entry
                game_state['processing_bonus_card'] = True
            else:
                message = f"Player {player.id + 1} is already processing a bonus card."
            player.turn_ended = True
            # Make sure has_rolled is set to ensure turn will end properly
            player.has_rolled = True
        else:
            message = f"Player {player.id + 1} has no bonus cards left."
            player.turn_ended = True
            player.has_rolled = True
    elif square_type == 'Q':
        if quiz_card_index < len(quiz_cards):
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
        game_state['show_path_choice_after_roll'] = True
        game_state['roll_for_path_choice'] = game_state['dice_roll']
        # Don't reset spaces_remaining here - use the value set by get_movement_path
        chain = True  # Allow turn to continue after path choice
        player.turn_ended = False
    elif square_type == 'F':
        player.finished = True
        player.position = len(squares) - 1
        win_sound.play()
        message = f"Player {player.id + 1} finished!"
        player.turn_ended = True
        if game_state.get('finish_order') is None:
            game_state['finish_order'] = []
        game_state['finish_order'].append(player)
        if len(game_state['finish_order']) == len(game_state['players']):
            fairlin_round1_sound.play()
            scaled_x = lambda idx: int(100 * scale + idx * 50 * scale)
            scaled_y = lambda _: int(500 * scale)
            for idx, fin_player in enumerate(game_state['finish_order']):
                fin_player.current_x = scaled_x(idx)
                fin_player.current_y = scaled_y(idx)
    elif square_type == 'Go':
        message = f"Player {player.id + 1} at start."
        player.turn_ended = True
    return message, chain

def move_player(player, game_state):
    """Handle a player rolling the die."""
    if player.finished:
        return "Player has finished.", False
    if game_state.get('rolling_dice', False):
        return "", False
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
    for player in game_state['players']:
        if player.active_animations:
            any_animations = True
            anim = player.active_animations[0]
            current_time = time.time()
            if current_time - anim['last_time'] >= anim['delay']:
                if 'is_jail_move' in anim:
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
                        elif anim.get('jail_action') == 'exit':
                            # Sound is now played at animation start instead of completion
                            anim['player'].position = anim['player'].prev_position
                            anim['player'].in_jail = False
                        player.active_animations.pop(0)
                        player.turn_ended = True
                else:
                    anim['index'] += 1
                    if anim['index'] < len(anim['path']):
                        # Update player position to match current point in animation path
                        anim['player'].position = anim['path'][anim['index']]
                        anim['player'].current_x, anim['player'].current_y = squares_coords[anim['player'].position]
                        
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
                            if not chain or game_state.get('show_quiz', False):
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

def render_coloured_message(screen, font, message, x, y, offset_x, offset_y, players, player_colours):
    """Render a message with player number in their colour."""
    x = int(x + offset_x)
    y = int(y + offset_y)
    parts = message.split("Player ", 1)
    if len(parts) == 1:
        text_surface = font.render(message, True, BLACK)
        screen.blit(text_surface, (x, y))
    else:
        prefix = parts[0]
        rest = parts[1]
        player_num_str = ""
        i = 0
        while i < len(rest) and rest[i].isdigit():
            player_num_str += rest[i]
            i += 1
        player_id = int(player_num_str) - 1 if player_num_str else -1
        remainder = rest[i:] if i < len(rest) else ""

        current_x = x
        if prefix:
            prefix_surface = font.render(prefix, True, BLACK)
            screen.blit(prefix_surface, (current_x, y))
            current_x += prefix_surface.get_width()
        
        player_text = font.render("Player ", True, BLACK)
        screen.blit(player_text, (current_x, y))
        current_x += player_text.get_width()

        if 0 <= player_id < len(players):
            number_colour = player_colours[players[player_id].colour_index]
            number_surface = font.render(player_num_str, True, number_colour)
            screen.blit(number_surface, (current_x, y))
            current_x += number_surface.get_width()
        else:
            number_surface = font.render(player_num_str, True, BLACK)
            screen.blit(number_surface, (current_x, y))
            current_x += number_surface.get_width()

        if remainder:
            remainder_surface = font.render(remainder, True, BLACK)
            screen.blit(remainder_surface, (current_x, y))

def draw_board(players, game_state, scale, offset_x, offset_y, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, bonus_result_images_scaled):
    """Draw the game board and all its elements with card-flipping animations for button and squish for squares."""
    screen.fill(GRAY)

    # Draw board spaces with pulsing squish animation during restart
    for i, square in enumerate(squares):
        x = int(squares_coords[i][0] * scale + offset_x)
        y = int(squares_coords[i][1] * scale + offset_y)

        # Determine the correct image for '1' and '-2' based on position
        if square in ['Go', 'B', 'Q', 'J', '0', 'P', 'F']:
            img = tile_images_scaled[square]
        elif square == '1':
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
        elif square == '-2':
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
            screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))

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
                x = int(player.current_x * scale + offset_x)
                y = int(player.current_y * scale + offset_y)
                
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
                img = cpu_image_scaled
            else:
                img = player_images_scaled[player.colour_index]
            screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))

    current_player = players[game_state['current_player']]
    next_id = (game_state['current_player'] + 1) % len(players)
    while next_id < len(players) and players[next_id].finished and len(game_state.get('finish_order', [])) < len(players):
        next_id = (next_id + 1) % len(players)
    if next_id < len(players):
        next_player = players[next_id]
        render_player_text(screen, font, "Current Turn: ", current_player, int(50 * scale), scale, offset_y, player_colours)
        render_player_text(screen, font, "Next Turn: ", next_player, int(80 * scale), scale, offset_y, player_colours)

    if 'message' in game_state:
        render_coloured_message(screen, font, game_state['message'], int(50 * scale), int(500 * scale), offset_x, offset_y, players, player_colours)

    # Draw die
    dice_rect = pygame.Rect(int(DIE_POS[0] * scale + offset_x), int(DIE_POS[1] * scale + offset_y), int(50 * scale), int(50 * scale))
    if game_state.get('rolling_dice', False):
        if time.time() - game_state['dice_start_time'] < 1:
            dice_face = random.choice(dice_images_scaled)
            rand_x = int(random.randint(100, ORIGINAL_WIDTH - 100) * scale + offset_x)
            rand_y = int(random.randint(100, ORIGINAL_HEIGHT - 100) * scale + offset_y)
            screen.blit(dice_face, (rand_x, rand_y))
        else:
            roll = game_state['dice_roll']
            dice_face = dice_images_scaled[roll - 1]
            screen.blit(dice_face, dice_rect.topleft)
            game_state['final_dice_roll'] = roll
            game_state['movement_delay_start'] = time.time()
            game_state['rolling_dice'] = False
    elif 'movement_delay_start' in game_state:
        current_time = time.time()
        roll = game_state['dice_roll']
        dice_face = dice_images_scaled[roll - 1]
        screen.blit(dice_face, dice_rect.topleft)
        if current_time - game_state['movement_delay_start'] >= 0.5:
            del game_state['movement_delay_start']
            current_player = players[game_state['current_player']]
            current_player.position_history.append(current_player.position)
            if current_player.in_jail:
                if roll % 2 == 0:
                    current_player.in_jail = False
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
        bar_width = int(restart_button_size * progress)
        bar_height = int(5 * scale)
        bar_rect = pygame.Rect(draw_pos[0], draw_pos[1] + restart_button_size, bar_width, bar_height)
        pygame.draw.rect(screen, GREEN, bar_rect)
    else:
        screen.blit(restart_button_scaled, restart_button_rect.topleft)

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
        quiz_width = int(300 * scale)  # Match bonus card width
        quiz_height = int(150 * scale)  # Slightly smaller height for quiz

        if game_state['quiz_state'] == 'growing':
            scale_factor = min(1.0, elapsed / 1.0)
            width = int(quiz_width * scale_factor)
            height = int(quiz_height * scale_factor)
            rect = pygame.Rect(die_center_x - width // 2, die_center_y - height // 2, width, height)
            pygame.draw.rect(screen, WHITE, rect)
            if elapsed >= 1.0:
                game_state['quiz_state'] = 'waiting'
                game_state['quiz_timer'] = current_time + 1.0
        elif game_state['quiz_state'] == 'waiting':
            rect = pygame.Rect(die_center_x - quiz_width // 2, die_center_y - quiz_height // 2, quiz_width, quiz_height)
            pygame.draw.rect(screen, WHITE, rect)
            question, options, _ = game_state['quiz_question']
            text = font.render(question, True, BLACK)
            screen.blit(text, (rect.x + int(10 * scale), rect.y + int(10 * scale)))
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
            text = font.render(question, True, BLACK)
            screen.blit(text, (rect.x + int(10 * scale), rect.y + int(10 * scale)))
            quiz_buttons = []
            button_height = int(25 * scale)
            button_spacing = int(5 * scale)
            for i, option in enumerate(options):
                button = pygame.Rect(
                    rect.x + int(10 * scale),
                    rect.y + int(50 * scale) + i * (button_height + button_spacing),
                    quiz_width - int(20 * scale),
                    button_height
                )
                
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
                text = font.render(option, True, WHITE)
                screen.blit(text, (button.x + int(10 * scale), button.y + int(5 * scale)))
                quiz_buttons.append((button, i))
            game_state['quiz_buttons'] = quiz_buttons
        elif game_state['quiz_state'] == 'answered':
            rect = pygame.Rect(die_center_x - quiz_width // 2, die_center_y - quiz_height // 2, quiz_width, quiz_height)
            pygame.draw.rect(screen, WHITE, rect)
            question, _, _ = game_state['quiz_question']
            text = font.render(question, True, BLACK)
            screen.blit(text, (rect.x + int(10 * scale), rect.y + int(10 * scale)))
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
            if elapsed >= 1.0:
                game_state['show_quiz'] = False
                del game_state['quiz_question']
                del game_state['quiz_shrink_start']
                if 'quiz_answer_delay_start' in game_state:
                    del game_state['quiz_answer_delay_start']

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
    
    player_states = [0, 0, 0, 0, 0, 0]
    difficulties = [None, None, None, None, None, None]
    
    not_set_image = pygame.image.load(load_asset("Assets/Images/Players/Player Not.png"))
    player_images_scaled = [pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale))) for img in player_images_original]
    cpu_image_scaled = pygame.transform.smoothscale(cpu_image_original, (int(80 * scale), int(80 * scale)))
    not_set_image_scaled = pygame.transform.smoothscale(not_set_image, (int(80 * scale), int(80 * scale)))
    difficulty_images_scaled = {
        key: pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale)))
        for key, img in difficulty_images_original.items()
    }
    
    slot_rects = [pygame.Rect(int(100 * scale + offset_x + i * 100 * scale), int(200 * scale + offset_y), int(80 * scale), int(80 * scale)) for i in range(6)]
    start_button_rect = pygame.Rect(int(300 * scale + offset_x), int(400 * scale + offset_y), int(200 * scale), int(50 * scale))

    while True:
        difficulty_rects = []
        for i, state in enumerate(player_states):
            if state == 2:
                slot_rect = slot_rects[i]
                diff_x = int(slot_rect.centerx - 25 * scale)
                diff_y = int(290 * scale + offset_y)
                diff_rect = pygame.Rect(diff_x, diff_y, int(50 * scale), int(50 * scale))
                difficulty_rects.append((i, diff_rect))

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
                player_images_scaled = [pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale))) for img in player_images_original]
                cpu_image_scaled = pygame.transform.smoothscale(cpu_image_original, (int(80 * scale), int(80 * scale)))
                not_set_image_scaled = pygame.transform.smoothscale(not_set_image, (int(80 * scale), int(80 * scale)))
                difficulty_images_scaled = {
                    key: pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale)))
                    for key, img in difficulty_images_original.items()
                }
                slot_rects = [pygame.Rect(int(100 * scale + offset_x + i * 100 * scale), int(200 * scale + offset_y), int(80 * scale), int(80 * scale)) for i in range(6)]
                start_button_rect = pygame.Rect(int(300 * scale + offset_x), int(400 * scale + offset_y), int(200 * scale), int(50 * scale))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button == 1:
                    for i, diff_rect in difficulty_rects:
                        if diff_rect.collidepoint(pos):
                            cycle_difficulty(i, difficulties)
                            break
                    else:
                        for i, rect in enumerate(slot_rects):
                            if rect.collidepoint(pos):
                                toggle_player_state(i, player_states, difficulties)
                                break
                if start_button_rect.collidepoint(pos) and any(state > 0 for state in player_states):
                    selected_players = []
                    for i, state in enumerate(player_states):
                        if state == 1:
                            selected_players.append((i, False, None))
                        elif state == 2:
                            selected_players.append((i, True, difficulties[i]))
                    super_mario_sound.play()
                    return selected_players
            elif event.type == pygame.KEYDOWN:
                if event.key >= pygame.K_1 and event.key <= pygame.K_6:
                    index = event.key - pygame.K_1
                    if index < len(player_states):
                        toggle_player_state(index, player_states, difficulties)

        screen.fill(GRAY)
        for i, (rect, state) in enumerate(zip(slot_rects, player_states)):
            if state == 0:
                screen.blit(not_set_image_scaled, rect.topleft)
            elif state == 1:
                screen.blit(player_images_scaled[i], rect.topleft)
            elif state == 2:
                screen.blit(cpu_image_scaled, rect.topleft)
                if difficulties[i]:
                    diff_img = difficulty_images_scaled[difficulties[i]]
                    for slot_i, diff_rect in difficulty_rects:
                        if slot_i == i:
                            screen.blit(diff_img, diff_rect.topleft)
                            break
            label = font.render(f"P{i+1}", True, player_colours[i])
            screen.blit(label, (rect.centerx - label.get_width() // 2, rect.top - int(20 * scale)))

        pygame.draw.rect(screen, GREEN if any(state > 0 for state in player_states) else GRAY, start_button_rect)
        text = font.render("Start Game", True, BLACK)
        screen.blit(text, text.get_rect(center=start_button_rect.center))

        pygame.display.flip()

def resize_assets(scale):
    """Resize all game assets based on screen scale while maintaining aspect ratios where necessary."""
    # Calculate slightly smaller tile size to account for the gaps
    tile_size = int(50 * scale) - int(GAP_BETWEEN_TILES * scale * 0.3)  # Reduced factor from 0.5 to 0.3 for smaller gap
    
    tile_images_scaled = {
        key: pygame.transform.smoothscale(img, (tile_size, tile_size))
        for key, img in tile_images_original.items() if key not in ['F', 'Jail']
    }
    finish_rotated = pygame.transform.rotate(tile_images_original['F'], 90)
    tile_images_scaled['F'] = pygame.transform.smoothscale(finish_rotated, (tile_size, int(100 * scale) - int(GAP_BETWEEN_TILES * scale * 0.3)))
    tile_images_scaled['Jail'] = pygame.transform.smoothscale(tile_images_original['Jail'], (int(75 * scale) - int(GAP_BETWEEN_TILES * scale * 0.3), int(75 * scale) - int(GAP_BETWEEN_TILES * scale * 0.3)))
    
    # Keep player tokens the same size
    player_images_scaled = [pygame.transform.smoothscale(img, (int(40 * scale), int(40 * scale))) for img in player_images_original]
    for img in player_images_scaled:
        img.set_alpha(191)
    cpu_image_scaled = pygame.transform.smoothscale(cpu_image_original, (int(40 * scale), int(40 * scale)))
    cpu_image_scaled.set_alpha(191)
    
    # Keep other game elements the same size
    dice_images_scaled = [pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale))) for img in dice_images_original]
    restart_button_scaled = pygame.transform.smoothscale(restart_button_original, (int(50 * scale), int(50 * scale)))
    
    # Scale bonus images with a smaller size (300x225 instead of 400x300)
    target_width = int(250 * scale)  # Reduced from 300 to 250
    target_height = int(target_width * 3 / 4)  # Height preserves 4:3 ratio
    bonus_result_images_scaled = {
        key: pygame.transform.smoothscale(img, (target_width, target_height))
        for key, img in bonus_result_images_original.items()
    }
    
    return tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, bonus_result_images_scaled

def main():
    """Main game loop - where all the action happens."""
    global SCREEN_WIDTH, SCREEN_HEIGHT, scale, offset_x, offset_y, screen, font, quiz_card_index, bonus_card_index
    scale = 1.0
    offset_x = 0
    offset_y = 0
    connect_sound.play()

    quit_game = False
    while not quit_game:
        selected_players = select_players()
        if selected_players is None:
            break

        players = [Player(i, colour_idx, is_computer, difficulty) for i, (colour_idx, is_computer, difficulty) in enumerate(selected_players)]
        for player in players:
            player.position_history.append(player.position)
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
            'processing_bonus_card': False  # Add a flag to track if we're currently processing a bonus card
        }
        clock = pygame.time.Clock()

        tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, bonus_result_images_scaled = resize_assets(scale)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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
                    tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, bonus_result_images_scaled = resize_assets(scale)
                    game_state['last_scale'] = scale
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        current_player = players[game_state['current_player']]
                        if not current_player.is_computer and not game_state.get('show_quiz', False) and \
                           not game_state.get('show_path_choice_after_roll', False) and \
                           not game_state.get('rolling_dice', False) and not current_player.has_rolled and \
                           not game_state.get('bonus_image_state') and not animations_active:
                            message, moved = move_player(current_player, game_state)
                            game_state['message'] = message
                    if game_state.get('show_quiz', False) and 'quiz_buttons' in game_state:
                        for button, option_index in game_state['quiz_buttons']:
                            if button.collidepoint(pos):
                                _, _, correct = game_state['quiz_question']
                                if option_index == correct:
                                    apply_quiz_effect(current_player, True, game_state, scale)
                                else:
                                    apply_quiz_effect(current_player, False, game_state, scale)
                    if game_state.get('show_path_choice_after_roll', False) and 'path_buttons' in game_state:
                        for button, choice in game_state['path_buttons']:
                            if button.collidepoint(pos):
                                remaining_spaces = game_state['spaces_remaining']
                                movement_path = get_movement_path_with_choice(current_player.position, choice, remaining_spaces)
                                anim = {
                                    'player': current_player,
                                    'path': movement_path,
                                    'index': 0,
                                    'last_time': time.time(),
                                    'message': f"Player {current_player.id + 1} chose path to {choice}. Moving {remaining_spaces - 1} more spaces.",
                                    'is_initial_move': True,
                                    'delay': 0.5
                                }
                                current_player.active_animations.append(anim)
                                indigogo_sound.play()
                                game_state['show_path_choice_after_roll'] = False
                                del game_state['path_buttons']
                                del game_state['roll_for_path_choice']
                                del game_state['spaces_remaining']
                                current_player.has_rolled = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    restart_button_rect = pygame.Rect(int(650 * scale + offset_x), int(540 * scale + offset_y), int(50 * scale), int(50 * scale))
                    if restart_button_rect.collidepoint(pos):
                        game_state['restart_hold_start'] = time.time()
                    dice_rect = pygame.Rect(int(DIE_POS[0] * scale + offset_x), int(DIE_POS[1] * scale + offset_y), int(50 * scale), int(50 * scale))
                    current_player = players[game_state['current_player']]
                    if not current_player.is_computer and dice_rect.collidepoint(pos) and not game_state.get('show_quiz', False) and \
                           not game_state.get('show_path_choice_after_roll', False) and not game_state.get('rolling_dice', False) and \
                           not current_player.has_rolled and not game_state.get('bonus_image_state') and not animations_active:
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
                                movement_path = get_movement_path_with_choice(current_player.position, choice, remaining_spaces)
                                anim = {
                                    'player': current_player,
                                    'path': movement_path,
                                    'index': 0,
                                    'last_time': time.time(),
                                    'message': f"Player {current_player.id + 1} chose path to {choice}. Moving {remaining_spaces} more spaces.",
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
                            mac_os_uh_ohh_sound.play()
                            whiz_sound.play()  # Play the whiz sound for jail movement
                            player.prev_position = player.position
                            
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
                                'message': f"Player {player.id + 1} sent to jail by bonus card.",
                                'is_jail_move': True,
                                'delay': 0.0167,
                                'jail_action': 'enter'
                            }
                            player.active_animations.append(anim)
                            # No need to set turn_ended here, it will be set when animation completes
                        elif effect[0] == "pick_quiz":
                            if quiz_card_index < len(quiz_cards):
                                question, options, correct = quiz_cards[quiz_card_index]
                                game_state['quiz_question'] = (question, options, correct)
                                game_state['show_quiz'] = True
                                game_state['quiz_state'] = 'growing'
                                game_state['quiz_start_time'] = time.time()
                                game_state['pop_played'] = False
                                drum_machine_sound.play()
                                quiz_card_index = (quiz_card_index + 1) % len(quiz_cards)
                                game_state['message'] = f"Player {player.id + 1} picks up a quiz card."
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
                        # Clear the processing_bonus_card flag when the bonus card animation is complete
                        game_state['processing_bonus_card'] = False

            # Handle CPU player turns
            if not animations_active and not game_state.get('show_quiz', False) and not game_state.get('show_path_choice_after_roll', False) and not game_state.get('rolling_dice', False) and 'movement_delay_start' not in game_state and not game_state.get('processing_bonus_card', False):
                current_player = players[game_state['current_player']]
                if current_player.is_computer and not current_player.has_rolled and not current_player.finished:
                    # Check if player is in jail first
                    if current_player.in_jail:
                        message, moved = move_player(current_player, game_state)
                        game_state['message'] = message
                    # Check if current position has path choices
                    elif isinstance(next_positions[current_player.position], list):
                        message, moved = move_player(current_player, game_state)
                        game_state['message'] = message
                        game_state['spaces_remaining'] = game_state['dice_roll']  # Set remaining spaces to full roll
                        choices = next_positions[current_player.position]
                        choice = random.choice(choices)
                        remaining_spaces = game_state['spaces_remaining']
                        current_player.path_choices[current_player.position] = choice
                        movement_path = get_movement_path_with_choice(current_player.position, choice, remaining_spaces)
                        anim = {
                            'player': current_player,
                            'path': movement_path,
                            'index': 0,
                            'last_time': time.time(),
                            'message': f"Player {current_player.id + 1} (CPU) chose path to {choice}. Moving {remaining_spaces} spaces.",
                            'is_initial_move': True,
                            'delay': 0.5
                        }
                        current_player.active_animations.append(anim)
                        indigogo_sound.play()
                        game_state['show_path_choice_after_roll'] = False
                        if 'roll_for_path_choice' in game_state:
                            del game_state['roll_for_path_choice']
                        if 'spaces_remaining' in game_state:
                            del game_state['spaces_remaining']
                        current_player.has_rolled = True
                    else:
                        # Always roll and move for any other square (including B and Q)
                        message, moved = move_player(current_player, game_state)
                        game_state['message'] = message
                        
                elif current_player.finished:
                    current_player.has_rolled = False
                    current_player.turn_ended = False
                    game_state['current_player'] = (game_state['current_player'] + 1) % len(players)
                    while players[game_state['current_player']].finished and len(game_state['finish_order']) < len(players):
                        game_state['current_player'] = (game_state['current_player'] + 1) % len(players)
                elif current_player.turn_ended and not current_player.active_animations:
                    current_player.has_rolled = False
                    current_player.turn_ended = False
                    game_state['current_player'] = (game_state['current_player'] + 1) % len(players)
                    while players[game_state['current_player']].finished and len(game_state['finish_order']) < len(players):
                        game_state['current_player'] = (game_state['current_player'] + 1) % len(players)
            
            # Check if a bonus card animation has just completed and clear the processing flag
            if not game_state.get('bonus_image_state') and game_state.get('processing_bonus_card'):
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

            # Handle CPU players making path choices automatically
            if game_state.get('show_path_choice_after_roll', False) and 'path_buttons' in game_state:
                current_player = players[game_state['current_player']]
                if current_player.is_computer:
                    if 'cpu_path_delay' not in game_state:
                        game_state['cpu_path_delay'] = time.time() + 0.8  # 0.8 second delay
                    elif time.time() > game_state['cpu_path_delay']:
                        # Get available choices
                        choices = next_positions[current_player.position]
                        choice = random.choice(choices)
                        
                        # Find the index of the choice in the path_buttons
                        for i, (_, btn_choice) in enumerate(game_state['path_buttons']):
                            if btn_choice == choice:
                                # Add splash effect tracking for path buttons
                                game_state['clicked_path_button'] = i
                                game_state['path_button_click_time'] = time.time()
                                break
                        
                        # Wait a moment to let the splash effect be visible before applying the choice
                        game_state['cpu_path_splash_delay'] = time.time() + 0.2  # 0.2 second delay to show splash
                        game_state['cpu_path_splash_choice'] = choice
                        
                        # Remove the CPU path choice delay after it's used
                        del game_state['cpu_path_delay']
                
                # Check if we need to apply the path choice after showing the splash effect
                if 'cpu_path_splash_delay' in game_state and time.time() > game_state['cpu_path_splash_delay']:
                    choice = game_state['cpu_path_splash_choice']
                    
                    # Apply chosen path
                    remaining_spaces = game_state.get('spaces_remaining', 0)
                    current_player.path_choices[current_player.position] = choice
                    movement_path = get_movement_path_with_choice(current_player.position, choice, remaining_spaces)
                    anim = {
                        'player': current_player,
                        'path': movement_path,
                        'index': 0,
                        'last_time': time.time(),
                        'message': f"Player {current_player.id + 1} (CPU) chose path to {choice}. Moving {remaining_spaces} spaces.",
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
                    
                    # Remove the splash delay after it's used
                    del game_state['cpu_path_splash_delay']
                    del game_state['cpu_path_splash_choice']

            # Extra check to ensure turn ends properly after a CPU player completes a quiz from a bonus card
            if not game_state.get('show_quiz', False) and game_state.get('quiz_from_bonus_completed', False) and game_state.get('processing_bonus_card', False):
                current_player = players[game_state['current_player']]
                if current_player.is_computer:
                    # Make sure the player's turn will end
                    current_player.turn_ended = True
                    current_player.has_rolled = True
                    
                    # If the bonus card is done processing, clear both flags
                    if not game_state.get('bonus_image_state'):
                        game_state['processing_bonus_card'] = False
                        del game_state['quiz_from_bonus_completed']

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

            draw_board(players, game_state, scale, offset_x, offset_y, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, bonus_result_images_scaled)
            pygame.display.flip()
            clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
