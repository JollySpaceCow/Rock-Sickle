import pygame
import sys
import os
from src.core import audio
from src.core.assets import AssetRegistry, load_asset
from src.core.progress import load_game_progress
from src.ui.gallery import render_achievements_pane
from src.constants import (
    ORIGINAL_WIDTH, ORIGINAL_HEIGHT,
    GRAY, GREEN, BLACK, DARK_GREY, WHITE,
    player_colours
)

def toggle_player_state(index, player_states, difficulties):
    """Toggle a player's state between not set, human, or CPU."""
    player_states[index] = (player_states[index] + 1) % 3
    if player_states[index] == 0:
        audio.pong_sound.play()
        difficulties[index] = None
    elif player_states[index] == 1:
        audio.whit_sound.play()
        difficulties[index] = None
    elif player_states[index] == 2:
        difficulties[index] = 'normal'
        audio.voltage_normal_sound.play()

def cycle_difficulty(index, difficulties):
    """Cycle through CPU difficulty levels."""
    if difficulties[index] == 'easy':
        difficulties[index] = 'normal'
        audio.voltage_normal_sound.play()
    elif difficulties[index] == 'normal':
        difficulties[index] = 'hard'
        audio.voltage_hard_sound.play()
    elif difficulties[index] == 'hard':
        difficulties[index] = 'easy'
        audio.voltage_easy_sound.play()

def select_players(layout_state):
    """Let players configure player types and select the board.
    
    This function manages the configuration loop and initialises layouts.
    Uses the provided layout_state dictionary to update layout settings dynamically.
    """
    # Load game progress to check if Expert board is unlocked
    game_progress = load_game_progress()
    
    player_states = [0, 0, 0, 0, 0, 0]
    difficulties = [None, None, None, None, None, None]
    selected_board = 0  # Default to the first board (Classic)
    
    # Check if player has completed at least one game
    has_completed_game = game_progress.get("completed_games", 0) >= 1
    
    # Only include boards that have been unlocked
    board_names = ["Classic"]
    if "Expert" in game_progress.get("unlocked_boards", ["Classic"]):
        board_names.append("Expert")
    if "Secret" in game_progress.get("unlocked_boards", ["Classic"]):
        board_names.append("Secret")
        
    # Flag to determine if we should show board selection
    show_board_selection = has_completed_game
    
    # Create fonts using the layout state scale
    scale = layout_state['scale']
    offset_x = layout_state['offset_x']
    offset_y = layout_state['offset_y']
    screen = layout_state['screen']
    font = layout_state['font']
    title_font = layout_state['title_font']
    
    not_set_image = pygame.image.load(load_asset("Assets/Images/Players/Player Not.png"))
    player_images_scaled = [pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale))) for img in AssetRegistry.player_images_original]
    
    # Scale CPU difficulty images
    cpu_difficulty_images_scaled = {
        key: pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale)))
        for key, img in AssetRegistry.cpu_difficulty_images_original.items()
    }
    
    not_set_image_scaled = pygame.transform.smoothscale(not_set_image, (int(80 * scale), int(80 * scale)))
    
    slot_rects = [pygame.Rect(int(100 * scale + offset_x + i * 100 * scale), int(150 * scale + offset_y), int(80 * scale), int(80 * scale)) for i in range(6)]
    
    # Add board selector buttons
    board_button_width = int(120 * scale)
    board_button_height = int(40 * scale)
    board_selector_rects = []
    for i in range(len(board_names)):
        x_pos = int((ORIGINAL_WIDTH * scale / 2) - (board_button_width * len(board_names) / 2) + (i * board_button_width) + offset_x)
        board_selector_rects.append(pygame.Rect(x_pos, int(350 * scale + offset_y), board_button_width, board_button_height))
    
    start_button_rect = pygame.Rect(int(300 * scale + offset_x), int(400 * scale + offset_y), int(200 * scale), int(50 * scale))
    gallery_button_size = int(55 * scale)
    gallery_button_rect = pygame.Rect(
        int(670 * scale + offset_x), int(540 * scale + offset_y), gallery_button_size, gallery_button_size
    )
    gallery_target_scaled = pygame.transform.smoothscale(
        AssetRegistry.board_buttons['Classic']['achievement'], (gallery_button_size, gallery_button_size)
    )
    
    show_achievements = False
    achievement_pane_rect = None

    while True:
        # Update references from layout_state in case of resizes
        scale = layout_state['scale']
        offset_x = layout_state['offset_x']
        offset_y = layout_state['offset_y']
        screen = layout_state['screen']
        font = layout_state['font']
        title_font = layout_state['title_font']
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                # Preserve existing display flags (e.g., fullscreen) during resize
                layout_state['screen_width'], layout_state['screen_height'] = event.size
                scale_x = layout_state['screen_width'] / ORIGINAL_WIDTH
                scale_y = layout_state['screen_height'] / ORIGINAL_HEIGHT
                layout_state['scale'] = min(scale_x, scale_y)
                layout_state['offset_x'] = (layout_state['screen_width'] - (ORIGINAL_WIDTH * layout_state['scale'])) / 2
                layout_state['offset_y'] = (layout_state['screen_height'] - (ORIGINAL_HEIGHT * layout_state['scale'])) / 2
                current_flags = pygame.display.get_surface().get_flags()
                new_flags = current_flags | pygame.RESIZABLE
                layout_state['screen'] = pygame.display.set_mode((layout_state['screen_width'], layout_state['screen_height']), new_flags)
                layout_state['font'] = pygame.font.SysFont(None, int(24 * layout_state['scale']))
                layout_state['title_font'] = pygame.font.SysFont(None, int(72 * layout_state['scale']))
                
                # Re-read the layout state variables after resize recalculations
                scale = layout_state['scale']
                offset_x = layout_state['offset_x']
                offset_y = layout_state['offset_y']
                screen = layout_state['screen']
                font = layout_state['font']
                title_font = layout_state['title_font']
                
                player_images_scaled = [pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale))) for img in AssetRegistry.player_images_original]
                cpu_difficulty_images_scaled = {
                    key: pygame.transform.smoothscale(img, (int(80 * scale), int(80 * scale)))
                    for key, img in AssetRegistry.cpu_difficulty_images_original.items()
                }
                not_set_image_scaled = pygame.transform.smoothscale(not_set_image, (int(80 * scale), int(80 * scale)))
                
                slot_rects = [pygame.Rect(int(100 * scale + offset_x + i * 100 * scale), int(150 * scale + offset_y), int(80 * scale), int(80 * scale)) for i in range(6)]
                
                # Recalculate board selector buttons
                board_button_width = int(120 * scale)
                board_button_height = int(40 * scale)
                board_selector_rects = []
                for i in range(len(board_names)):
                    x_pos = int((ORIGINAL_WIDTH * scale / 2) - (board_button_width * len(board_names) / 2) + (i * board_button_width) + offset_x)
                    board_selector_rects.append(pygame.Rect(x_pos, int(350 * scale + offset_y), board_button_width, board_button_height))
                    
                start_button_rect = pygame.Rect(int(300 * scale + offset_x), int(400 * scale + offset_y), int(200 * scale), int(50 * scale))
                gallery_button_size = int(55 * scale)
                gallery_button_rect = pygame.Rect(
                    int(670 * scale + offset_x), int(540 * scale + offset_y), gallery_button_size, gallery_button_size
                )
                gallery_target_scaled = pygame.transform.smoothscale(
                    AssetRegistry.board_buttons['Classic']['achievement'], (gallery_button_size, gallery_button_size)
                )
            
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
                            
                if has_completed_game and gallery_button_rect.collidepoint(pos):
                    show_achievements = not show_achievements
                    audio.connect_sound.play()
                
                # Close achievements if clicking outside
                if show_achievements and achievement_pane_rect and not achievement_pane_rect.collidepoint(pos) and (
                    not has_completed_game or not gallery_button_rect.collidepoint(pos)
                ):
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
                # Fullscreen toggle is managed in input module.
                # Escape key handling
                if event.key == pygame.K_ESCAPE:
                    if show_achievements:
                        show_achievements = False
                elif pygame.K_1 <= event.key <= pygame.K_6:
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
                    # Fallback to normal if difficulty is not recognised
                    screen.blit(cpu_difficulty_images_scaled['normal'], rect.topleft)
            
            label = font.render(f"P{i+1}", True, player_colours[i])
            screen.blit(label, (rect.centerx - label.get_width() // 2, rect.top - int(20 * scale)))
            
        # Only draw board selector if player has completed at least one game
        if show_board_selection and len(board_names) > 1:
            board_selector_text = font.render("Select Board:", True, BLACK)
            screen.blit(board_selector_text, (int(ORIGINAL_WIDTH * scale / 2 - board_selector_text.get_width() / 2 + offset_x), int(320 * scale + offset_y)))
            
            for i, rect in enumerate(board_selector_rects):
                # Use a different colour for the selected board
                button_colour = GREEN if i == selected_board else DARK_GREY
                pygame.draw.rect(screen, button_colour, rect)
                # Use black text for selected button, white for unselected buttons
                text_colour = BLACK if i == selected_board else WHITE
                text = font.render(board_names[i], True, text_colour)
                screen.blit(text, text.get_rect(center=rect.center))
                
        # Gallery button (target tile, same as in-game) — only after completing a game
        if has_completed_game:
            screen.blit(gallery_target_scaled, gallery_button_rect.topleft)

        # Create a desaturated button with 50% opacity when inactive
        if any(state > 0 for state in player_states):
            pygame.draw.rect(screen, GREEN, start_button_rect)
        else:
            # Create a transparent surface for the inactive button
            button_surface = pygame.Surface((start_button_rect.width, start_button_rect.height), pygame.SRCALPHA)
            r, g, b = GREEN
            gray_value = (r + g + b) // 3
            button_surface.fill((gray_value, gray_value, gray_value, 128))
            screen.blit(button_surface, start_button_rect)
            
        if any(state > 0 for state in player_states):
            text = font.render("Start Game", True, BLACK)
            screen.blit(text, text.get_rect(center=start_button_rect.center))
        else:
            text = font.render("Start Game", True, BLACK)
            text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
            text_surface.blit(text, (0, 0))
            text_surface.set_alpha(128)
            screen.blit(text_surface, text.get_rect(center=start_button_rect.center))

        # Draw Achievements Pane if active
        if show_achievements:
            achievement_pane_rect = render_achievements_pane(screen, scale, offset_x, offset_y, board_names[selected_board])

        pygame.display.flip()
