import time
import random
from src.core import audio

def handle_cpu_turn(game_state, players, squares_coords, JAIL_POS, move_player_func):
    """Handle the automated movement and actions of a CPU player on their turn.
    
    Checks for jail cards or attempts to roll the die to escape or move.
    """
    current_player = players[game_state['current_player']]
    if current_player.is_computer and not current_player.has_rolled and not current_player.finished:
        if current_player.in_jail:
            if current_player.has_jail_free_card:
                current_player.in_jail = False
                current_player.has_jail_free_card = False
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
                    'message': f"CPU Player {current_player.id + 1} used Get Out of Jail Free card!",
                    'is_jail_move': True,
                    'delay': 0.0167,
                    'jail_action': 'exit'
                }
                audio.head_shake_cpu_sound.play()
                current_player.active_animations.append(anim)
                game_state['message'] = f"CPU Player {current_player.id + 1} used Get Out of Jail Free card!"
                current_player.turn_ended = True
            else:
                message, moved = move_player_func(current_player, game_state)
                game_state['message'] = message
                if not current_player.in_jail:
                    current_player.jail_from_x = None
                    current_player.jail_from_y = None
                    current_player.jail_marker_anim_start = None
        else:
            message, moved = move_player_func(current_player, game_state)
            game_state['message'] = message

def handle_cpu_quiz(game_state, current_player, scale, apply_quiz_effect_func):
    """Handle CPU players automatically answering quiz cards based on difficulty.
    
    Provides natural pauses and visual splash effects before applying responses.
    """
    if game_state.get('show_quiz', False) and 'quiz_buttons' in game_state:
        if current_player.is_computer:
            if 'cpu_quiz_delay' not in game_state:
                game_state['cpu_quiz_delay'] = time.time() + 3.0
            elif time.time() > game_state['cpu_quiz_delay']:
                _, _, correct = game_state['quiz_question']
                is_correct = False
                
                if current_player.difficulty == 'easy':
                    is_correct = random.random() < 0.3
                elif current_player.difficulty == 'normal':
                    is_correct = random.random() < 0.5
                elif current_player.difficulty == 'hard':
                    is_correct = random.random() < 0.7
                else:
                    is_correct = random.random() < 0.5
                
                selected_option = correct if is_correct else random.choice([i for i in range(len(game_state['quiz_buttons'])) if i != correct])
                
                game_state['clicked_quiz_button'] = selected_option
                game_state['button_click_time'] = time.time()
                
                game_state['cpu_splash_delay'] = time.time() + 1.0
                game_state['cpu_splash_option'] = selected_option
                game_state['cpu_splash_is_correct'] = is_correct
                
                del game_state['cpu_quiz_delay']
            
            if 'cpu_splash_delay' in game_state and time.time() > game_state['cpu_splash_delay']:
                is_correct = game_state['cpu_splash_is_correct']
                
                if is_correct:
                    game_state['message'] = f"Player {current_player.id + 1} answered correctly!"
                    audio.mac_os_dinbg_sound.play()
                    game_state['quiz_state'] = 'answered'
                    game_state['quiz_answer_delay_start'] = time.time()
                    if 'quiz_buttons' in game_state:
                        del game_state['quiz_buttons']
                    
                    current_player.turn_ended = True
                    current_player.has_rolled = True
                    
                    if game_state.get('processing_bonus_card', False):
                        game_state['quiz_from_bonus_completed'] = True
                else:
                    apply_quiz_effect_func(current_player, False, game_state, scale)
                
                del game_state['cpu_splash_delay']
                del game_state['cpu_splash_option']
                del game_state['cpu_splash_is_correct']

def handle_cpu_bonus(game_state, current_player):
    """Handle CPU players automatically processing bonus cards.
    
    Delaies action slightly before dismissing card displays.
    """
    if 'bonus_image_state' in game_state and game_state['bonus_image_state'] == 'showing':
        if current_player.is_computer:
            if 'bonus_action_start_time' in game_state and time.time() - game_state['bonus_action_start_time'] >= 2.0:
                if game_state['bonus_action'][0] != "pick_quiz" or not game_state.get('show_quiz', False):
                    game_state['bonus_image_state'] = 'flipping_back'
                    game_state['bonus_flip_back_start'] = time.time()
                    game_state['bonus_flipped'] = False
                    
                    if 'cpu_bonus_delay' in game_state:
                        del game_state['cpu_bonus_delay']
                    
                    current_player.has_rolled = True
            elif 'cpu_bonus_delay' not in game_state:
                game_state['cpu_bonus_delay'] = time.time() + 1.5
            elif time.time() > game_state['cpu_bonus_delay']:
                if game_state['bonus_action'][0] == "pick_quiz" and game_state.get('show_quiz', False):
                    pass
                else:
                    game_state['bonus_image_state'] = 'shrinking'
                    game_state['bonus_shrink_start'] = time.time()
                    del game_state['cpu_bonus_delay']
                    current_player.has_rolled = True

def handle_cpu_path(game_state, current_player, squares, next_positions, get_movement_path_with_choice_func):
    """Handle CPU players automatically picking paths at board forks.
    
    Provides visual feedback and starts the animation on path selections.
    """
    if game_state.get('show_path_choice_after_roll', False) and 'path_buttons' in game_state:
        if current_player.is_computer:
            if 'cpu_path_delay' not in game_state:
                game_state['cpu_path_delay'] = time.time() + 2.5
            elif time.time() > game_state['cpu_path_delay']:
                choice_idx = random.randrange(len(game_state['path_buttons']))
                _, choice = game_state['path_buttons'][choice_idx]
                
                game_state['clicked_path_button'] = choice_idx
                game_state['path_button_click_time'] = time.time()
                
                if 'cpu_path_splash_delay' not in game_state:
                    game_state['cpu_path_splash_delay'] = time.time() + 0.8
                elif time.time() > game_state['cpu_path_splash_delay']:
                    current_player.path_choices[current_player.position] = choice
                    remaining_spaces = game_state.get('spaces_remaining', 0)
                    
                    started_on_choice = isinstance(next_positions[current_player.position], list)
                    movement_path = get_movement_path_with_choice_func(current_player.position, choice, remaining_spaces, squares, next_positions, started_on_choice)
                    
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
                    
                    game_state['show_path_choice_after_roll'] = False
                    del game_state['path_buttons']
                    if 'roll_for_path_choice' in game_state:
                        del game_state['roll_for_path_choice']
                    if 'spaces_remaining' in game_state:
                        del game_state['spaces_remaining']
                    
                    del game_state['cpu_path_delay']
                    del game_state['cpu_path_splash_delay']
                    
                    current_player.has_rolled = True
