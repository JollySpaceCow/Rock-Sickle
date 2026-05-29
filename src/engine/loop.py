import pygame
import random
import time
import os
import logging
from src.core import audio, quiz_tts
from src.core.progress import load_game_progress, save_game_progress, increment_stat
from src.core.assets import AssetRegistry, load_and_convert
from src.constants import (
    ORIGINAL_WIDTH, ORIGINAL_HEIGHT,
    GAP_BETWEEN_TILES, JAIL_SIZE, DIE_POS, player_colours,
    CLASSIC_JAIL_POS, EXPERT_JAIL_POS, SECRET_JAIL_POS
)
from src.game.board import get_board_squares, get_classic_squares_coords, get_expert_squares_coords, get_secret_squares_coords
from src.game.mechanics import roll_die, interpolate_position, get_movement_path, get_movement_path_with_choice
from src.game.achievements import check_achievement_completion, get_achievement_by_id
from src.ui.renderer import draw_board, format_time, display_player_timers
from src.ui.button_anim import update_ui_buttons_fly_in
from src.ui.gallery import render_achievements_pane
from src.ui import camera
from src.engine import cpu, input, quiz
import src.game.cards as cards

logger = logging.getLogger()

def player_holds_jail_free_card(game_state):
    """Return True when the single jail-free card is already in circulation."""
    return any(player.has_jail_free_card for player in game_state.get('players', []))

def draw_expert_bonus_card(game_state):
    """Draw the next expert bonus card, skipping Jail Free while it is held."""
    deck_size = len(cards.expert_bonus_cards)
    if deck_size == 0:
        return None

    jail_free_in_circulation = player_holds_jail_free_card(game_state)
    for _ in range(deck_size):
        bonus = cards.expert_bonus_cards[cards.expert_bonus_card_index]
        cards.expert_bonus_card_index = (cards.expert_bonus_card_index + 1) % deck_size
        effect = cards.parse_bonus_card(bonus)
        if effect[0] != "jail_free" or not jail_free_in_circulation:
            return bonus

    return None

def spend_jail_free_card_if_held(player, game_state):
    """Spend a jail-free card as the player is sent to jail."""
    if not player.has_jail_free_card:
        return False

    player.has_jail_free_card = False
    player.jail_free_card_visible = False
    game_state['jail_free_card_spent_player'] = player.id
    return True

def resize_assets(scale, board_type='Classic'):
    """Resize all game assets based on screen scale while maintaining aspect ratios where necessary.
    
    This function scales assets and stores them in the centralised AssetRegistry.
    Complies with Australian English spelling conventions.
    """
    # Calculate slightly smaller tile size to account for the gaps
    # Different boards use different tile sizes
    if board_type == 'Expert':
        tile_size = int(40 * scale) - int(GAP_BETWEEN_TILES * scale * 0.3)  # Smaller for expert board
    elif board_type == 'Secret':
        tile_size = int(13 * scale)  # Smaller than the 13px spacing to maintain visible gaps between squares
    else:
        tile_size = int(60 * scale) - int(GAP_BETWEEN_TILES * scale * 0.3)  # Regular size for classic board
    
    # Select the appropriate image set based on board type
    tile_images_set = AssetRegistry.board_tile_images[board_type]
    button_set = AssetRegistry.board_buttons[board_type]
    
    # Scale the selected tile images
    tile_images_scaled = {
        key: pygame.transform.smoothscale(img, (tile_size, tile_size))
        for key, img in tile_images_set.items() if key not in ['F', 'Jail']
    }
    
    # Expert board has a different finish image orientation than classic
    if board_type == 'Classic':
        finish_rotated = pygame.transform.rotate(tile_images_set['F'], 90)
        finish_height = int(120 * scale) - int(GAP_BETWEEN_TILES * scale * 0.3)
    elif board_type == 'Secret':
        finish_rotated = tile_images_set['F']
        finish_height = tile_size
    else:  # Expert board
        finish_rotated = tile_images_set['F']
        finish_height = tile_size
    
    tile_images_scaled['F'] = pygame.transform.smoothscale(finish_rotated, (tile_size, finish_height))
    
    # Adjust jail size based on board type
    if board_type == 'Expert':
        jail_size = int(tile_size * 4.1)
    elif board_type == 'Secret':
        jail_size = int(tile_size * 2.0)
    else:
        jail_size = int(tile_size * 1.5)
        
    tile_images_scaled['Jail'] = pygame.transform.smoothscale(tile_images_set['Jail'], (jail_size, jail_size))
    
    # Make player tokens smaller on expert board due to smaller tiles
    player_size = int(50 * scale)
    if board_type == 'Expert':
        player_size = int(35 * scale)
    elif board_type == 'Secret':
        player_size = int(14 * scale)
        
    player_images_scaled = [pygame.transform.smoothscale(img, (player_size, player_size)) for img in AssetRegistry.player_images_original]
    for img in player_images_scaled:
        img.set_alpha(191)
    
    # Scale CPU difficulty images
    cpu_difficulty_images_scaled = {
        key: pygame.transform.smoothscale(img, (player_size, player_size))
        for key, img in AssetRegistry.cpu_difficulty_images_original.items()
    }
    # Set alpha for all CPU difficulty images
    for img in cpu_difficulty_images_scaled.values():
        img.set_alpha(191)
    
    # Default CPU image for backwards compatibility
    cpu_image_scaled = cpu_difficulty_images_scaled['normal']
    
    # Make dice slightly larger
    dice_images_scaled = [pygame.transform.smoothscale(img, (int(55 * scale), int(55 * scale))) for img in AssetRegistry.dice_images_original]
    
    # Use the appropriate button images based on board type
    restart_button_scaled = pygame.transform.smoothscale(button_set['restart'], (int(55 * scale), int(55 * scale)))
    settings_button_scaled = pygame.transform.smoothscale(button_set['settings'], (int(55 * scale), int(55 * scale)))
    achievement_button_scaled = pygame.transform.smoothscale(button_set['achievement'], (int(55 * scale), int(55 * scale)))
    
    # Load and scale the magnify button (magnifying glass icon)
    magnify_button_original = load_and_convert("Assets/Images/Tiles/Magnifying Glass.png")
    if board_type == 'Expert':
        magnify_button_original = load_and_convert("Assets/Images/Tiles/eMagnifying Glass.png")
    magnify_button_scaled = pygame.transform.smoothscale(magnify_button_original, (int(55 * scale), int(55 * scale)))
    
    # Scale bonus images with a slightly larger size
    target_width = int(280 * scale)
    target_height = int(target_width * 3 / 4)
    bonus_result_images_scaled = {
        key: pygame.transform.smoothscale(img, (target_width, target_height))
        for key, img in AssetRegistry.bonus_result_images_original.items()
    }
    
    # Scale card covers
    cover_bonus_scaled = pygame.transform.smoothscale(AssetRegistry.cover_bonus_original, (target_width, target_height))
    cover_quiz_scaled = pygame.transform.smoothscale(AssetRegistry.cover_quiz_original, (target_width, target_height))
    
    # Store in AssetRegistry for clean component access
    AssetRegistry.player_images_scaled = player_images_scaled
    AssetRegistry.cpu_image_scaled = cpu_image_scaled
    AssetRegistry.cpu_difficulty_images_scaled = cpu_difficulty_images_scaled
    AssetRegistry.dice_images_scaled = dice_images_scaled
    AssetRegistry.tile_images_scaled = tile_images_scaled
    AssetRegistry.restart_button_scaled = restart_button_scaled
    AssetRegistry.settings_button_scaled = settings_button_scaled
    AssetRegistry.achievement_button_scaled = achievement_button_scaled
    AssetRegistry.magnify_button_scaled = magnify_button_scaled
    AssetRegistry.bonus_result_images_scaled = bonus_result_images_scaled
    AssetRegistry.cover_bonus_scaled = cover_bonus_scaled
    AssetRegistry.cover_quiz_scaled = cover_quiz_scaled
    
    return tile_images_scaled, player_images_scaled, cpu_image_scaled, dice_images_scaled, restart_button_scaled, settings_button_scaled, achievement_button_scaled, bonus_result_images_scaled, magnify_button_scaled

def apply_effect(player, square_type, game_state, scale, squares, squares_coords, JAIL_POS):
    """Apply the effect of landing on a square.
    
    Complies with Australian English spelling conventions.
    """
    chain = False
    message = ""
    
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
            current_pos = player.position
            last_bonus_pos = game_state.get('last_bonus_position', {}).get(str(player.id), None)
            can_pick_bonus = not game_state.get('bonus_image_key') or current_pos != last_bonus_pos
            
            if can_pick_bonus:
                bonus = draw_expert_bonus_card(game_state)
                if bonus is None:
                    message = f"Player {player.id + 1} can't pick a jail free card while one is already held."
                    player.has_rolled = True
                    return message, chain

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
                message = f"Player {player.id + 1} must finish current bonus card first."
                player.has_rolled = True
        else:
            message = f"Player {player.id + 1} has no bonus cards left."
            player.turn_ended = True
            player.has_rolled = True
    elif square_type == 'Q':
        message = quiz.trigger_quiz(player, game_state)
        player.turn_ended = True
    elif square_type == 'J':
        player.prev_position = player.position
        spent_jail_free = spend_jail_free_card_if_held(player, game_state)
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
            'end_pos': random_jail_pos,
            'steps': 60,
            'current_step': 0,
            'last_time': time.time(),
            'message': "Moving to jail.",
            'is_jail_move': True,
            'delay': 0.0167,  # ~60fps
            'jail_action': 'enter'
        }
        player.active_animations.append(anim)
        if spent_jail_free:
            message = f"Player {player.id + 1} sent to jail and spent their Get Out of Jail Free card."
        else:
            message = f"Player {player.id + 1} sent to jail."
        player.turn_ended = True
        game_state['game_jail_visit'] = True
        
        increment_stat("jail_landings")
    elif square_type == 'P':
        message = f"Player {player.id + 1} chooses a path."
        if game_state.get('spaces_remaining', 0) == 0:
            message = f"Player {player.id + 1} stops at the path choice."
            player.turn_ended = True
            chain = False
        else:
            game_state['show_path_choice_after_roll'] = True
            game_state['roll_for_path_choice'] = game_state['dice_roll']
            chain = True
            player.turn_ended = False
    elif square_type == 'F':
        player.finished = True
        player.position = len(squares) - 1
        
        player.finish_time = time.time()
        player.elapsed_time = player.finish_time - player.start_time
        
        message = f"Player {player.id + 1} finished in {format_time(player.elapsed_time)}!"
        player.turn_ended = True
        if game_state.get('finish_order') is None:
            game_state['finish_order'] = []
        game_state['finish_order'].append(player)
        if len(game_state['finish_order']) == len(game_state['players']):
            audio.win_sound.play()
            audio.fairlin_round1_sound.play()
            game_state['victory_cutscene'] = True
            game_state['victory_cutscene_start'] = time.time()
            
            # Define target positions for victory formation
            finish_x, finish_y = 60, 155 + 2*GAP_BETWEEN_TILES - 5
            victory_x = lambda idx: int((finish_x + 80 + idx * 50) * scale)
            victory_y = lambda _: int(finish_y * scale)
            
            audio.woosh_sound.play()
            for idx, fin_player in enumerate(game_state['finish_order']):
                anim = {
                    'player': fin_player,
                    'start_pos': (fin_player.current_x, fin_player.current_y),
                    'end_pos': (victory_x(idx), victory_y(idx)),
                    'start_time': time.time(),
                    'duration': 2.0,
                    'type': 'victory_glide',
                    'scale_factor': 1.5
                }
                fin_player.victory_scale_factor = 1.0
                fin_player.active_animations.append(anim)
            
            game_progress = load_game_progress()
            game_progress['completed_games'] = game_progress.get('completed_games', 0) + 1
            
            current_board = game_state.get('selected_board')
            if current_board == 'Classic':
                game_progress['classic_board_completed'] = True
                if not game_state.get('game_jail_visit', False):
                    game_progress['classic_no_jail_completed'] = True
                if 'Expert' not in game_progress.get('unlocked_boards', ['Classic']):
                    game_progress['unlocked_boards'].append('Expert')
            elif current_board == 'Expert':
                game_progress['expert_board_completed'] = True
                if not game_state.get('game_jail_visit', False):
                    game_progress['expert_no_jail_completed'] = True
            elif current_board == 'Secret':
                game_progress['secret_board_completed'] = True

            if game_progress['completed_games'] >= 100 and 'Secret' not in game_progress.get('unlocked_boards', []):
                game_progress['unlocked_boards'].append('Secret')
                logger.info("Secret board unlocked!")
            
            winner = game_state['finish_order'][0]
            if not winner.is_computer:
                for p in game_state['players']:
                    if p.is_computer and p.difficulty == 'hard':
                        game_progress['stats']['hard_cpu_defeats'] = game_progress['stats'].get('hard_cpu_defeats', 0) + 1
                        break
            
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
                        game_state['message'] = f"ACHIEVEMENT ACCOMPLISHED: {achievement['title']}!"
            
            save_game_progress(game_progress)
        else:
            audio.finished_sound.play()
    elif square_type == 'Go':
        message = f"Player {player.id + 1} at start."
        player.turn_ended = True
    elif square_type == 'FP':
        message = f"Player {player.id + 1} on Free Parking."
        player.turn_ended = True
        audio.car_horn_sound.play()
        
        game_state['free_parking_effect'] = True
        game_state['free_parking_start_time'] = time.time()
        game_state['free_parking_duration'] = 1.0
        game_state['free_parking_player'] = player
        game_state['free_parking_position'] = player.position
    return message, chain

def move_player(player, game_state):
    """Handle a player rolling the die.
    
    Complies with Australian English spelling conventions.
    """
    if player.finished:
        return "Player has finished.", False
    if player.has_rolled:
        return "Player has already rolled this turn.", False
    if game_state.get('rolling_dice', False):
        return "", False

    player.has_rolled = True
    
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
    return quiz.apply_quiz_effect(player, correct, game_state, scale)

def update_animation(game_state, scale, squares, squares_coords, JAIL_POS):
    """Update all active animations in the game.
    
    Complies with Australian English spelling conventions.
    """
    any_animations = False
    if game_state.get('victory_cutscene', False):
        any_animations = True
    
    # Smoothly interpolate camera state
    factor = 0.1
    
    current_zoom = game_state.get('camera_zoom', 1.0)
    target_zoom = game_state.get('camera_target_zoom', 1.0)
    if abs(current_zoom - target_zoom) > 0.001:
        game_state['camera_zoom'] = current_zoom + (target_zoom - current_zoom) * factor
        any_animations = True
    else:
        game_state['camera_zoom'] = target_zoom
        
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
            game_state.pop('free_parking_effect')
            game_state.pop('free_parking_start_time')
            game_state.pop('free_parking_duration')
            game_state.pop('free_parking_player')
        else:
            any_animations = True
    
    for player in game_state['players']:
        if player.active_animations:
            any_animations = True
            anim = player.active_animations[0]
            current_time = time.time()
            
            if 'is_jail_move' in anim and 'sound_delay' in anim and not anim.get('sound_played', False):
                if current_time >= anim['sound_delay']:
                    audio.whiz_sound.play()
                    anim['sound_played'] = True
                    anim['last_time'] = current_time
            
            if anim.get('type') == 'victory_glide':
                progress = min(1.0, (current_time - anim['start_time']) / anim['duration'])
                t = 1.0 - (1.0 - progress) * (1.0 - progress)
                
                start_x, start_y = anim['start_pos']
                end_x, end_y = anim['end_pos']
                
                anim['player'].current_x = start_x + (end_x - start_x) * t
                anim['player'].current_y = start_y + (end_y - start_y) * t
                
                if progress >= 1.0:
                    player.victory_scale_factor = anim.get('scale_factor', 1.5)
                    player.victory_x = anim['player'].current_x
                    player.victory_y = anim['player'].current_y
                    player.active_animations.pop(0)
            elif 'last_time' in anim and 'delay' in anim and current_time - anim['last_time'] >= anim['delay']:
                if 'is_jail_move' in anim:
                    if anim.get('sound_played', True):
                        anim['current_step'] += 1
                        if anim['current_step'] <= anim['steps']:
                            anim['player'].current_x, anim['player'].current_y = interpolate_position(
                                anim['start_pos'], anim['end_pos'], anim['steps'], anim['current_step']
                            )
                            anim['last_time'] = current_time
                        else:
                            if anim.get('jail_action') == 'enter':
                                game_state['game_jail_visit'] = True
                                anim['player'].position = 10  # Jail position
                                anim['player'].in_jail = True
                                anim['player'].jail_x = anim['player'].current_x
                                anim['player'].jail_y = anim['player'].current_y
                                
                                if anim.get('cleanup_jail_sound', False) and 'jail_sound_delay' in game_state:
                                    if 'jail_sound_played' in game_state:
                                        del game_state['jail_sound_played']
                                    if 'jail_sound_delay' in game_state:
                                        del game_state['jail_sound_delay']
                            elif anim.get('jail_action') == 'exit':
                                anim['player'].position = anim['player'].prev_position
                                anim['player'].in_jail = False
                                anim['player'].jail_from_x = None
                                anim['player'].jail_from_y = None
                                anim['player'].jail_marker_anim_start = None
                            player.active_animations.pop(0)
                            player.turn_ended = True
                else:
                    anim['index'] += 1
                    if anim['index'] < len(anim['path']):
                        prev_position = anim['player'].position
                        prev_square_type = squares[prev_position] if prev_position < len(squares) else None
                        
                        anim['player'].position = anim['path'][anim['index']]
                        anim['player'].current_x, anim['player'].current_y = squares_coords[anim['player'].position]
                        
                        if anim['player'].position == 0:
                            anim['player'].current_x = squares_coords[0][0]
                            anim['player'].current_y = squares_coords[0][1]
                        
                        if prev_square_type == 'B' and prev_position != anim['player'].position:
                            if 'last_bonus_position' in game_state and str(anim['player'].id) in game_state['last_bonus_position']:
                                if game_state['last_bonus_position'][str(anim['player'].id)] == prev_position:
                                    del game_state['last_bonus_position'][str(anim['player'].id)]
                        
                        if 'is_backwards' not in anim:
                            if anim['player'].position not in anim['player'].position_history:
                                anim['player'].position_history.append(anim['player'].position)
                        else:
                            while (len(anim['player'].position_history) > 0 and 
                                   anim['player'].position_history[-1] > anim['player'].position):
                                anim['player'].position_history.pop()
                        
                        anim['last_time'] = current_time
                        if 'is_initial_move' in anim and anim['is_initial_move']:
                            if anim['player'].is_computer:
                                audio.glug_cpu_sound.play()
                            else:
                                audio.glug_sound.play()
                        elif 'is_backwards' in anim:
                            if anim['player'].is_computer:
                                audio.wobble_cpu_sound.play()
                            else:
                                audio.wobble_sound.play()
                        else:
                            if anim['player'].is_computer:
                                audio.jump_cpu_sound.play()
                            else:
                                audio.jump_sound.play()
                        game_state['message'] = anim['message'] + f" Moved to {squares[anim['player'].position]}."
                    else:
                        if 'is_backwards' in anim:
                            player.active_animations.pop(0)
                            square_type = squares[anim['player'].position]
                            message, chain = apply_effect(anim['player'], square_type, game_state, scale, squares, squares_coords, JAIL_POS)
                            if message:
                                game_state['message'] = message
                            if not chain:
                                player.turn_ended = True
                            else:
                                player.turn_ended = False
                        else:
                            square_type = squares[anim['player'].position]
                            message, chain = apply_effect(anim['player'], square_type, game_state, scale, squares, squares_coords, JAIL_POS)
                            game_state['message'] = anim['message'] + f" Landed on {square_type}. {message}"
                            player.active_animations.pop(0)
                            if (not chain or game_state.get('show_quiz', False)) and square_type != 'B':
                                player.turn_ended = True
                            else:
                                any_animations = True
    return any_animations

def run_game_loop(layout_state, players, selected_board, saved_progress):
    """The central gameplay loop orchestrator.
    
    This function handles all frames, events, CPU decisions, and drawing tasks
    for a match. Returns a boolean indicating if the game should completely quit.
    Complies with Australian English spelling conventions.
    """
    scale = layout_state['scale']
    offset_x = layout_state['offset_x']
    offset_y = layout_state['offset_y']
    screen = layout_state['screen']
    font = layout_state['font']
    title_font = layout_state['title_font']
    
    squares, next_positions = get_board_squares(selected_board)
    
    if selected_board == 'Expert':
        squares_coords = get_expert_squares_coords()
        JAIL_POS = EXPERT_JAIL_POS
    elif selected_board == 'Secret':
        squares_coords = get_secret_squares_coords()
        JAIL_POS = SECRET_JAIL_POS
    else:
        squares_coords = get_classic_squares_coords()
        JAIL_POS = CLASSIC_JAIL_POS
        
    game_state = AssetRegistry.camera_asset_cache  # placeholder link if needed, but rather:
    
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
        'selected_board': selected_board,
        'game_jail_visit': False,
        'game_start_time': time.time(),
        'ui_buttons_fly_in_start': time.time(),
        'game_start_buffer': 1.0,
        'show_settings_menu': False,
        'last_bonus_position': {},
        'volume_drag_active': False,
        'show_achievements_menu': False,
        'camera_mode': 0,
        'camera_zoom': 1.0,
        'camera_focus_x': 400.0,
        'camera_focus_y': 300.0,
        'camera_target_zoom': 1.0,
        'camera_target_focus_x': 400.0,
        'camera_target_focus_y': 300.0,
    }
    
    if selected_board == 'Secret':
        game_state['die_pos'] = (700, 150)
        
    # Apply saved settings
    if 'settings' in saved_progress:
        game_state['master_volume'] = saved_progress['settings'].get('master_volume', 1.0)
        game_state['show_game_status'] = saved_progress['settings'].get('show_game_status', False)
        game_state['use_modern_status_display'] = saved_progress['settings'].get('use_modern_status_display', True)
        game_state['show_timers'] = saved_progress['settings'].get('show_timers', False)
        game_state['speak_quiz_questions'] = saved_progress['settings'].get('speak_quiz_questions', True)
        game_state['speak_quiz_answers'] = saved_progress['settings'].get('speak_quiz_answers', True)
        game_state['use_device_tts'] = saved_progress['settings'].get('use_device_tts', False)
    else:
        game_state['master_volume'] = 1.0
        game_state['show_game_status'] = False
        game_state['use_modern_status_display'] = True
        game_state['show_timers'] = False
        game_state['speak_quiz_questions'] = True
        game_state['speak_quiz_answers'] = True
        game_state['use_device_tts'] = False
        
    audio.apply_master_volume(game_state['master_volume'])
    quiz_tts.set_answer_source(game_state.get('use_device_tts', False))
    clock = pygame.time.Clock()
    
    # Resize assets initially
    resize_assets(scale, selected_board)
    
    running = True
    quit_game = False
    
    # Create lambda functions to avoid circular calls and preserve component parameters
    move_player_func = lambda p, gs: move_player(p, gs)
    apply_quiz_effect_func = lambda p, c, gs, sc: apply_quiz_effect(p, c, gs, sc)
    get_movement_path_with_choice_func = lambda p, c, rs, sq, np, soc: get_movement_path_with_choice(p, c, rs, sq, np, soc)
    resize_assets_func = lambda sc, bt: resize_assets(sc, bt)
    
    while running:
        events = pygame.event.get()
        keep_running, quit_all = input.handle_events(
            events, game_state, players, layout_state, squares, next_positions,
            move_player_func, apply_quiz_effect_func, get_movement_path_with_choice_func, resize_assets_func
        )
        
        # Keep layout reference variables synchronised from events
        scale = layout_state['scale']
        offset_x = layout_state['offset_x']
        offset_y = layout_state['offset_y']
        screen = layout_state['screen']
        font = layout_state['font']
        title_font = layout_state['title_font']
        SCREEN_WIDTH = layout_state['screen_width']
        SCREEN_HEIGHT = layout_state['screen_height']
        
        if not keep_running:
            running = False
            if quit_all:
                quit_game = True
                break
                
        # Update camera targets based on current state
        camera.update_camera_targets(game_state, players)
        
        animations_active = update_animation(game_state, scale, squares, squares_coords, JAIL_POS)
        
        if game_state.get('restart_hold_start') is not None:
            hold_time = time.time() - game_state['restart_hold_start']
            if hold_time >= 1.5:
                game_state['restart_ready'] = True
                
        if 'fade_start' in game_state:
            fade_time = time.time() - game_state['fade_start']
            if fade_time >= 1.0:
                running = False
                
        # Handle Bonus card scaling progression
        if 'bonus_image_state' in game_state:
            current_time = time.time()
            if game_state['bonus_image_state'] == 'waiting':
                if current_time - game_state['bonus_image_start'] >= 0.1:
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
                    player = players[game_state['current_player']]
                    effect = game_state['bonus_action']
                    
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
                        game_state['game_jail_visit'] = True
                        player.prev_position = player.position
                        spent_jail_free = spend_jail_free_card_if_held(player, game_state)
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
                        if spent_jail_free:
                            game_state['message'] = f"Player {player.id + 1} spent their Get Out of Jail Free card."
                    elif effect[0] == "jail_free":
                        player.has_jail_free_card = True
                        player.jail_free_card_visible = False
                        game_state['bonus_target_player_id'] = player.id
                        if audio.doubles_sound is not None:
                            audio.doubles_sound.play()
                        game_state['message'] = f"Player {player.id + 1} got a Get Out of Jail Free card!"
                    elif effect[0] == "pick_quiz":
                        game_state['pending_quiz'] = True
            elif game_state['bonus_image_state'] == 'showing':
                player = players[game_state['current_player']]
                if (game_state['bonus_action'][0] == "jail_free" and
                    'bonus_action_start_time' in game_state and
                    current_time - game_state['bonus_action_start_time'] >= 1.2):
                    game_state['bonus_image_state'] = 'gliding_to_player'
                    game_state['bonus_glide_start'] = current_time
                elif 'bonus_action_start_time' in game_state and current_time - game_state['bonus_action_start_time'] >= 2.0:
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
            elif game_state['bonus_image_state'] == 'gliding_to_player':
                elapsed = current_time - game_state['bonus_glide_start']
                if elapsed >= 1.0:
                    target_player_id = game_state.get('bonus_target_player_id', players[game_state['current_player']].id)
                    target_player = next((p for p in players if p.id == target_player_id), players[game_state['current_player']])
                    target_player.jail_free_card_visible = True
                    for key in [
                        'bonus_image_key', 'bonus_image_state', 'bonus_action',
                        'bonus_target_player_id', 'bonus_glide_start'
                    ]:
                        game_state.pop(key, None)
                    target_player.turn_ended = True
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
                    
                    if game_state.get('pending_quiz', False):
                        quiz_tts.stop_quiz_tts()
                        game_state.pop('quiz_tts_started', None)
                        if game_state.get('selected_board') == "Expert" and cards.expert_quiz_card_index < len(cards.expert_quiz_cards):
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
                            question, options, correct = cards.quiz_cards[cards.quiz_card_index]
                            game_state['quiz_question'] = (question, options, correct)
                            game_state['show_quiz'] = True
                            game_state['quiz_state'] = 'growing'
                            game_state['quiz_start_time'] = time.time()
                            game_state['pop_played'] = False
                            audio.drum_machine_sound.play()
                            cards.quiz_card_index = (cards.quiz_card_index + 1) % len(cards.quiz_cards)
                            game_state['message'] = f"Player {players[game_state['current_player']].id + 1} faces a quiz."
                        
                        del game_state['pending_quiz']
                    
                    current_player = players[game_state['current_player']]
                    if not current_player.active_animations:
                        current_player.turn_ended = True

        # Handle CPU turns dynamically
        if not animations_active and not game_state.get('show_quiz', False) and \
           not game_state.get('show_path_choice_after_roll', False) and not game_state.get('rolling_dice', False) and \
           'movement_delay_start' not in game_state and not game_state.get('processing_bonus_card', False):
            current_player = players[game_state['current_player']]
            
            if current_player.is_computer and not current_player.has_rolled and not current_player.finished:
                cpu.handle_cpu_turn(game_state, players, squares_coords, JAIL_POS, move_player_func)
            elif current_player.finished:
                current_player.has_rolled = False
                current_player.turn_ended = False
                
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
                if str(game_state['current_player']) in game_state['last_bonus_position']:
                    del game_state['last_bonus_position'][str(game_state['current_player'])]
            elif current_player.turn_ended and not current_player.active_animations:
                current_player.has_rolled = False
                current_player.turn_ended = False
                
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
                if str(game_state['current_player']) in game_state['last_bonus_position']:
                    del game_state['last_bonus_position'][str(game_state['current_player'])]
        
        if not game_state.get('bonus_image_state') and game_state.get('processing_bonus_card', False):
            game_state['processing_bonus_card'] = False
            
        # CPU Quiz answering automation
        if game_state.get('show_quiz', False) and 'quiz_buttons' in game_state:
            current_player = players[game_state['current_player']]
            if current_player.is_computer:
                cpu.handle_cpu_quiz(game_state, current_player, scale, apply_quiz_effect_func)
            elif 'pending_quiz_answer' in game_state:
                # Process human keyboard quiz answer after delay for visualization
                if time.time() - game_state['quiz_answer_delay_start'] >= 0.8:
                    option_index = game_state['pending_quiz_answer']
                    _, _, correct = game_state['quiz_question']
                    if option_index == correct:
                        apply_quiz_effect_func(current_player, True, game_state, scale)
                    else:
                        apply_quiz_effect_func(current_player, False, game_state, scale)
                    del game_state['pending_quiz_answer']
                
        # CPU Bonus card interaction automation
        if 'bonus_image_state' in game_state and game_state['bonus_image_state'] == 'showing':
            current_player = players[game_state['current_player']]
            if current_player.is_computer:
                cpu.handle_cpu_bonus(game_state, current_player)
                
        # CPU Path selection automation
        if game_state.get('show_path_choice_after_roll', False) and 'path_buttons' in game_state:
            current_player = players[game_state['current_player']]
            if current_player.is_computer:
                cpu.handle_cpu_path(game_state, current_player, squares, next_positions, get_movement_path_with_choice_func)
                
        update_ui_buttons_fly_in(game_state)

        # Perform layout drawing operations
        draw_board(screen, players, game_state, scale, offset_x, offset_y, font, title_font)
        
        if game_state.get('show_achievements_menu', False):
            render_achievements_pane(screen, scale, offset_x, offset_y, game_state['selected_board'])
            
        if game_state.get('show_timers', False):
            timer_x = SCREEN_WIDTH - 200 * scale
            timer_y_start = 30 * scale
            timer_spacing = 40 * scale
            display_player_timers(game_state, screen, font, timer_x, timer_y_start, timer_spacing, players, player_colours)
            
        if game_state.get('jail_sound_delay') and not game_state.get('jail_sound_played', False):
            if time.time() > game_state['jail_sound_delay']:
                audio.mac_os_uh_ohh_sound.play()
                game_state['jail_sound_played'] = True

        if game_state.get('show_quiz', False) and game_state.get('quiz_state') == 'buttons':
            if game_state.get('speak_quiz_answers', True):
                quiz_tts.tick_answers()
                
        pygame.display.flip()
        clock.tick(60)
        
    return quit_game
