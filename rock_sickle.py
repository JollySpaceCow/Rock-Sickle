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
squares_coords = [
    (50, 50), (100, 50), (150, 50), (200, 50), (250, 50), (300, 50), (350, 50), (400, 50), (450, 50), (500, 50),
    (500, 100), (500, 150), (500, 200), (500, 250), (500, 300), (500, 350), (500, 400),
    (450, 400), (400, 400), (350, 400), (300, 400), (250, 400), (200, 400),
    (200, 350), (200, 300), (150, 300), (100, 300), (50, 300), (50, 250), (50, 200),
    (150, 400), (100, 400), (50, 400), (50, 350), (50, 300), (50, 250), (50, 200),
    (50, 130)
]

# Define constant positions for jail and die
JAIL_POS = (425, 325)
DIE_POS = (250, 175)

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
        if player.position == 0 or len(player.position_history) < 2:
            message = f"Player {player.id + 1} can't move back."
            player.turn_ended = True
        else:
            num_back = 2
            if len(player.position_history) > num_back:
                target_pos = player.position_history[-num_back - 1]
                movement_path = [player.position] + player.position_history[-2:-num_back - 2:-1]
            else:
                target_pos = 0
                movement_path = [player.position] + player.position_history[:-1]
            anim = {
                'player': player,
                'path': movement_path,
                'index': 0,
                'last_time': time.time(),
                'message': f"Moving back to {squares[target_pos]}.",
                'is_backwards': True,
                'delay': 0.5
            }
            player.active_animations.append(anim)
            message = f"Player {player.id + 1} moves back 2 spaces."
            chain = True
            player.turn_ended = False
    elif square_type == 'B':
        if bonus_card_index < len(bonus_cards):
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
            player.turn_ended = True
        else:
            message = f"Player {player.id + 1} has no bonus cards left."
            player.turn_ended = True
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
        anim = {
            'player': player,
            'start_pos': (player.current_x, player.current_y),
            'end_pos': JAIL_POS,
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
    else:
        game_state['message'] = f"Player {player.id + 1} answered wrong. Moving back 2 spaces."
        bing_bong_sound.play()
        if len(player.position_history) > 2:
            target_pos = player.position_history[-3]
            movement_path = player.position_history[-1:-4:-1]
        else:
            target_pos = 0
            movement_path = player.position_history[::-1] + [0] * (2 - len(player.position_history) + 1)
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
                        elif anim.get('jail_action') == 'exit':
                            anim['player'].position = anim['player'].prev_position
                            anim['player'].in_jail = False
                        player.active_animations.pop(0)
                        player.turn_ended = True
                else:
                    anim['index'] += 1
                    if anim['index'] < len(anim['path']):
                        anim['player'].position = anim['path'][anim['index']]
                        anim['player'].current_x, anim['player'].current_y = squares_coords[anim['player'].position]
                        if 'is_backwards' not in anim and anim['player'].position not in anim['player'].position_history:
                            anim['player'].position_history.append(anim['player'].position)
                        elif 'is_backwards' in anim and len(anim['player'].position_history) > 2:
                            anim['player'].position_history.pop()
                        anim['last_time'] = current_time
                        if 'is_initial_move' in anim and anim['is_initial_move']:
                            glug_sound.play()
                        elif 'is_backwards' in anim:
                            wobble_sound.play()
                        else:
                            jump_sound.play()
                        game_state['message'] = anim['message'] + f" Moved to {squares[anim['player'].position]}."
                    else:
                        # If this was a backwards movement, end turn without applying square effects
                        if 'is_backwards' in anim:
                            player.active_animations.pop(0)
                            player.turn_ended = True
                            game_state['message'] = anim['message'] + f" Landed on {squares[anim['player'].position]}."
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

    for player in players:
        if not player.finished or player.position == len(squares) - 1:
            if player.in_jail:
                x, y = jail_x, jail_y
            else:
                x = int(player.current_x * scale + offset_x)
                y = int(player.current_y * scale + offset_y)
            if player.is_computer:
                img = cpu_image_scaled
            else:
                img = player_images_scaled[player.colour_index]
            screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))

    # Draw bonus image with proper centering and 4:3 aspect ratio, starting from die position
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
                    current_player.active_animations.append(anim)
                    head_shake_sound.play()
                    current_player.turn_ended = True
                else:
                    bonk_sound.play()
                    game_state['message'] = f"Player {current_player.id + 1} rolled {roll} (odd). Still in jail."
                    current_player.turn_ended = True
            else:
                if isinstance(next_positions[current_player.position], list):
                    game_state['show_path_choice_after_roll'] = True
                    game_state['roll_for_path_choice'] = roll
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
                pygame.draw.rect(screen, BLUE, button)
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

    if game_state.get('show_path_choice_after_roll', False):
        current_player = players[game_state['current_player']]
        current_pos = current_player.position
        choices = next_positions[current_pos]
        remaining_spaces = game_state.get('spaces_remaining', 0)
        
        # Show ghost players at potential end positions
        for choice in choices:
            movement_path = get_movement_path_with_choice(current_pos, choice, remaining_spaces)
            ending_pos = movement_path[-1]
            x, y = squares_coords[ending_pos]
            x = int(x * scale + offset_x)
            y = int(y * scale + offset_y)
            img = player_images_scaled[current_player.colour_index]
            img_copy = img.copy()
            img_copy.set_alpha(128)
            screen.blit(img_copy, (x - img_copy.get_width() // 2, y - img_copy.get_height() // 2))
        
        # Draw path choice dialog centered on die position
        die_center_x = int(DIE_POS[0] * scale + offset_x)
        die_center_y = int(DIE_POS[1] * scale + offset_y)
        dialog_width = int(300 * scale)
        dialog_height = int(150 * scale)
        rect = pygame.Rect(die_center_x - dialog_width // 2, die_center_y - dialog_height // 2, dialog_width, dialog_height)
        pygame.draw.rect(screen, WHITE, rect)
        text = font.render(f"Choose Path (Spaces left: {remaining_spaces}):", True, BLACK)
        screen.blit(text, (rect.x + int(10 * scale), rect.y + int(10 * scale)))
        
        buttons = []
        labels = ["North", "West"]
        button_height = int(25 * scale)
        button_spacing = int(5 * scale)
        for i, (label, choice) in enumerate(zip(labels, choices)):
            movement_path = get_movement_path_with_choice(current_pos, choice, remaining_spaces)
            ending_pos = movement_path[-1]
            button = pygame.Rect(
                rect.x + int(10 * scale),
                rect.y + int(50 * scale) + i * (button_height + button_spacing),
                dialog_width - int(20 * scale),
                button_height
            )
            pygame.draw.rect(screen, BLUE, button)
            text = font.render(f"{label} (ends at {ending_pos})", True, WHITE)
            screen.blit(text, (button.x + int(10 * scale), button.y + int(5 * scale)))
            buttons.append((button, choice))
        game_state['path_buttons'] = buttons

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
    tile_images_scaled = {
        key: pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale)))
        for key, img in tile_images_original.items() if key not in ['F', 'Jail']
    }
    finish_rotated = pygame.transform.rotate(tile_images_original['F'], 90)
    tile_images_scaled['F'] = pygame.transform.smoothscale(finish_rotated, (int(50 * scale), int(100 * scale)))
    tile_images_scaled['Jail'] = pygame.transform.smoothscale(tile_images_original['Jail'], (int(75 * scale), int(75 * scale)))
    player_images_scaled = [pygame.transform.smoothscale(img, (int(40 * scale), int(40 * scale))) for img in player_images_original]
    for img in player_images_scaled:
        img.set_alpha(191)
    cpu_image_scaled = pygame.transform.smoothscale(cpu_image_original, (int(40 * scale), int(40 * scale)))
    cpu_image_scaled.set_alpha(191)
    dice_images_scaled = [pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale))) for img in dice_images_original]
    restart_button_scaled = pygame.transform.smoothscale(restart_button_original, (int(50 * scale), int(50 * scale)))
    
    # Scale bonus images with a smaller size (300x225 instead of 400x300)
    target_width = int(300 * scale)  # Smaller base width
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
            'restart_ready': False
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
                           not game_state.get('rolling_dice', False) and not current_player.has_rolled:
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
                           not game_state.get('show_path_choice_after_roll', False) and not game_state.get('rolling_dice', False) and not current_player.has_rolled:
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
                                remaining_spaces = game_state.get('spaces_remaining', 0)
                                # Store the player's choice for this position
                                current_player.path_choices[current_player.position] = choice
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
                    if current_time - game_state['bonus_image_start'] >= 0.5:
                        game_state['bonus_image_state'] = 'growing'
                        game_state['bonus_grow_start'] = current_time
                elif game_state['bonus_image_state'] == 'growing':
                    elapsed = current_time - game_state['bonus_grow_start']
                    if elapsed >= 1.0:
                        game_state['bonus_image_state'] = 'showing'
                        # Start the bonus action
                        player = players[game_state['current_player']]
                        effect = game_state['bonus_action']
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
                                'delay': 0.5
                            }
                            player.active_animations.append(anim)
                        elif effect[0] == "move_back":
                            num = effect[1]
                            if len(player.position_history) > num:
                                target_pos = player.position_history[-num-1]
                                movement_path = player.position_history[-1:-num-2:-1]
                            else:
                                target_pos = 0
                                movement_path = player.position_history[::-1] + [0] * (num - len(player.position_history) + 1)
                            anim = {
                                'player': player,
                                'path': movement_path,
                                'index': 0,
                                'last_time': time.time(),
                                'message': f"Player {player.id + 1} moving back {num} spaces from bonus card.",
                                'is_backwards': True,
                                'delay': 0.5
                            }
                            player.active_animations.append(anim)
                        elif effect[0] == "go_to_jail":
                            mac_os_uh_ohh_sound.play()
                            player.prev_position = player.position
                            whiz_sound.play()
                            anim = {
                                'player': player,
                                'start_pos': (player.current_x, player.current_y),
                                'end_pos': JAIL_POS,
                                'steps': 60,
                                'current_step': 0,
                                'last_time': time.time(),
                                'message': f"Player {player.id + 1} sent to jail by bonus card.",
                                'is_jail_move': True,
                                'delay': 0.0167,  # ~60fps (1/60 second)
                                'jail_action': 'enter'
                            }
                            player.active_animations.append(anim)
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
                    if not player.active_animations and not game_state.get('show_quiz', False):
                        game_state['bonus_image_state'] = 'shrinking'
                        game_state['bonus_shrink_start'] = current_time
                        disconnect_sound.play()
                elif game_state['bonus_image_state'] == 'shrinking':
                    elapsed = current_time - game_state['bonus_shrink_start']
                    if elapsed >= 1.0:
                        del game_state['bonus_image_key']
                        del game_state['bonus_image_state']
                        del game_state['bonus_action']

            if not animations_active and not game_state.get('show_quiz', False) and not game_state.get('show_path_choice_after_roll', False) and not game_state.get('rolling_dice', False) and 'movement_delay_start' not in game_state:
                current_player = players[game_state['current_player']]
                if current_player.is_computer and not current_player.has_rolled and not current_player.finished:
                    if current_player.in_jail:
                        message, moved = move_player(current_player, game_state)
                        game_state['message'] = message
                    elif isinstance(next_positions[current_player.position], list):
                        choices = next_positions[current_player.position]
                        choice = random.choice(choices)
                        message, moved = move_player(current_player, game_state)
                        game_state['message'] = message
                        remaining_spaces = game_state.get('spaces_remaining', 0)
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
                        current_player.has_rolled = True
                    else:
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

            draw_board(players, game_state, scale, offset_x, offset_y, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, bonus_result_images_scaled)
            pygame.display.flip()
            clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()