import pygame
import random
import time
import sys
import os
import traceback
import logging

# Set up logging
logging.basicConfig(
    filename=os.path.join(os.path.abspath(os.path.dirname(__file__)), "rock_sickle.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# Determine base path for assets
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.dirname(__file__))

def load_asset(relative_path):
    full_path = os.path.join(base_path, relative_path)
    if not os.path.exists(full_path):
        logger.error(f"Asset not found: {full_path}")
        raise FileNotFoundError(f"Asset not found: {full_path}")
    return full_path

# Initialize Pygame
pygame.init()
logger.info("Pygame initialized successfully")

# Set custom icon
icon_path = load_asset("Assets/Images/Icons/RockSickle.png")
icon_surface = pygame.image.load(icon_path)
pygame.display.set_icon(icon_surface)
logger.info(f"Custom icon set successfully: {icon_path}")

# Screen settings
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = 800, 600
SCREEN_WIDTH, SCREEN_HEIGHT = ORIGINAL_WIDTH, ORIGINAL_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Rock-Sickle")
logger.info("Display initialized successfully")

# Colors
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
player_colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

# Load original image assets
try:
    forward_one_original = pygame.image.load(load_asset("Assets/Images/Tiles/Forward One.png"))
    back_two_original = pygame.image.load(load_asset("Assets/Images/Tiles/Back Two.png"))
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

# Load difficulty images
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

# Load audio assets
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
    logger.info("Audio assets loaded successfully")
except Exception as e:
    logger.error(f"Error loading audio assets: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Font
font = pygame.font.SysFont(None, 24)

# Board squares and coordinates
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

# Quiz and bonus cards
quiz_cards = [
    ("Which process turns sediment into rock?", ["Weathering", "Erosion", "Lithification"], 2),
    ("How are igneous rocks formed?", ["By layers of sediment building up", "When magma cools down", "From the Earth's crust", "When old rocks undergo intense pressure and heat"], 1),
    ("What type of rock is formed by pressure and heat?", ["Metamorphic", "Igneous"], 0),
    ("Is air a rock?", ["Yes", "No"], 1),
    ("What type of rock is formed in layers?", ["Sedimentary", "When flowing water touches lava", "Igneous"], 0),
    ("Is Granite a metamorphic rock?", ["Yes", "No"], 1),
    ("What is molten rock called underground?", ["Magma", "Erupt", "Lava"], 0),
    ("What are the three main types of rock?", ["Molten, Solid, Liquid", "Smooth, Hard, Brittle", "Adhesion, Mohs, Bead", "Sedimentary, Igneous, Metamorphic"], 3),
    ("What type of rock can you find fossils in?", ["Granite", "Sedimentary", "Metamorphic"], 1),
]
random.shuffle(quiz_cards)
quiz_card_index = 0

bonus_cards = ["Move forward 2 spaces", "Go back 1 space", "Roll again", "Go to jail"]
random.shuffle(bonus_cards)
bonus_card_index = 0

class Player:
    def __init__(self, id, color_index, is_computer=False, difficulty=None):
        self.id = id
        self.color_index = color_index
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

def roll_die(difficulty=None):
    if difficulty == 'easy':
        return random.choice([1, 1, 2, 2, 3, 4])
    elif difficulty == 'hard':
        return random.choice([3, 4, 5, 6, 6, 6])
    else:
        return random.randint(1, 6)

def interpolate_position(start_pos, end_pos, steps, current_step):
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    x = start_x + (end_x - start_x) * current_step / steps
    y = start_y + (end_y - start_y) * current_step / steps
    return x, y

def apply_effect(player, square_type, game_state, scale):
    global bonus_card_index, quiz_card_index
    message = ""
    chain = False
    if square_type == '0':
        message = f"Player {player.id + 1} on safe space. Turn ends."
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
            message = f"Player {player.id + 1} cannot move forward beyond board."
            player.turn_ended = True
    elif square_type == '-2':
        if player.position == 0 or len(player.position_history) < 2:
            message = f"Player {player.id + 1} cannot move back from start or insufficient history."
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
            game_state['bonus_delay_start'] = time.time()
            game_state['bonus_action'] = bonus
            message = f"Player {player.id + 1} picks bonus card: {bonus}. Action will be applied in 1.5 seconds."
            player.turn_ended = True
        else:
            message = f"Player {player.id + 1} has no more bonus cards."
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
            message = f"Player {player.id + 1} must answer the quiz question."
        else:
            message = f"Player {player.id + 1} has no more quiz cards."
        player.turn_ended = True
    elif square_type == 'J':
        player.prev_position = player.position
        whiz_sound.play()
        anim = {
            'player': player,
            'start_pos': (player.current_x, player.current_y),
            'end_pos': (400, 200),
            'steps': 20,
            'current_step': 0,
            'last_time': time.time(),
            'message': "Moving to jail.",
            'is_jail_move': True,
            'delay': 0.5
        }
        player.active_animations.append(anim)
        message = f"Player {player.id + 1} moving to jail. Roll even to escape on next turn."
        player.turn_ended = True
    elif square_type == 'P':
        game_state['show_path_choice'] = True
        game_state['pending_move'] = {'player': player, 'choices': next_positions[player.position]}
        message = f"Player {player.id + 1} chooses path."
        player.turn_ended = True
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
        message = f"Player {player.id + 1} at start position."
        player.turn_ended = True
    return message, chain

def get_movement_path(start_pos, spaces, in_jail=False):
    path = [start_pos]
    current_pos = start_pos
    if in_jail:
        return path
    for _ in range(spaces):
        if current_pos >= len(squares) - 1:
            path.append(len(squares) - 1)
            break
        next_pos = next_positions[current_pos]
        if isinstance(next_pos, list):
            path.append(current_pos)
            break
        else:
            current_pos = next_pos if next_pos is not None else current_pos
            path.append(current_pos)
    return path

def move_player(player, game_state, roll=None):
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
    return "", True

def apply_quiz_effect(player, correct, game_state, scale):
    if correct:
        game_state['message'] = f"Player {player.id + 1} answered correctly! Turn ends."
        mac_os_dinbg_sound.play()
        player.turn_ended = True
        game_state['quiz_state'] = 'shrinking'
        game_state['quiz_shrink_start'] = time.time()
        disconnect_sound.play()
    else:
        game_state['message'] = f"Player {player.id + 1} answered incorrectly. Moving back 2 spaces."
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
        game_state['quiz_state'] = 'shrinking'
        game_state['quiz_shrink_start'] = time.time()
        disconnect_sound.play()

def update_animation(game_state, scale):
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
                        if anim['message'].startswith("Moving to jail") or anim['message'].startswith("Bonus card: Sent to jail"):
                            anim['player'].position = 10
                            anim['player'].in_jail = True
                        elif anim['message'].startswith("Rolled"):
                            anim['player'].position = anim['player'].prev_position
                        player.active_animations.pop(0)
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
                        square_type = squares[anim['player'].position]
                        message, chain = apply_effect(anim['player'], square_type, game_state, scale)
                        game_state['message'] = anim['message'] + f" Landed on {square_type}. {message}"
                        player.active_animations.pop(0)
                        if chain and not game_state.get('show_quiz', False) and not game_state.get('show_path_choice', False):
                            any_animations = True
                        else:
                            anim['player'].turn_ended = True
    return any_animations

def render_player_text(screen, font, prefix, player, y, scale, player_colors):
    prefix_surface = font.render(prefix, True, BLACK)
    player_text = font.render("Player ", True, BLACK)
    number_text = font.render(str(player.id + 1), True, player_colors[player.color_index])
    cpu_text = font.render(" (CPU)", True, BLACK) if player.is_computer else None

    x = int(600 * scale)
    screen.blit(prefix_surface, (x, y))
    x += prefix_surface.get_width()
    screen.blit(player_text, (x, y))
    x += player_text.get_width()
    screen.blit(number_text, (x, y))
    if cpu_text:
        x += number_text.get_width()
        screen.blit(cpu_text, (x, y))

def render_colored_message(screen, font, message, x, y, players, player_colors):
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
            number_color = player_colors[players[player_id].color_index]
            number_surface = font.render(player_num_str, True, number_color)
            screen.blit(number_surface, (current_x, y))
            current_x += number_surface.get_width()
        else:
            number_surface = font.render(player_num_str, True, BLACK)
            screen.blit(number_surface, (current_x, y))
            current_x += number_surface.get_width()

        if remainder:
            remainder_surface = font.render(remainder, True, BLACK)
            screen.blit(remainder_surface, (current_x, y))

def draw_board(players, game_state, scale, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled):
    global SCREEN_WIDTH
    screen.fill(GRAY)
    for i, square in enumerate(squares):
        x, y = int(squares_coords[i][0] * scale), int(squares_coords[i][1] * scale)
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
        screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))

    jail_x, jail_y = int(400 * scale), int(200 * scale)
    screen.blit(tile_images_scaled['Jail'], (jail_x - tile_images_scaled['Jail'].get_width() // 2, jail_y - tile_images_scaled['Jail'].get_height() // 2))

    for player in players:
        if not player.finished or player.position == len(squares) - 1:
            if player.in_jail:
                x, y = jail_x, jail_y
            else:
                x, y = int(player.current_x * scale), int(player.current_y * scale)
            if player.is_computer:
                img = cpu_image_scaled
            else:
                img = player_images_scaled[player.color_index]
            screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))

    roll_button = pygame.Rect(int(600 * scale), int(500 * scale), int(150 * scale), int(50 * scale))
    pygame.draw.rect(screen, GREEN, roll_button)
    text = font.render("Roll Die", True, BLACK)
    screen.blit(text, (roll_button.x + int(10 * scale), roll_button.y + int(15 * scale)))

    dev_buttons = [
        ("One Space Fwd", pygame.Rect(int(600 * scale), int(450 * scale), int(150 * scale), int(40 * scale)), ORANGE),
        ("One Jump Fwd", pygame.Rect(int(600 * scale), int(400 * scale), int(150 * scale), int(40 * scale)), YELLOW),
        ("Go to Jail", pygame.Rect(int(600 * scale), int(350 * scale), int(150 * scale), int(40 * scale)), RED),
        ("Get Out Jail", pygame.Rect(int(600 * scale), int(300 * scale), int(150 * scale), int(40 * scale)), GREEN),
        ("Quiz Card", pygame.Rect(int(600 * scale), int(250 * scale), int(150 * scale), int(40 * scale)), BLUE),
        ("Bonus Card", pygame.Rect(int(600 * scale), int(200 * scale), int(150 * scale), int(40 * scale)), PURPLE),
        ("Back 2", pygame.Rect(int(600 * scale), int(150 * scale), int(150 * scale), int(40 * scale)), PINK),
    ]
    for label, rect, color in dev_buttons:
        pygame.draw.rect(screen, color, rect)
        text = font.render(label, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    # Turn Indicator UI
    current_player = players[game_state['current_player']]
    next_id = (game_state['current_player'] + 1) % len(players)
    while next_id < len(players) and players[next_id].finished and len(game_state['finish_order']) < len(players):
        next_id = (next_id + 1) % len(players)
    if next_id < len(players):
        next_player = players[next_id]
        render_player_text(screen, font, "Current Turn: ", current_player, int(50 * scale), scale, player_colors)
        render_player_text(screen, font, "Next Turn: ", next_player, int(80 * scale), scale, player_colors)

    if 'message' in game_state:
        render_colored_message(screen, font, game_state['message'], int(50 * scale), int(500 * scale), players, player_colors)

    if game_state.get('show_quiz', False) and game_state.get('quiz_question'):
        current_time = time.time()
        elapsed = current_time - game_state['quiz_start_time']
        if game_state['quiz_state'] == 'growing':
            scale_factor = min(1.0, elapsed / 1.0)
            width = int(400 * scale * scale_factor)
            height = int(200 * scale * scale_factor)
            rect = pygame.Rect(int(200 * scale + (400 * scale - width) // 2), int(200 * scale + (200 * scale - height) // 2), width, height)
            pygame.draw.rect(screen, WHITE, rect)
            if elapsed >= 1.0:
                game_state['quiz_state'] = 'waiting'
                game_state['quiz_timer'] = current_time + 0.5
        elif game_state['quiz_state'] == 'waiting':
            pygame.draw.rect(screen, WHITE, (int(200 * scale), int(200 * scale), int(400 * scale), int(200 * scale)))
            question, options, _ = game_state['quiz_question']
            text = font.render(question, True, BLACK)
            screen.blit(text, (int(210 * scale), int(210 * scale)))
            if current_time >= game_state['quiz_timer']:
                game_state['quiz_state'] = 'buttons'
                game_state['pop_played'] = False
        elif game_state['quiz_state'] == 'buttons':
            if not game_state['pop_played']:
                pop_sound.play()
                game_state['pop_played'] = True
            pygame.draw.rect(screen, WHITE, (int(200 * scale), int(200 * scale), int(400 * scale), int(200 * scale)))
            question, options, _ = game_state['quiz_question']
            text = font.render(question, True, BLACK)
            screen.blit(text, (int(210 * scale), int(210 * scale)))
            quiz_buttons = []
            for i, option in enumerate(options):
                button = pygame.Rect(int(210 * scale), int(250 * scale + i * 40 * scale), int(380 * scale), int(30 * scale))
                pygame.draw.rect(screen, BLUE, button)
                text = font.render(option, True, WHITE)
                screen.blit(text, (button.x + int(10 * scale), button.y + int(5 * scale)))
                quiz_buttons.append((button, i))
            game_state['quiz_buttons'] = quiz_buttons
        elif game_state['quiz_state'] == 'shrinking':
            elapsed = current_time - game_state['quiz_shrink_start']
            scale_factor = max(0.0, 1.0 - elapsed / 1.0)
            width = int(400 * scale * scale_factor)
            height = int(200 * scale * scale_factor)
            rect = pygame.Rect(int(200 * scale + (400 * scale - width) // 2), int(200 * scale + (200 * scale - height) // 2), width, height)
            pygame.draw.rect(screen, WHITE, rect)
            if elapsed >= 1.0:
                game_state['show_quiz'] = False
                del game_state['quiz_question']

    if game_state.get('show_path_choice', False):
        pygame.draw.rect(screen, WHITE, (int(200 * scale), int(200 * scale), int(400 * scale), int(200 * scale)))
        text = font.render("Choose Path:", True, BLACK)
        screen.blit(text, (int(210 * scale), int(210 * scale)))
        buttons = []
        choices = game_state.get('pending_move', {}).get('choices', [23, 30])
        labels = ["North", "West"]
        for i, choice in enumerate(choices):
            button = pygame.Rect(int(210 * scale), int(250 * scale + i * 40 * scale), int(380 * scale), int(30 * scale))
            pygame.draw.rect(screen, BLUE, button)
            text = font.render(labels[i], True, WHITE)
            screen.blit(text, (button.x + int(10 * scale), button.y + int(5 * scale)))
            buttons.append((button, choice))
        game_state['path_buttons'] = buttons

    dice_rect = pygame.Rect(int(350 * scale), int(250 * scale), int(50 * scale), int(50 * scale))
    if game_state.get('rolling_dice', False):
        current_player = players[game_state['current_player']]
        if time.time() - game_state['dice_start_time'] < 1:
            dice_face = random.choice(dice_images_scaled)
            rand_x = int(random.randint(100, ORIGINAL_WIDTH - 100) * scale)
            rand_y = int(random.randint(100, ORIGINAL_HEIGHT - 100) * scale)
            screen.blit(dice_face, (rand_x, rand_y))
        else:
            roll = game_state['dice_roll']
            dice_face = dice_images_scaled[roll - 1]
            screen.blit(dice_face, dice_rect.topleft)
            game_state['final_dice_roll'] = roll
            game_state['movement_delay_start'] = time.time()
            game_state['rolling_dice'] = False
            current_player.has_rolled = True
    elif 'movement_delay_start' in game_state:
        current_time = time.time()
        if current_time - game_state['movement_delay_start'] >= 0.25:
            del game_state['movement_delay_start']
            current_player = players[game_state['current_player']]
            roll = game_state['dice_roll']
            current_player.position_history.append(current_player.position)
            if current_player.in_jail:
                if roll % 2 == 0:
                    current_player.in_jail = False
                    anim = {
                        'player': current_player,
                        'start_pos': (400, 200),
                        'end_pos': squares_coords[current_player.prev_position],
                        'steps': 20,
                        'current_step': 0,
                        'last_time': time.time(),
                        'message': f"Player {current_player.id + 1} rolled {roll} (even). Escaping jail.",
                        'is_jail_move': True,
                        'delay': 0.05
                    }
                    current_player.active_animations.append(anim)
                    head_shake_sound.play()
                    current_player.turn_ended = True
                else:
                    bonk_sound.play()
                    game_state['message'] = f"Player {current_player.id + 1} rolled {roll} (odd). Still in jail."
                    current_player.turn_ended = True
            else:
                movement_path = get_movement_path(current_player.position, roll)
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
    elif 'final_dice_roll' in game_state:
        dice_face = dice_images_scaled[game_state['final_dice_roll'] - 1]
        screen.blit(dice_face, dice_rect.topleft)

def toggle_player_state(index, player_states, difficulties):
    """Toggle the player slot state: 0 (Not Set) → 1 (Human) → 2 (CPU) → 0."""
    player_states[index] = (player_states[index] + 1) % 3
    if player_states[index] == 0:
        pong_sound.play()
        difficulties[index] = None
    elif player_states[index] == 1:
        whit_sound.play()
        difficulties[index] = None
    elif player_states[index] == 2:
        difficulties[index] = 'normal'  # Default to Normal for CPU
        voltage_normal_sound.play()

def cycle_difficulty(index, difficulties):
    """Cycle CPU difficulty: Easy → Normal → Hard → Easy."""
    if difficulties[index] == 'easy':
        difficulties[index] = 'normal'
        voltage_normal_sound.play()
    elif difficulties[index] == 'normal':
        difficulties[index] = 'hard'
        voltage_hard_sound.play()
    elif difficulties[index] == 'hard':
        difficulties[index] = 'easy'
        voltage_easy_sound.play()

def select_players(scale):
    # Initialize player states and difficulties
    player_states = [1, 0, 0, 0, 0, 0]  # P1 starts as Human, others Not Set
    difficulties = [None, None, None, None, None, None]
    
    # Define slot and button rectangles
    slot_rects = [pygame.Rect(int(100 * scale + i * 100 * scale), int(200 * scale), int(80 * scale), int(80 * scale)) for i in range(6)]
    start_button_rect = pygame.Rect(int(300 * scale), int(400 * scale), int(200 * scale), int(50 * scale))

    # Load and scale images
    player_images_scaled = [pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale))) for img in player_images_original]
    cpu_image_scaled = pygame.transform.smoothscale(cpu_image_original, (int(80 * scale), int(80 * scale)))
    not_set_image = pygame.image.load(load_asset("Assets/Images/Players/Player Not.png"))
    not_set_image_scaled = pygame.transform.smoothscale(not_set_image, (int(80 * scale), int(80 * scale)))
    difficulty_images_scaled = {
        key: pygame.transform.smoothscale(img, (int(30 * scale), int(30 * scale)))
        for key, img in difficulty_images_original.items()
    }

    while True:
        # Calculate difficulty rectangles for CPU slots
        difficulty_rects = []
        for i, state in enumerate(player_states):
            if state == 2:
                slot_rect = slot_rects[i]
                diff_x = int(slot_rect.centerx - 15 * scale)  # Center horizontally (30/2 = 15)
                diff_y = int(290 * scale)  # Below the slot
                diff_rect = pygame.Rect(diff_x, diff_y, int(30 * scale), int(30 * scale))
                difficulty_rects.append((i, diff_rect))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                return None  # Restart with new scale on resize
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button == 1:  # Left-click to toggle state
                    for i, rect in enumerate(slot_rects):
                        if rect.collidepoint(pos):
                            toggle_player_state(i, player_states, difficulties)
                elif event.button == 3:  # Right-click to cycle difficulty
                    for i, diff_rect in difficulty_rects:
                        if diff_rect.collidepoint(pos):
                            cycle_difficulty(i, difficulties)
                            break
                if start_button_rect.collidepoint(pos) and any(state > 0 for state in player_states):
                    selected_players = []
                    for i, state in enumerate(player_states):
                        if state == 1:
                            selected_players.append((i, False, None))  # Human
                        elif state == 2:
                            selected_players.append((i, True, difficulties[i]))  # CPU
                    super_mario_sound.play()
                    return selected_players
            elif event.type == pygame.KEYDOWN:
                if event.key >= pygame.K_1 and event.key <= pygame.K_6:
                    index = event.key - pygame.K_1
                    if index < len(player_states):
                        toggle_player_state(index, player_states, difficulties)

        # Draw the selection screen
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
            label = font.render(f"P{i+1}", True, BLACK)
            screen.blit(label, (rect.centerx - label.get_width() // 2, rect.top - int(20 * scale)))

        # Draw Start button
        pygame.draw.rect(screen, GREEN if any(state > 0 for state in player_states) else GRAY, start_button_rect)
        text = font.render("Start Game", True, BLACK)
        screen.blit(text, text.get_rect(center=start_button_rect.center))

        pygame.display.flip()

def main():
    global SCREEN_WIDTH
    scale = 1.0
    connect_sound.play()
    selected_players = select_players(scale)
    while selected_players is None:
        selected_players = select_players(scale)

    players = [Player(i, color_idx, is_computer, difficulty) for i, (color_idx, is_computer, difficulty) in enumerate(selected_players)]
    for player in players:
        player.position_history.append(player.position)
    game_state = {
        'current_player': 0,
        'message': "",
        'show_quiz': False,
        'show_path_choice': False,
        'rolling_dice': False,
        'dice_start_time': 0,
        'dice_roll': 0,
        'final_dice_roll': 1,
        'pop_played': False,
        'quiz_state': None,
        'finish_order': [],
        'players': players,
        'last_scale': scale
    }
    clock = pygame.time.Clock()

    # Pre-scale images
    tile_images_scaled = {
        key: pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale)))
        for key, img in tile_images_original.items() if key != 'F'
    }
    finish_rotated = pygame.transform.rotate(tile_images_original['F'], 90)
    tile_images_scaled['F'] = pygame.transform.smoothscale(finish_rotated, (int(50 * scale), int(100 * scale)))
    player_images_scaled = [pygame.transform.smoothscale(img, (int(40 * scale), int(40 * scale))) for img in player_images_original]
    for img in player_images_scaled:
        img.set_alpha(191)
    cpu_image_scaled = pygame.transform.smoothscale(cpu_image_original, (int(40 * scale), int(40 * scale)))
    cpu_image_scaled.set_alpha(191)
    dice_images_scaled = [pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale))) for img in dice_images_original]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                scale_x = SCREEN_WIDTH / ORIGINAL_WIDTH
                scale_y = SCREEN_HEIGHT / ORIGINAL_HEIGHT
                scale = min(scale_x, scale_y)
                font = pygame.font.SysFont(None, int(24 * scale))
                tile_images_scaled = {
                    key: pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale)))
                    for key, img in tile_images_original.items() if key != 'F'
                }
                finish_rotated = pygame.transform.rotate(tile_images_original['F'], 90)
                tile_images_scaled['F'] = pygame.transform.smoothscale(finish_rotated, (int(50 * scale), int(100 * scale)))
                player_images_scaled = [pygame.transform.smoothscale(img, (int(40 * scale), int(40 * scale))) for img in player_images_original]
                for img in player_images_scaled:
                    img.set_alpha(191)
                cpu_image_scaled = pygame.transform.smoothscale(cpu_image_original, (int(40 * scale), int(40 * scale)))
                cpu_image_scaled.set_alpha(191)
                dice_images_scaled = [pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale))) for img in dice_images_original]
                game_state['last_scale'] = scale
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                roll_button = pygame.Rect(int(600 * scale), int(500 * scale), int(150 * scale), int(50 * scale))
                dice_rect = pygame.Rect(int(350 * scale), int(250 * scale), int(50 * scale), int(50 * scale))
                current_player = players[game_state['current_player']]
                if (roll_button.collidepoint(pos) or dice_rect.collidepoint(pos)) and not game_state.get('show_quiz', False) and \
                       not game_state.get('show_path_choice', False) and not game_state.get('rolling_dice', False) and not current_player.has_rolled:
                    message, moved = move_player(current_player, game_state)
                    game_state['message'] = message
                if not game_state.get('rolling_dice', False):
                    dev_buttons = [
                        pygame.Rect(int(600 * scale), int(450 * scale), int(150 * scale), int(40 * scale)),
                        pygame.Rect(int(600 * scale), int(400 * scale), int(150 * scale), int(40 * scale)),
                        pygame.Rect(int(600 * scale), int(350 * scale), int(150 * scale), int(40 * scale)),
                        pygame.Rect(int(600 * scale), int(300 * scale), int(150 * scale), int(40 * scale)),
                        pygame.Rect(int(600 * scale), int(250 * scale), int(150 * scale), int(40 * scale)),
                        pygame.Rect(int(600 * scale), int(200 * scale), int(150 * scale), int(40 * scale)),
                        pygame.Rect(int(600 * scale), int(150 * scale), int(150 * scale), int(40 * scale)),
                    ]
                    if dev_buttons[0].collidepoint(pos):
                        if not current_player.finished and not current_player.in_jail:
                            movement_path = get_movement_path(current_player.position, 1)
                            anim = {
                                'player': current_player,
                                'path': movement_path,
                                'index': 0,
                                'last_time': time.time(),
                                'message': "Dev: Moving forward 1 space.",
                                'is_initial_move': True,
                                'delay': 0.5
                            }
                            current_player.active_animations.append(anim)
                            glug_sound.play()
                    elif dev_buttons[1].collidepoint(pos):
                        if not current_player.finished and not current_player.in_jail and current_player.position + 1 < len(squares):
                            movement_path = [current_player.position, current_player.position + 1]
                            anim = {
                                'player': current_player,
                                'path': movement_path,
                                'index': 0,
                                'last_time': time.time(),
                                'message': "Dev: Jumping forward 1 space.",
                                'is_initial_move': False,
                                'delay': 0.5
                            }
                            current_player.active_animations.append(anim)
                            jump_sound.play()
                    elif dev_buttons[2].collidepoint(pos):
                        if not current_player.finished and not current_player.in_jail:
                            current_player.prev_position = current_player.position
                            anim = {
                                'player': current_player,
                                'start_pos': (current_player.current_x, current_player.current_y),
                                'end_pos': (400, 200),
                                'steps': 20,
                                'current_step': 0,
                                'last_time': time.time(),
                                'message': "Dev: Moving to jail.",
                                'is_jail_move': True,
                                'delay': 0.05
                            }
                            current_player.active_animations.append(anim)
                            whiz_sound.play()
                    elif dev_buttons[3].collidepoint(pos):
                        if current_player.in_jail:
                            current_player.in_jail = False
                            anim = {
                                'player': current_player,
                                'start_pos': (400, 200),
                                'end_pos': squares_coords[current_player.prev_position],
                                'steps': 20,
                                'current_step': 0,
                                'last_time': time.time(),
                                'message': "Dev: Escaping jail.",
                                'is_jail_move': True,
                                'delay': 0.05
                            }
                            current_player.active_animations.append(anim)
                            head_shake_sound.play()
                    elif dev_buttons[4].collidepoint(pos):
                        if not current_player.finished and not game_state.get('show_quiz', False):
                            global quiz_card_index
                            if quiz_card_index < len(quiz_cards):
                                question, options, correct = quiz_cards[quiz_card_index]
                                game_state['quiz_question'] = (question, options, correct)
                                game_state['show_quiz'] = True
                                game_state['quiz_state'] = 'growing'
                                game_state['quiz_start_time'] = time.time()
                                game_state['pop_played'] = False
                                drum_machine_sound.play()
                                quiz_card_index = (quiz_card_index + 1) % len(quiz_cards)
                                game_state['message'] = "Dev: Quiz card triggered."
                    elif dev_buttons[5].collidepoint(pos):
                        if not current_player.finished:
                            global bonus_card_index
                            if bonus_card_index < len(bonus_cards):
                                bonus = bonus_cards[bonus_card_index]
                                bonus_card_index = (bonus_card_index + 1) % len(bonus_cards)
                                drip_drop_sound.play()
                                game_state['bonus_delay_start'] = time.time()
                                game_state['bonus_action'] = bonus
                                game_state['message'] = f"Dev: Bonus card - {bonus}. Action will be applied in 1.5 seconds."
                    elif dev_buttons[6].collidepoint(pos):
                        if not current_player.finished and not current_player.in_jail and current_player.position != 0:
                            num_back = 2
                            if len(current_player.position_history) > num_back:
                                target_pos = current_player.position_history[-num_back - 1]
                                movement_path = current_player.position_history[-1:-num_back - 2:-1]
                            else:
                                target_pos = 0
                                movement_path = current_player.position_history[::-1] + [0] * (num_back - len(current_player.position_history) + 1)
                            anim = {
                                'player': current_player,
                                'path': movement_path,
                                'index': 0,
                                'last_time': time.time(),
                                'message': "Dev: Moving back 2 spaces.",
                                'is_backwards': True,
                                'delay': 0.5
                            }
                            current_player.active_animations.append(anim)
                            wobble_sound.play()

                if game_state.get('show_quiz', False) and 'quiz_buttons' in game_state:
                    for button, option_index in game_state['quiz_buttons']:
                        if button.collidepoint(pos):
                            _, _, correct = game_state['quiz_question']
                            if option_index == correct:
                                apply_quiz_effect(current_player, True, game_state, scale)
                            else:
                                apply_quiz_effect(current_player, False, game_state, scale)
                            del game_state['quiz_buttons']

                if game_state.get('show_path_choice', False) and 'path_buttons' in game_state:
                    for button, choice in game_state['path_buttons']:
                        if button.collidepoint(pos):
                            player = game_state['pending_move']['player']
                            movement_path = [player.position, choice]
                            anim = {
                                'player': player,
                                'path': movement_path,
                                'index': 0,
                                'last_time': time.time(),
                                'message': "Moving to chosen path.",
                                'is_initial_move': False,
                                'delay': 0.5
                            }
                            player.active_animations.append(anim)
                            indigogo_sound.play()
                            player.turn_ended = True
                            game_state['show_path_choice'] = False
                            del game_state['path_buttons']
                            del game_state['pending_move']

        if update_animation(game_state, scale):
            pass
        elif 'animation' not in game_state and not game_state.get('show_quiz', False) and \
             not game_state.get('show_path_choice', False) and not game_state.get('rolling_dice', False):
            current_player = players[game_state['current_player']]
            if current_player.is_computer and not current_player.has_rolled:
                if not current_player.finished:
                    if current_player.in_jail:
                        message, moved = move_player(current_player, game_state)
                        game_state['message'] = message
                    elif game_state.get('show_path_choice', False):
                        choices = game_state['pending_move']['choices']
                        choice = random.choice(choices)
                        movement_path = [current_player.position, choice]
                        anim = {
                            'player': current_player,
                            'path': movement_path,
                            'index': 0,
                            'last_time': time.time(),
                            'message': "Moving to chosen path.",
                            'is_initial_move': False,
                            'delay': 0.5
                        }
                        current_player.active_animations.append(anim)
                        indigogo_sound.play()
                        game_state['show_path_choice'] = False
                        del game_state['path_buttons']
                        del game_state['pending_move']
                    elif game_state.get('show_quiz', False):
                        if current_player.difficulty == 'easy':
                            correct_prob = 0.2
                        elif current_player.difficulty == 'hard':
                            correct_prob = 0.8
                        else:
                            correct_prob = 0.5
                        correct = random.random() < correct_prob
                        apply_quiz_effect(current_player, correct, game_state, scale)
                        del game_state['quiz_buttons']
                    else:
                        message, moved = move_player(current_player, game_state)
                        game_state['message'] = message
            elif current_player.position == len(squares) - 1 and not current_player.finished:
                current_player.finished = True
                game_state['finish_order'].append(current_player)
                if len(game_state['finish_order']) == len(players):
                    fairlin_round1_sound.play()
                    scaled_x = lambda idx: int(100 * scale + idx * 50 * scale)
                    scaled_y = lambda _: int(500 * scale)
                    for idx, fin_player in enumerate(game_state['finish_order']):
                        fin_player.current_x = scaled_x(idx)
                        fin_player.current_y = scaled_y(idx)
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

        if 'bonus_delay_start' in game_state and time.time() - game_state['bonus_delay_start'] >= 1.5:
            bonus = game_state['bonus_action']
            player = players[game_state['current_player']]
            if bonus == "Go back 1 space":
                if len(player.position_history) > 1:
                    target_pos = player.position_history[-2]
                    movement_path = [player.position, target_pos]
                else:
                    target_pos = 0
                    movement_path = [player.position, 0]
                anim = {
                    'player': player,
                    'path': movement_path,
                    'index': 0,
                    'last_time': time.time(),
                    'message': f"Player {player.id + 1} moving back 1 space from bonus card.",
                    'is_backwards': True,
                    'delay': 0.5
                }
                player.active_animations.append(anim)
            elif bonus == "Move forward 2 spaces":
                movement_path = get_movement_path(player.position, 2)
                anim = {
                    'player': player,
                    'path': movement_path,
                    'index': 0,
                    'last_time': time.time(),
                    'message': f"Player {player.id + 1} moving forward 2 spaces from bonus card.",
                    'is_initial_move': False,
                    'delay': 0.5
                }
                player.active_animations.append(anim)
            elif bonus == "Roll again":
                player.has_rolled = False
                game_state['message'] = f"Player {player.id + 1} gets bonus card: Roll again."
            elif bonus == "Go to jail":
                player.prev_position = player.position
                anim = {
                    'player': player,
                    'start_pos': (player.current_x, player.current_y),
                    'end_pos': (400, 200),
                    'steps': 20,
                    'current_step': 0,
                    'last_time': time.time(),
                    'message': f"Player {player.id + 1} sent to jail by bonus card.",
                    'is_jail_move': True,
                    'delay': 0.05
                }
                player.active_animations.append(anim)
                whiz_sound.play()
            del game_state['bonus_delay_start']
            del game_state['bonus_action']

        draw_board(players, game_state, scale, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
