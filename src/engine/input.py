import pygame
import time
from src.core import audio, quiz_tts
from src.ui.button_anim import get_ui_button_rects
from src.core.progress import load_game_progress, save_game_progress
from src.constants import ORIGINAL_WIDTH, ORIGINAL_HEIGHT, DIE_POS, JAIL_SIZE

def handle_events(events, game_state, players, layout_state, squares, next_positions, move_player_func, apply_quiz_effect_func, get_movement_path_with_choice_func, resize_assets_func):
    """Handle all Pygame events during gameplay, updating the game and layout states.
    
    This modularises the keyboard, mouse clicks, and screen resizing actions.
    All comment descriptions and variables comply with Australian English.
    """
    keep_running = True
    quit_game = False
    
    scale = layout_state['scale']
    offset_x = layout_state['offset_x']
    offset_y = layout_state['offset_y']
    screen = layout_state['screen']
    font = layout_state['font']
    title_font = layout_state['title_font']
    SCREEN_WIDTH = layout_state['screen_width']
    SCREEN_HEIGHT = layout_state['screen_height']
    
    # Check if there are any active animations on players
    animations_active = any(player.active_animations for player in players)
    
    for event in events:
        if event.type == pygame.QUIT:
            # Save current settings before closing the game window
            saved_progress = load_game_progress()
            if 'settings' not in saved_progress:
                saved_progress['settings'] = {}
            
            saved_progress['settings']['master_volume'] = game_state.get('master_volume', 1.0)
            saved_progress['settings']['show_game_status'] = game_state.get('show_game_status', False)
            saved_progress['settings']['use_modern_status_display'] = game_state.get('use_modern_status_display', True)
            saved_progress['settings']['show_timers'] = game_state.get('show_timers', False)
            saved_progress['settings']['speak_quiz_questions'] = game_state.get('speak_quiz_questions', True)
            saved_progress['settings']['speak_quiz_answers'] = game_state.get('speak_quiz_answers', True)
            saved_progress['settings']['use_device_tts'] = game_state.get('use_device_tts', False)
            
            save_game_progress(saved_progress)
            keep_running = False
            quit_game = True
            
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.size
            scale_x = SCREEN_WIDTH / ORIGINAL_WIDTH
            scale_y = SCREEN_HEIGHT / ORIGINAL_HEIGHT
            scale = min(scale_x, scale_y)
            offset_x = (SCREEN_WIDTH - (ORIGINAL_WIDTH * scale)) / 2
            offset_y = (SCREEN_HEIGHT - (ORIGINAL_HEIGHT * scale)) / 2
            # Ensure window remains resizable during resize (ignore other flags to avoid overflow)
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            font = pygame.font.SysFont(None, int(24 * scale))
            title_font = pygame.font.SysFont(None, int(72 * scale))
            
            # Update layout_state for references
            layout_state['scale'] = scale
            layout_state['offset_x'] = offset_x
            layout_state['offset_y'] = offset_y
            layout_state['screen'] = screen
            layout_state['font'] = font
            layout_state['title_font'] = title_font
            layout_state['screen_width'] = SCREEN_WIDTH
            layout_state['screen_height'] = SCREEN_HEIGHT
            
            # Trigger asset resizing behaviour
            resize_assets_func(scale, game_state['selected_board'])
            game_state['last_scale'] = scale
            
        elif event.type == pygame.KEYDOWN:
            # Fullscreen toggle (F11, or Cmd+Ctrl+F) with debounce to avoid rapid toggling crashes
            if event.key == pygame.K_F11:
                now = time.time()
                # Prevent toggling more often than half a second
                if now - layout_state.get('last_fullscreen_toggle', 0) < 1.0:
                    # Skip this toggle to avoid race conditions
                    pass
                else:
                    layout_state['last_fullscreen_toggle'] = now
                    # Determine current fullscreen state via pygame flags to avoid double toggling (macOS Cmd+Ctrl+F may trigger OS fullscreen first)
                    screen = layout_state['screen']
                    is_current_fullscreen = bool(screen.get_flags() & pygame.FULLSCREEN)
                    # Flip fullscreen state based on actual flag
                    fullscreen = not is_current_fullscreen
                    layout_state['fullscreen'] = fullscreen
                    if fullscreen:
                        # Store current windowed dimensions before entering fullscreen
                        layout_state['windowed_width'] = layout_state['screen_width']
                        layout_state['windowed_height'] = layout_state['screen_height']
                        # Enter fullscreen using native desktop resolution (0,0 lets SDL pick the best size)
                        # If already in desired state, just update layout_state and skip set_mode
                        if is_current_fullscreen:
                            # Already fullscreen, no need to call set_mode again
                            layout_state['fullscreen'] = True
                        else:
                            # Enter fullscreen using native desktop resolution (0,0 lets SDL pick the best size)
                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        # Restore to previous windowed size
                        prev_w = layout_state.get('windowed_width', ORIGINAL_WIDTH)
                        prev_h = layout_state.get('windowed_height', ORIGINAL_HEIGHT)
                        # If already windowed, no need to call set_mode again
                        if not is_current_fullscreen:
                            # Already windowed, just update state
                            layout_state['fullscreen'] = False
                        else:
                            # Restore to previous windowed size
                            screen = pygame.display.set_mode((prev_w, prev_h), pygame.RESIZABLE)
                    # Update layout_state with new screen and dimensions
                    layout_state['screen'] = screen
                    layout_state['screen_width'] = screen.get_width()
                    layout_state['screen_height'] = screen.get_height()
                    # Recalculate scaling based on new dimensions
                    scale_x = layout_state['screen_width'] / ORIGINAL_WIDTH
                    scale_y = layout_state['screen_height'] / ORIGINAL_HEIGHT
                    layout_state['scale'] = min(scale_x, scale_y)
                    layout_state['offset_x'] = (layout_state['screen_width'] - (ORIGINAL_WIDTH * layout_state['scale'])) / 2
                    layout_state['offset_y'] = (layout_state['screen_height'] - (ORIGINAL_HEIGHT * layout_state['scale'])) / 2
                    # Update fonts for new scale
                    layout_state['font'] = pygame.font.SysFont(None, int(24 * layout_state['scale']))
                    layout_state['title_font'] = pygame.font.SysFont(None, int(72 * layout_state['scale']))
                    # Resize assets after toggle
                    resize_assets_func(layout_state['scale'], game_state['selected_board'])
                    game_state['last_scale'] = layout_state['scale']
                    scale = layout_state['scale']
            # Space handling
            elif event.key == pygame.K_SPACE:
                current_player = players[game_state['current_player']]
                if time.time() - game_state.get('game_start_time', 0) < game_state.get('game_start_buffer', 0):
                    pass
                elif not current_player.is_computer and not game_state.get('show_quiz', False) and \
                        not game_state.get('show_path_choice_after_roll', False) and \
                        not game_state.get('rolling_dice', False) and not current_player.has_rolled and \
                        not game_state.get('bonus_image_state') and not animations_active:
                    message, moved = move_player_func(current_player, game_state)
                    game_state['message'] = message
            # Quiz handling
            elif game_state.get('show_quiz', False) and game_state.get('quiz_state') == 'buttons' and 'quiz_buttons' in game_state:
                current_player = players[game_state['current_player']]
                if not current_player.is_computer:
                    if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                        option_index = event.key - pygame.K_1
                        if option_index < len(game_state['quiz_buttons']):
                            game_state['clicked_quiz_button'] = option_index
                            game_state['button_click_time'] = time.time()
                            quiz_tts.stop_quiz_tts()
                            _, _, correct = game_state['quiz_question']
                            if option_index == correct:
                                apply_quiz_effect_func(current_player, True, game_state, scale)
                            else:
                                apply_quiz_effect_func(current_player, False, game_state, scale)
            # Escape handling
            elif event.key == pygame.K_ESCAPE:
                if game_state.get('show_achievements_menu', False):
                    game_state['show_achievements_menu'] = False
                elif game_state.get('show_settings_menu', False):
                    game_state['show_settings_menu'] = False
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            screen = layout_state['screen']
            restart_button_rect, achievement_button_rect, settings_button_rect, magnify_button_rect = get_ui_button_rects(
                game_state, scale, offset_x, offset_y, screen.get_height()
            )
            if restart_button_rect.collidepoint(pos):
                game_state['restart_hold_start'] = time.time()
                
            if achievement_button_rect.collidepoint(pos):
                game_state['show_achievements_menu'] = not game_state.get('show_achievements_menu', False)
                audio.connect_sound.play()
                if game_state['show_achievements_menu']:
                    game_state['show_settings_menu'] = False
                    
            if settings_button_rect.collidepoint(pos):
                game_state['show_settings_menu'] = not game_state.get('show_settings_menu', False)
                
            if magnify_button_rect.collidepoint(pos):
                game_state['camera_mode'] = (game_state.get('camera_mode', 0) + 1) % 3
                audio.connect_sound.play()
                game_state['show_settings_menu'] = False
                game_state['show_achievements_menu'] = False
                
            if game_state.get('show_settings_menu', False):
                menu_width = int(200 * scale)
                menu_height = int(370 * scale)
                menu_x = settings_button_rect.x + (settings_button_rect.width // 2) - (menu_width // 2)
                menu_y = settings_button_rect.y - menu_height - int(10 * scale)
                menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
                
                if 'status_toggle_rect' in game_state and game_state['status_toggle_rect'].collidepoint(pos):
                    game_state['show_game_status'] = not game_state.get('show_game_status', True)
                if 'style_toggle_rect' in game_state and game_state['style_toggle_rect'].collidepoint(pos):
                    game_state['use_modern_status_display'] = not game_state.get('use_modern_status_display', False)
                if 'timer_toggle_rect' in game_state and game_state['timer_toggle_rect'].collidepoint(pos):
                    game_state['show_timers'] = not game_state.get('show_timers', False)
                    audio.connect_sound.play()
                if 'questions_toggle_rect' in game_state and game_state['questions_toggle_rect'].collidepoint(pos):
                    game_state['speak_quiz_questions'] = not game_state.get('speak_quiz_questions', True)
                    if not game_state['speak_quiz_questions']:
                        quiz_tts.stop_question_tts()
                    audio.connect_sound.play()
                if 'answers_toggle_rect' in game_state and game_state['answers_toggle_rect'].collidepoint(pos):
                    game_state['speak_quiz_answers'] = not game_state.get('speak_quiz_answers', True)
                    if not game_state['speak_quiz_answers']:
                        quiz_tts.stop_answer_tts()
                    audio.connect_sound.play()
                if 'tts_source_toggle_rect' in game_state and game_state['tts_source_toggle_rect'].collidepoint(pos):
                    game_state['use_device_tts'] = not game_state.get('use_device_tts', False)
                    quiz_tts.set_answer_source(game_state['use_device_tts'])
                    quiz_tts.stop_answer_tts()
                    audio.connect_sound.play()
                if 'volume_slider_rect' in game_state and game_state['volume_slider_rect'].collidepoint(pos):
                    game_state['volume_drag_active'] = True
                    slider_rect = game_state['volume_slider_rect']
                    slider_width = game_state['volume_slider_width']
                    relative_x = max(0, min(pos[0] - slider_rect.x, slider_width))
                    volume = relative_x / slider_width
                    game_state['master_volume'] = volume
                    audio.apply_master_volume(volume)
                if 'reset_button_rect' in game_state and game_state['reset_button_rect'].collidepoint(pos):
                    game_state['master_volume'] = 1.0
                    game_state['show_game_status'] = False
                    game_state['use_modern_status_display'] = True
                    game_state['show_timers'] = False
                    game_state['speak_quiz_questions'] = True
                    game_state['speak_quiz_answers'] = True
                    game_state['use_device_tts'] = False
                    quiz_tts.set_answer_source(False)
                    audio.apply_master_volume(game_state['master_volume'])
                    audio.restart_sound.play()
                if not menu_rect.collidepoint(pos) and not settings_button_rect.collidepoint(pos):
                    game_state['show_settings_menu'] = False
                    game_state['volume_drag_active'] = False
                    
            if game_state.get('show_achievements_menu', False):
                pane_width = int(600 * scale)
                pane_height = int(520 * scale)
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
                if time.time() - game_state.get('game_start_time', 0) >= game_state.get('game_start_buffer', 0):
                    message, moved = move_player_func(current_player, game_state)
                    game_state['message'] = message
                    
            if game_state.get('show_quiz', False) and 'quiz_buttons' in game_state:
                for button, option_index in game_state['quiz_buttons']:
                    if button.collidepoint(pos):
                        game_state['clicked_quiz_button'] = option_index
                        game_state['button_click_time'] = time.time()
                        quiz_tts.stop_quiz_tts()
                        _, _, correct = game_state['quiz_question']
                        if option_index == correct:
                            apply_quiz_effect_func(current_player, True, game_state, scale)
                        else:
                            apply_quiz_effect_func(current_player, False, game_state, scale)
                            
            if game_state.get('show_path_choice_after_roll', False) and 'path_buttons' in game_state:
                for button, choice in game_state['path_buttons']:
                    if button.collidepoint(pos):
                        game_state['clicked_path_button'] = game_state['path_buttons'].index((button, choice))
                        game_state['path_button_click_time'] = time.time()
                        current_player.path_choices[current_player.position] = choice
                        remaining_spaces = game_state.get('spaces_remaining', 0)
                        started_on_choice = isinstance(next_positions[current_player.position], list)
                        movement_path = get_movement_path_with_choice_func(current_player.position, choice, remaining_spaces, squares, next_positions, started_on_choice)
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
            game_state['volume_drag_active'] = False
            
        elif event.type == pygame.MOUSEMOTION:
            if game_state.get('volume_drag_active', False) and 'volume_slider_rect' in game_state:
                pos = event.pos
                slider_rect = game_state['volume_slider_rect']
                slider_width = game_state['volume_slider_width']
                relative_x = max(0, min(pos[0] - slider_rect.x, slider_width))
                volume = relative_x / slider_width
                game_state['master_volume'] = volume
                audio.apply_master_volume(volume)
                
    return keep_running, quit_game
