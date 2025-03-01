import pygame
import random
import time
import sys
import os  # Add this import

# Initialize Pygame
pygame.init()

# Original screen settings
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = 800, 600
SCREEN_WIDTH, SCREEN_HEIGHT = ORIGINAL_WIDTH, ORIGINAL_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Rock-Sickle")

# Set the window icon (add these lines)
icon_path = '/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Icons/RockSickle.png'  # Change to PNG format
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)

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

# Load original images without scaling
forward_one_original = pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Tiles/Forward One.png')
back_two_original = pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Tiles/Back Two.png')

tile_images_original = {
    'Go': pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Tiles/Go.png'),
    '1_East': forward_one_original,
    '1_South': pygame.transform.rotate(forward_one_original, 90),
    '1_West': pygame.transform.rotate(forward_one_original, 180),
    '1_North': pygame.transform.rotate(forward_one_original, 270),
    '-2_East': pygame.transform.rotate(back_two_original, 180),
    '-2_South': pygame.transform.rotate(back_two_original, 270),
    '-2_West': back_two_original,
    '-2_North': pygame.transform.rotate(back_two_original, 90),
    'B': pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Tiles/Bonus.png'),
    'Q': pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Tiles/Quiz.png'),
    'J': pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Tiles/Go To Jail.png'),
    '0': pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Tiles/Safe Space.png'),
    'P': pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Tiles/Choose Your Path.png'),
    'F': pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Tiles/Finish.png'),
    'Jail': pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Tiles/Jail Location.png'),
}

player_image_paths = [
    '/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Players/Player Red.png',
    '/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Players/Player Orange.png',
    '/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Players/Player Yellow.png',
    '/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Players/Player Green.png',
    '/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Players/Player Blue.png',
    '/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Players/Player Purple.png',
]
player_images_original = [pygame.image.load(img) for img in player_image_paths]
cpu_image_original = pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Players/Player CPU.png')

dice_images_original = [
    pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Dices/1.png'),
    pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Dices/2.png'),
    pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Dices/3.png'),
    pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Dices/4.png'),
    pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Dices/5.png'),
    pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Dices/6.png'),
]

# Load difficulty button images (not scaled initially)
easy_button_image = pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/DifficultyButtons/1Baby.png')
normal_button_image = pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/DifficultyButtons/3Consentrated.png')
hard_button_image = pygame.image.load('/Users/harrison/Desktop/Rock_Sickle/Assets/Images/DifficultyButtons/4Angery.png')

# Load Audio Assets with Error Handling
try:
    roll_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Drum Roll (Roll the Dice).wav')
    glug_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Glug (Moving).wav')
    bonk_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Bonk (Stay In Jail).wav')
    head_shake_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Head Shake (Exit Jail).wav')
    whiz_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Whiz2 (Moving to Jail).wav')
    drip_drop_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Drip Drop (Pick up Bonus Card).wav')
    drum_machine_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Drum Machine (Pick up Quiz Card).wav')
    win_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Odesong (Win).wav')
    pop_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/pop (Anser Buttons Appear).wav')
    bing_bong_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/bing_bong (Incorrect Quiz Answer).wav')
    connect_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Connect.wav')
    disconnect_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Disconnect (Put Card Away).wav')
    indigogo_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/indigogo (Path Chosen).wav')
    jump_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Jump (Forward a Space).wav')
    mac_os_dinbg_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/mac_os_dinbg (Quiz Answer Correct).wav')
    mac_os_uh_ohh_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/mac_os_uh_ohh (Sent to Jail by Bonus Card).wav')
    super_mario_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/super_mario_64_soundtrack_correct_solution (Amount of Players has been Chosen).wav')
    wobble_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Wobble (Back a Space).wav')
    fairlin_round1_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/SE1_EVT_FAIRLIN_ROUND1 (Win).wav')
    pong_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Pong (Player Not Set).wav')
    voltage_easy_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Voltage (Easy CPU Player Selected).wav')
    voltage_normal_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Voltage2 (Normal CPU Player Selected).wav')
    voltage_hard_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Voltage3 (Hard CPU Player Selected).wav')
    whit_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Whit (Player Set).wav')
except pygame.error as e:
    print(f"Error loading sound file: {e}")

# Font (initial size, will be scaled later)
font = pygame.font.SysFont(None, 24)

# Board squares
squares = [
    'Go', '1', '0', 'Q', '-2', 'J', '1', 'B', '0', '0',
    'J', '0', '1', '-2', '1', '-2', '0',  # Positions 10-16: '0', '1', '-2', '1', '-2', '0'
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
        self.difficulty = difficulty  # None for humans, 'easy', 'normal', or 'hard' for CPUs
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
        self.active_animations = []  # Track active animations for this player

def roll_die(difficulty=None):
    if difficulty == 'easy':
        return random.choice([1, 1, 2, 2, 3, 4])  # Biased towards lower rolls
    elif difficulty == 'hard':
        return random.choice([3, 4, 5, 6, 6, 6])  # Biased towards higher rolls
    else:  # Normal difficulty or human player
        return random.randint(1, 6)  # Normal random roll

def interpolate_position(start_pos, end_pos, steps, current_step):
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    x = start_x + (end_x - start_x) * current_step / steps
    y = start_y + (end_y - start_y) * current_step / steps
    return x, y

def apply_effect(player, square_type, game_state, scale):
    global bonus_card_index, quiz_card_index  # Declare globals to prevent UnboundLocalError
    message = ""
    chain = False
    if square_type == '0':
        message = "Safe space. Turn ends."
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
            message = "Move forward 1 space."
            chain = True  # Chain to next effect
            player.turn_ended = False  # Only end turn after all effects
        else:
            message = "Cannot move forward beyond board."
            player.turn_ended = True
    elif square_type == '-2':
        if player.position == 0 or len(player.position_history) < 2:
            message = "Cannot move back from start or insufficient history."
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
            message = "Move back 2 spaces."
            chain = True  # Chain to next effect
            player.turn_ended = False  # Only end turn after all effects
    elif square_type == 'B':
        if bonus_card_index < len(bonus_cards):
            bonus = bonus_cards[bonus_card_index]
            bonus_card_index = (bonus_card_index + 1) % len(bonus_cards)
            drip_drop_sound.play()
            game_state['bonus_delay_start'] = time.time()
            game_state['bonus_action'] = bonus
            message = f"Bonus card: {bonus}. Action will be applied in 1.5 seconds."
            player.turn_ended = True
        else:
            message = "No more bonus cards."
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
            message = "Answer the quiz question."
        else:
            message = "No more quiz cards."
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
            'delay': 0.05
        }
        player.active_animations.append(anim)
        message = "Moving to jail. Roll even to escape on next turn."
        player.turn_ended = True
    elif square_type == 'P':
        game_state['show_path_choice'] = True
        game_state['pending_move'] = {'player': player, 'choices': next_positions[player.position]}
        message = "Choose your path."
        player.turn_ended = True
    elif square_type == 'F':
        player.finished = True
        player.position = len(squares) - 1
        win_sound.play()
        message = "Player finished!"
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
        message = "Start position."
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
            path.append(current_pos)  # Stop at 'P' for path choice
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
        game_state['message'] = "Correct! Turn ends."
        mac_os_dinbg_sound.play()
        player.turn_ended = True
    else:
        game_state['message'] = "Incorrect. Move back 2 spaces."
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
            anim = player.active_animations[0]  # Process the first animation in the queue
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
                        elif anim['message'].startswith("Rolled"):  # Jail escape
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
                        # Play sound only when moving to a new position
                        if anim['index'] > 0:  # Avoid playing sound on the initial position
                            if 'is_backwards' in anim:
                                wobble_sound.play()
                            elif 'is_initial_move' in anim and anim['is_initial_move']:
                                glug_sound.play()
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

def scale_images(scale):
    tile_images_scaled = {
        key: pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale)))
        for key, img in tile_images_original.items() if key != 'F'
    }
    scaled_finish = pygame.transform.smoothscale(tile_images_original['F'], (int(100 * scale), int(50 * scale)))
    tile_images_scaled['F'] = pygame.transform.rotate(scaled_finish, 90)
    
    player_images_scaled = [pygame.transform.smoothscale(img, (int(40 * scale), int(40 * scale))) for img in player_images_original]
    for img in player_images_scaled:
        img.set_alpha(191)
    
    cpu_image_scaled = pygame.transform.smoothscale(cpu_image_original, (int(40 * scale), int(40 * scale)))
    cpu_image_scaled.set_alpha(191)
    
    dice_images_scaled = [pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale))) for img in dice_images_original]
    
    easy_button_scaled = pygame.transform.smoothscale(easy_button_image, (int(80 * scale), int(30 * scale)))
    normal_button_scaled = pygame.transform.smoothscale(normal_button_image, (int(80 * scale), int(30 * scale)))
    hard_button_scaled = pygame.transform.smoothscale(hard_button_image, (int(80 * scale), int(30 * scale)))
    
    return (tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled,
            easy_button_scaled, normal_button_scaled, hard_button_scaled)

def draw_board(players, game_state, scale, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled,
               easy_button_scaled, normal_button_scaled, hard_button_scaled):
    global SCREEN_WIDTH
    screen.fill(GRAY)
    for i, square in enumerate(squares):
        x, y = int(squares_coords[i][0] * scale), int(squares_coords[i][1] * scale)
        if square in ['Go', 'B', 'Q', 'J', '0', 'P', 'F']:
            img = tile_images_scaled[square]
        elif square == '1':
            if i in [1, 6]:  # East
                img = tile_images_scaled['1_East']
            elif i in [12, 14]:  # South
                img = tile_images_scaled['1_North']
            elif i == 24:  # North
                img = tile_images_scaled['1_West']
            elif i == 31:  # West
                img = tile_images_scaled['1_West']
            else:
                img = tile_images_scaled['1_East']  # Default fallback
        elif square == '-2':
            if i == 4:  # East
                img = tile_images_scaled['-2_West']
            elif i in [13, 15]:  # South
                img = tile_images_scaled['-2_South']
            elif i == 19:  # West
                img = tile_images_scaled['-2_East']
            elif i in [28, 33, 35]:  # North
                img = tile_images_scaled['-2_North']
            else:
                img = tile_images_scaled['-2_West']  # Default fallback
        screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))

    jail_x, jail_y = int(400 * scale), int(200 * scale)
    screen.blit(tile_images_scaled['Jail'], (jail_x - tile_images_scaled['Jail'].get_width() // 2, jail_y - tile_images_scaled['Jail'].get_height() // 2))

    if 'last_scale' not in game_state or game_state['last_scale'] != scale:
        player_images_scaled = [pygame.transform.smoothscale(img, (int(40 * scale), int(40 * scale))) for img in player_images_original]
        for img in player_images_scaled:
            img.set_alpha(191)
        cpu_image_scaled = pygame.transform.smoothscale(cpu_image_original, (int(40 * scale), int(40 * scale)))
        cpu_image_scaled.set_alpha(191)
        game_state['last_scale'] = scale
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

    # Turn Indicator UI (moved above dev buttons)
    current_id = game_state['current_player']
    next_id = (current_id + 1) % len(players)
    while players[next_id].finished and len(game_state['finish_order']) < len(players):
        next_id = (next_id + 1) % len(players)
    current_text = f"Current Turn: Player {current_id + 1}"
    if players[current_id].is_computer:
        current_text += " (CPU)"
    next_text = f"Next Turn: Player {next_id + 1}"
    if players[next_id].is_computer:
        next_text += " (CPU)"
    current_surface = font.render(current_text, True, BLACK)
    next_surface = font.render(next_text, True, BLACK)
    screen.blit(current_surface, (SCREEN_WIDTH // 2 - current_surface.get_width() // 2, int(100 * scale)))
    screen.blit(next_surface, (SCREEN_WIDTH // 2 - next_surface.get_width() // 2, int(130 * scale)))

    if 'message' in game_state:
        text = font.render(game_state['message'], True, BLACK)
        screen.blit(text, (int(50 * scale), int(500 * scale)))

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

    if 'last_scale' not in game_state or game_state['last_scale'] != scale:
        dice_images_scaled = [pygame.transform.smoothscale(img, (int(50 * scale), int(50 * scale))) for img in dice_images_original]
        game_state['last_scale'] = scale
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
                if roll % 2 == 0:  # Normal jail escape rule
                    current_player.in_jail = False
                    anim = {
                        'player': current_player,
                        'start_pos': (400, 200),
                        'end_pos': squares_coords[current_player.prev_position],
                        'steps': 20,
                        'current_step': 0,
                        'last_time': time.time(),
                        'message': f"Rolled {roll} (even). Escaping jail.",
                        'is_jail_move': True,
                        'delay': 0.05
                    }
                    current_player.active_animations.append(anim)
                    head_shake_sound.play()
                    current_player.turn_ended = True
                else:
                    bonk_sound.play()
                    game_state['message'] = f"Rolled {roll} (odd). Still in jail."
                    current_player.turn_ended = True
            else:
                movement_path = get_movement_path(current_player.position, roll)
                anim = {
                    'player': current_player,
                    'path': movement_path,
                    'index': 0,
                    'last_time': time.time(),
                    'message': f"Rolled {roll}. Moving {roll} spaces.",
                    'is_initial_move': True,
                    'delay': 0.5
                }
                current_player.active_animations.append(anim)
    elif 'final_dice_roll' in game_state:  # Updated to remove syntax warning
        dice_face = dice_images_scaled[game_state['final_dice_roll'] - 1]
        screen.blit(dice_face, dice_rect.topleft)

def select_players(scale):
    player_states = [1, 0, 0, 0, 0, 0]
    difficulties = [None, None, None, None, None, None]
    slot_rects = [pygame.Rect(int(100 * scale + i * 100 * scale), int(200 * scale), int(80 * scale), int(80 * scale)) for i in range(6)]
    difficulty_rects = [
        [pygame.Rect(int(100 * scale + i * 100 * scale), int(300 * scale), int(80 * scale), int(30 * scale)),
         pygame.Rect(int(100 * scale + i * 100 * scale), int(340 * scale), int(80 * scale), int(30 * scale)),
         pygame.Rect(int(100 * scale + i * 100 * scale), int(380 * scale), int(80 * scale), int(30 * scale))]
        for i in range(6)
    ]
    start_button_rect = pygame.Rect(int(300 * scale), int(400 * scale), int(200 * scale), int(50 * scale))

    _, player_images_scaled, cpu_image_scaled, _, easy_button_scaled, normal_button_scaled, hard_button_scaled = scale_images(scale)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                return None  # Exit and restart to handle resize
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for i, rect in enumerate(slot_rects):
                    if rect.collidepoint(pos) and event.button == 1:
                        old_state = player_states[i]
                        player_states[i] = (player_states[i] + 1) % 3
                        if player_states[i] == 0:
                            pong_sound.play()
                        elif player_states[i] == 1:
                            whit_sound.play()
                        elif player_states[i] == 2:
                            if difficulties[i] is None:  # First switch to CPU
                                difficulties[i] = 'normal'
                                voltage_normal_sound.play()
                            elif difficulties[i] == 'easy':
                                voltage_easy_sound.play()
                            elif difficulties[i] == 'normal':
                                voltage_normal_sound.play()
                            elif difficulties[i] == 'hard':
                                voltage_hard_sound.play()
                for i, (easy, med, hard) in enumerate(difficulty_rects):
                    if player_states[i] == 2:
                        if easy.collidepoint(pos) and event.button == 3:
                            difficulties[i] = 'easy'
                            voltage_easy_sound.play()
                        elif med.collidepoint(pos) and event.button == 3:
                            difficulties[i] = 'normal'
                            voltage_normal_sound.play()
                        elif hard.collidepoint(pos) and event.button == 3:
                            difficulties[i] = 'hard'
                            voltage_hard_sound.play()
                if start_button_rect.collidepoint(pos) and any(state > 0 for state in player_states):
                    selected_players = []
                    for i, state in enumerate(player_states):
                        if state == 1:
                            selected_players.append((i, False, None))
                        elif state == 2:
                            selected_players.append((i, True, difficulties[i]))
                    super_mario_sound.play()
                    return selected_players

        screen.fill(GRAY)
        for i, (rect, state) in enumerate(zip(slot_rects, player_states)):
            if state == 0:
                text = font.render("Not Set", True, BLACK)
                screen.blit(text, text.get_rect(center=rect.center))
            elif state == 1:
                screen.blit(player_images_scaled[i], rect.topleft)
            elif state == 2:
                screen.blit(cpu_image_scaled, rect.topleft)
            label = font.render(f"P{i+1}", True, BLACK)
            screen.blit(label, (rect.centerx - label.get_width() // 2, rect.top - int(20 * scale)))

        for i, (easy_rect, med_rect, hard_rect) in enumerate(difficulty_rects):
            if player_states[i] == 2:
                screen.blit(easy_button_scaled, easy_rect.topleft)
                screen.blit(normal_button_scaled, med_rect.topleft)
                screen.blit(hard_button_scaled, hard_rect.topleft)
                if difficulties[i] == 'easy':
                    pygame.draw.rect(screen, GREEN, easy_rect, 3)
                elif difficulties[i] == 'normal':
                    pygame.draw.rect(screen, YELLOW, med_rect, 3)
                elif difficulties[i] == 'hard':
                    pygame.draw.rect(screen, RED, hard_rect, 3)

        pygame.draw.rect(screen, GREEN if any(state > 0 for state in player_states) else GRAY, start_button_rect)
        text = font.render("Start Game", True, BLACK)
        screen.blit(text, text.get_rect(center=start_button_rect.center))

        pygame.display.flip()

def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT, font
    scale = 1.0
    connect_sound.play()
    selected_players = select_players(scale)
    while selected_players is None:  # Restart if window resized during player selection
        selected_players = select_players(scale)

    players = [Player(i, color_idx, is_computer, difficulty) for i, (color_idx, is_computer, difficulty) in enumerate(selected_players)]
    for player in players:
        player.position_history.append(player.position)  # Initial position in history
    game_state = {
        'current_player': 0,
        'message': "",
        'show_quiz': False,
        'show_path_choice': False,
        'rolling_dice': False,
        'dice_start_time': 0,
        'dice_roll': 0,
        'final_dice_roll': 1,  # Start with die visible (face 1)
        'pop_played': False,
        'quiz_state': None,
        'finish_order': [],
        'players': players,
        'last_scale': scale  # Initialize last_scale to avoid rescaling on first draw
    }
    clock = pygame.time.Clock()

    # Pre-scale images for initial draw
    (tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled,
     easy_button_scaled, normal_button_scaled, hard_button_scaled) = scale_images(scale)

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
                (tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled,
                 easy_button_scaled, normal_button_scaled, hard_button_scaled) = scale_images(scale)
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
                            player.turn_ended = True  # Path choice ends turn
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
                        choice = random.choice(choices)  # Random path choice for CPU
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
                        else:  # normal
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

        # Check for bonus delay and apply bonus action after 1.5 seconds
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
                    'message': "Moving back 1 space from bonus card.",
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
                    'message': "Moving forward 2 spaces from bonus card.",
                    'is_initial_move': False,
                    'delay': 0.5
                }
                player.active_animations.append(anim)
            elif bonus == "Roll again":
                player.has_rolled = False  # Allow another roll
                game_state['message'] = "Bonus card: Roll again."
            elif bonus == "Go to jail":
                player.prev_position = player.position
                anim = {
                    'player': player,
                    'start_pos': (player.current_x, player.current_y),
                    'end_pos': (400, 200),
                    'steps': 20,
                    'current_step': 0,
                    'last_time': time.time(),
                    'message': "Bonus card: Sent to jail.",
                    'is_jail_move': True,
                    'delay': 0.05
                }
                player.active_animations.append(anim)
                whiz_sound.play()
            del game_state['bonus_delay_start']
            del game_state['bonus_action']

        draw_board(players, game_state, scale, tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled,
                   easy_button_scaled, normal_button_scaled, hard_button_scaled)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()