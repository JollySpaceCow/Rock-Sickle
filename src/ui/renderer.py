"""Board rendering and UI display components.

Manages all board layouts, tiled spaces, player tokens, dice animations,
card decks, card-flipping transitions, settings overlays, and timers.
All visual layout computations follow Australian English spelling conventions.
"""

import pygame
import time
import math
import random
import logging
from src.core import audio, quiz_tts
from src.core.assets import AssetRegistry, load_asset
from src.ui import camera
from src.ui.button_anim import get_ui_button_rects
from src.constants import (
    GAP_BETWEEN_TILES, ORIGINAL_WIDTH, ORIGINAL_HEIGHT,
    WHITE, BLACK, GREEN, YELLOW, BLUE, DULL_PINK, DARK_GREEN, GRAY, PINK,
    player_colours, DIE_POS, JAIL_SIZE, CLASSIC_JAIL_POS, EXPERT_JAIL_POS, SECRET_JAIL_POS
)
from src.game.board import (
    get_board_squares, get_classic_squares_coords, get_expert_squares_coords, get_secret_squares_coords
)
from src.game.mechanics import get_movement_path, get_movement_path_with_choice

logger = logging.getLogger()


def _get_friendly_square_name(square_type):
    """Convert internal square code to friendly display name."""
    name_mapping = {
        '1': 'Plus One',
        '0': 'Safe Space',
        '-2': 'Minus Two',
        'J': 'Go To Jail',
        'Q': 'Quiz Card',
        'B': 'Bonus Card',
        'F': 'Finish',
        'P': 'Path Choice',
        'FP': 'Safe Space',
        'Go': 'Go',
    }
    return name_mapping.get(square_type, square_type)


def _random_visible_dice_pos(screen, dice_face):
    margin = 10
    available_x = screen.get_width() - dice_face.get_width()
    available_y = screen.get_height() - dice_face.get_height()
    if available_x <= 0 or available_y <= 0:
        return max(0, available_x // 2), max(0, available_y // 2)

    min_x = margin if available_x >= margin * 2 else 0
    min_y = margin if available_y >= margin * 2 else 0
    max_x = available_x - margin if available_x >= margin * 2 else available_x
    max_y = available_y - margin if available_y >= margin * 2 else available_y
    return random.randint(min_x, max_x), random.randint(min_y, max_y)


def _draw_secret_pathway_rails(screen, squares_coords, scale, game_state, camera_zoom):
    """Draw paired black rails along the Secret board spiral path (one rail per side)."""
    if len(squares_coords) < 2:
        return

    screen_w = screen.get_width()
    screen_h = screen.get_height()
    half_tile = max(3, int(6.5 * scale * camera_zoom))
    path_gap = max(1, int(1.5 * scale * camera_zoom))
    rail_offset = half_tile + path_gap
    line_width = max(1, int(2 * scale * camera_zoom))

    for i in range(len(squares_coords) - 1):
        x1, y1 = camera.transform_coords(
            squares_coords[i][0], squares_coords[i][1],
            scale, game_state, screen_w, screen_h,
        )
        x2, y2 = camera.transform_coords(
            squares_coords[i + 1][0], squares_coords[i + 1][1],
            scale, game_state, screen_w, screen_h,
        )

        dx = x2 - x1
        dy = y2 - y1
        length = max(1, math.sqrt(dx * dx + dy * dy))
        dx /= length
        dy /= length
        perp_dx = -dy
        perp_dy = dx

        left_start = (int(x1 + perp_dx * rail_offset), int(y1 + perp_dy * rail_offset))
        left_end = (int(x2 + perp_dx * rail_offset), int(y2 + perp_dy * rail_offset))
        right_start = (int(x1 - perp_dx * rail_offset), int(y1 - perp_dy * rail_offset))
        right_end = (int(x2 - perp_dx * rail_offset), int(y2 - perp_dy * rail_offset))

        pygame.draw.line(screen, BLACK, left_start, left_end, line_width)
        pygame.draw.line(screen, BLACK, right_start, right_end, line_width)


def get_expert_tile_image(tile_index, square_type, current_tile_images, squares_coords, next_positions):
    """Determine the correctly orientated texture for 1 and -2 spaces on the expert board.
    
    This function uses dynamic 'smarty pants' logic based on adjacent spaces in the path.
    Complies with Australian English spelling conventions.
    """
    if square_type == '1':
        # Orient based on the next space ("upper" space) in the player direction
        next_pos = next_positions[tile_index]
        if isinstance(next_pos, list):
            next_idx = next_pos[0]
        else:
            next_idx = next_pos
            
        if next_idx is not None and next_idx < len(squares_coords):
            x_curr, y_curr = squares_coords[tile_index]
            x_next, y_next = squares_coords[next_idx]
            
            dx = x_next - x_curr
            dy = y_next - y_curr
            
            if abs(dx) >= abs(dy):
                if dx >= 0:
                    return current_tile_images['1_East']
                else:
                    return current_tile_images['1_West']
            else:
                if dy >= 0:
                    # Next space is to the South (dy > 0). Use 1_North to point South.
                    return current_tile_images['1_North']
                else:
                    # Next space is to the North (dy < 0). Use 1_South to point North.
                    return current_tile_images['1_South']
        return current_tile_images['1_East']
        
    elif square_type == '-2':
        # Orient based on the previous space ("lower" space) in the player direction
        # Find the space that leads to tile_index
        prev_idx = None
        for p_idx in range(len(next_positions)):
            next_pos = next_positions[p_idx]
            if next_pos == tile_index:
                prev_idx = p_idx
                break
            elif isinstance(next_pos, list) and tile_index in next_pos:
                prev_idx = p_idx
                break
                
        if prev_idx is not None and prev_idx < len(squares_coords):
            x_curr, y_curr = squares_coords[tile_index]
            x_prev, y_prev = squares_coords[prev_idx]
            
            dx = x_prev - x_curr
            dy = y_prev - y_curr
            
            if abs(dx) >= abs(dy):
                if dx >= 0:
                    # Previous space is to the East, meaning we came FROM East
                    return current_tile_images['-2_East']
                else:
                    # Previous space is to the West, meaning we came FROM West
                    return current_tile_images['-2_West']
            else:
                if dy >= 0:
                    # Previous space is to the South (dy > 0). Use -2_North to point South.
                    return current_tile_images['-2_North']
                else:
                    # Previous space is to the North (dy < 0). Use -2_South to point North.
                    return current_tile_images['-2_South']
        return current_tile_images['-2_West']
        
    return current_tile_images.get(square_type)


def format_time(seconds):
    """Format elapsed time into MM:SS format."""
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02d}:{seconds:02d}"

def get_player_position_text(player, game_state):
    """Get the text describing the player's current position."""
    squares, _ = get_board_squares(game_state.get('selected_board', 'Classic'))
    
    if player.finished:
        return f"Finished (#{player.finish_order})"
    elif player.in_jail:
        return "In Jail!"
    elif player.position == 0:
        return "At Start"
    elif player.position >= len(squares) - 1:
        return "Finished!"
    else:
        sq_type = squares[player.position]
        if sq_type == '0':
            return f"Space {player.position} (Safe)"
        elif sq_type == '1':
            return f"Space {player.position} (+1)"
        elif sq_type == '-2':
            return f"Space {player.position} (-2)"
        elif sq_type == 'B':
            return f"Space {player.position} (Bonus)"
        elif sq_type == 'J':
            return f"Space {player.position} (Jail!)"
        elif sq_type == 'Q':
            return f"Space {player.position} (Quiz)"
        elif sq_type == 'P':
            return f"Space {player.position} (Fork)"
        else:
            return f"Space {player.position}"

def render_player_text(screen, font, prefix, player, y, scale, offset_y, player_colours):
    """Render text for a player with their specific colour."""
    label = font.render(f"P{player.id + 1}", True, player_colours[player.id])
    screen.blit(label, (int(10 * scale), int(y * scale + offset_y)))
    
    text = font.render(f"{prefix}", True, BLACK)
    screen.blit(text, (int(10 * scale) + label.get_width() + 5, int(y * scale + offset_y)))

def display_player_timers(game_state, screen, font, x, y_start, spacing, players, player_colours):
    """Display the timers for all players, sorted by fastest time if finished."""
    title = font.render("Player Times:", True, BLACK)
    screen.blit(title, (x, y_start))
    
    def sort_key(p):
        if p.finished and p.elapsed_time is not None:
            return (0, p.elapsed_time)
        elif p.start_time is not None:
            return (1, -(time.time() - p.start_time))
        else:
            return (2, 0)
            
    sorted_players = sorted([p for p in players if p.start_time is not None], key=sort_key)
    current_y = y_start + spacing
    
    for player in sorted_players:
        if player.finished and player.elapsed_time is not None:
            time_str = format_time(player.elapsed_time)
            status = f" (Finished #{player.finish_order})"
        elif player.start_time is not None:
            current_elapsed = time.time() - player.start_time
            time_str = format_time(current_elapsed)
            status = " (Playing)"
        else:
            continue
            
        label = font.render(f"P{player.id + 1}: ", True, player_colours[player.id])
        screen.blit(label, (x, current_y))
        
        time_text = font.render(f"{time_str}{status}", True, BLACK)
        screen.blit(time_text, (x + label.get_width(), current_y))
        current_y += spacing

def render_coloured_message(screen, font, message, x, y, offset_x, offset_y, players, player_colours):
    """Render a message with 'Player X' coloured in their specific colour."""
    if message.startswith("Player"):
        parts = message.split(" ", 2)
        if len(parts) >= 2 and parts[1].isdigit():
            player_num = int(parts[1])
            if 1 <= player_num <= len(players):
                player_idx = player_num - 1
                
                label = font.render(f"Player {player_num}", True, player_colours[player_idx])
                screen.blit(label, (x, y))
                
                if len(parts) > 2:
                    rest_text = font.render(f" {parts[2]}", True, BLACK)
                    screen.blit(rest_text, (x + label.get_width(), y))
                return
                
    text = font.render(message, True, BLACK)
    screen.blit(text, (x, y))

def render_wrapped_text(screen, font, text, max_width, x, y, color=BLACK, line_spacing=5, return_height_only=False):
    """Render text that wraps to the next line if it exceeds max_width."""
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        word_surface = font.render(word + ' ', True, color)
        word_width = word_surface.get_width()
        
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
            
    if current_line:
        lines.append(' '.join(current_line))
        
    total_height = 0
    for i, line in enumerate(lines):
        line_surface = font.render(line, True, color)
        if not return_height_only:
            screen.blit(line_surface, (x, y + i * (font.get_height() + line_spacing)))
        total_height += font.get_height() + line_spacing
        
    return total_height

def draw_card_with_shadow(screen, surf, pos, rot, scale, scale_val):
    """Helper for drawing a card with standard offset shadow."""
    shadow_offset = int(12 * scale * scale_val)
    rotated_surf = pygame.transform.rotate(surf, rot)
    shadow_surf = rotated_surf.copy()
    shadow_surf.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)

    shadow_rect = shadow_surf.get_rect(center=(pos[0] + shadow_offset, pos[1] + shadow_offset))
    screen.blit(shadow_surf, shadow_rect.topleft)

    card_rect = rotated_surf.get_rect(center=pos)
    screen.blit(rotated_surf, card_rect.topleft)

def draw_jail_free_micro_card(screen, pos, scale, camera_zoom, alpha=255):
    """Draw the held jail-free card at token scale."""
    image = AssetRegistry.bonus_result_images_original.get('expert_jail_free_micro')
    if image is None:
        return

    card_width = max(12, int(28 * scale * camera_zoom))
    card_height = max(9, int(card_width * image.get_height() / image.get_width()))
    card = pygame.transform.smoothscale(image, (card_width, card_height))
    if alpha < 255:
        card.set_alpha(alpha)

    shadow = card.copy()
    shadow.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
    shadow_rect = shadow.get_rect(center=(pos[0] + int(2 * scale), pos[1] + int(2 * scale)))
    card_rect = card.get_rect(center=pos)
    screen.blit(shadow, shadow_rect.topleft)
    screen.blit(card, card_rect.topleft)

def draw_player_badge(screen, player, badge_pos, badge_size, player_colours, cpu_difficulty_images_scaled, cpu_image_scaled, player_images_scaled):
    """Helper for drawing player badge on quiz card."""
    outer_radius = badge_size // 2
    inner_radius = int(outer_radius * 0.85)
    icon_size = int(badge_size * 0.75)
    
    shadow_surf = pygame.Surface((badge_size + 4, badge_size + 4), pygame.SRCALPHA)
    pygame.draw.circle(shadow_surf, (0, 0, 0, 80), (outer_radius + 2, outer_radius + 2), outer_radius)
    screen.blit(shadow_surf, (badge_pos[0] - outer_radius - 2, badge_pos[1] - outer_radius - 2))
    
    pygame.draw.circle(screen, WHITE, badge_pos, outer_radius)
    badge_colour = player_colours[player.colour_index]
    pygame.draw.circle(screen, badge_colour, badge_pos, inner_radius)
    
    if player.is_computer:
        icon_img = cpu_difficulty_images_scaled.get(player.difficulty, cpu_image_scaled)
    else:
        icon_img = player_images_scaled[player.colour_index]
        
    scaled_icon = pygame.transform.smoothscale(icon_img, (icon_size, icon_size))
    scaled_icon.set_alpha(255)
    screen.blit(scaled_icon, (badge_pos[0] - icon_size // 2, badge_pos[1] - icon_size // 2))

def draw_board(screen, players, game_state, scale, offset_x, offset_y, font, title_font):
    """Draw the game board and all its elements with camera operations and animations."""
    camera_zoom = game_state.get('camera_zoom', 1.0)
    board_type = game_state.get('selected_board', 'Classic')
    
    squares, next_positions = get_board_squares(board_type)
    if board_type == 'Expert':
        squares_coords = get_expert_squares_coords()
        jail_pos = EXPERT_JAIL_POS
    elif board_type == 'Secret':
        squares_coords = get_secret_squares_coords()
        jail_pos = SECRET_JAIL_POS
    else:
        squares_coords = get_classic_squares_coords()
        jail_pos = CLASSIC_JAIL_POS

    # Dynamically scale camera assets
    if abs(camera_zoom - 1.0) > 0.001:
        if (abs(AssetRegistry.camera_asset_cache['zoom'] - camera_zoom) < 0.001 and 
            abs(AssetRegistry.camera_asset_cache['scale'] - scale) < 0.001 and 
            AssetRegistry.camera_asset_cache['board_type'] == board_type):
            
            current_tile_images = AssetRegistry.camera_asset_cache['tiles']
            current_player_images = AssetRegistry.camera_asset_cache['players']
            current_cpu_difficulty_images = AssetRegistry.camera_asset_cache['cpu']
            current_dice_images = AssetRegistry.camera_asset_cache['dice']
        else:
            if board_type == 'Expert':
                tile_size = int((40 * scale) - (GAP_BETWEEN_TILES * scale * 0.3))
                player_size = int(35 * scale)
            elif board_type == 'Secret':
                tile_size = int(13 * scale)
                player_size = int(14 * scale)
            else:
                tile_size = int((60 * scale) - (GAP_BETWEEN_TILES * scale * 0.3))
                player_size = int(50 * scale)
            
            z_tile_size = int(tile_size * camera_zoom)
            z_player_size = int(player_size * camera_zoom)
            z_dice_size = int(55 * scale * camera_zoom)
            
            tile_images_set = AssetRegistry.board_tile_images[board_type]
            
            current_tile_images = {
                key: pygame.transform.smoothscale(img, (z_tile_size, z_tile_size))
                for key, img in tile_images_set.items() if key not in ['F', 'Jail']
            }
            
            if board_type == 'Classic':
                finish_rotated = pygame.transform.rotate(tile_images_set['F'], 90)
                finish_height = int((120 * scale) - (GAP_BETWEEN_TILES * scale * 0.3))
            elif board_type == 'Secret':
                finish_rotated = tile_images_set['F']
                finish_height = tile_size
            else:
                finish_rotated = tile_images_set['F']
                finish_height = tile_size
            
            current_tile_images['F'] = pygame.transform.smoothscale(finish_rotated, (z_tile_size, int(finish_height * camera_zoom)))
            
            if board_type == 'Expert':
                jail_scaled_size = int(tile_size * 4.1)
            elif board_type == 'Secret':
                jail_scaled_size = int(tile_size * 2.0)
            else:
                jail_scaled_size = int(tile_size * 1.5)
            
            current_tile_images['Jail'] = pygame.transform.smoothscale(tile_images_set['Jail'], (int(jail_scaled_size * camera_zoom), int(jail_scaled_size * camera_zoom)))
            
            current_player_images = [
                pygame.transform.smoothscale(img, (z_player_size, z_player_size))
                for img in AssetRegistry.player_images_original
            ]
            for img in current_player_images:
                img.set_alpha(191)
                
            current_cpu_difficulty_images = {
                key: pygame.transform.smoothscale(img, (z_player_size, z_player_size))
                for key, img in AssetRegistry.cpu_difficulty_images_original.items()
            }
            for img in current_cpu_difficulty_images.values():
                img.set_alpha(191)
                
            current_dice_images = [
                pygame.transform.smoothscale(img, (z_dice_size, z_dice_size))
                for img in AssetRegistry.dice_images_original
            ]
            
            AssetRegistry.camera_asset_cache = {
                'zoom': camera_zoom,
                'scale': scale,
                'board_type': board_type,
                'tiles': current_tile_images,
                'players': current_player_images,
                'cpu': current_cpu_difficulty_images,
                'dice': current_dice_images
            }
    else:
        current_tile_images = AssetRegistry.tile_images_scaled
        current_player_images = AssetRegistry.player_images_scaled
        current_cpu_difficulty_images = AssetRegistry.cpu_difficulty_images_scaled
        current_dice_images = AssetRegistry.dice_images_scaled

    # Background fills
    if board_type == 'Expert':
        screen.fill(DULL_PINK)
    elif board_type == 'Secret':
        screen.fill(DARK_GREEN)

        # Paired black pathway rails along each side of the spiral (under tiles and arrows)
        _draw_secret_pathway_rails(screen, squares_coords, scale, game_state, camera_zoom)
        
        # Secret board directional arrow overlays - drawn underneath the squares
        # Complies with Australian English spelling conventions
        if len(squares_coords) > 1:
            arrow_color = (255, 255, 255)
            for i in range(len(squares_coords) - 1):
                x1, y1 = camera.transform_coords(squares_coords[i][0], squares_coords[i][1], scale, game_state, screen.get_width(), screen.get_height())
                x2, y2 = camera.transform_coords(squares_coords[i+1][0], squares_coords[i+1][1], scale, game_state, screen.get_width(), screen.get_height())
                
                dx = x2 - x1
                dy = y2 - y1
                length = max(1, math.sqrt(dx*dx + dy*dy))
                dx /= length
                dy /= length
                
                # Position the white triangle centered exactly at the midpoint between spaces
                # This ensures the triangle and its angled sides are visible in the gap
                mid_x = (x1 + x2) // 2
                mid_y = (y1 + y2) // 2
                
                perp_dx = -dy
                perp_dy = dx
                
                # Base edge width stays wide; tip length is slightly shorter for a sharper pointer
                # Complies with Australian English spelling conventions
                arrow_length = max(3, int(5.2 * scale * camera_zoom))
                arrow_width = max(3, int(6.5 * scale * camera_zoom))
                
                # Tip points forward in the direction of movement, centered on the midpoint
                tip_x = int(mid_x + dx * arrow_length * 0.5)
                tip_y = int(mid_y + dy * arrow_length * 0.5)
                
                # Base is positioned backwards, showing the exaggerated angled edges in the gap
                arrow_p1_x = int(mid_x - dx * arrow_length * 0.5 + perp_dx * arrow_width)
                arrow_p1_y = int(mid_y - dy * arrow_length * 0.5 + perp_dy * arrow_width)
                arrow_p2_x = int(mid_x - dx * arrow_length * 0.5 - perp_dx * arrow_width)
                arrow_p2_y = int(mid_y - dy * arrow_length * 0.5 - perp_dy * arrow_width)
                
                pygame.draw.polygon(screen, arrow_color, [(tip_x, tip_y), (arrow_p1_x, arrow_p1_y), (arrow_p2_x, arrow_p2_y)])
    else:
        screen.fill(GRAY)

    free_parking_x = None
    free_parking_y = None
    free_parking_img = None

    # Render board squares
    for i, square in enumerate(squares):
        if i >= len(squares_coords):
            break
            
        x, y = camera.transform_coords(squares_coords[i][0], squares_coords[i][1], scale, game_state, screen.get_width(), screen.get_height())
        display_square = square
        
        if display_square in ['Go', 'B', 'Q', 'J', '0', 'P', 'F', 'FP']:
            img = current_tile_images[display_square]
            if display_square == 'FP' and game_state.get('free_parking_effect', False) and i == game_state.get('free_parking_position', -1):
                free_parking_x = x
                free_parking_y = y
                free_parking_img = img
                
        elif display_square == '1':
            if board_type in ['Expert', 'Secret']:
                img = get_expert_tile_image(i, '1', current_tile_images, squares_coords, next_positions)
            else:
                if i in [1, 6]:
                    img = current_tile_images['1_East']
                elif i in [12, 14]:
                    img = current_tile_images['1_North']
                elif i == 24 or i == 31:
                    img = current_tile_images['1_West']
                else:
                    img = current_tile_images['1_East']
        elif display_square == '-2':
            if board_type in ['Expert', 'Secret']:
                img = get_expert_tile_image(i, '-2', current_tile_images, squares_coords, next_positions)
            else:
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

        tile_rect = pygame.Rect(x - img.get_width() // 2, y - img.get_height() // 2, img.get_width(), img.get_height())

        if 'fade_start' in game_state:
            fade_time = time.time() - game_state['fade_start']
            if fade_time < 1.0:
                number_of_cycles = 6
                cycle_duration = 1.0 / number_of_cycles
                width_scale = (1 + math.sin(2 * math.pi * (fade_time / cycle_duration))) / 2
                squished_tile = pygame.transform.smoothscale(img, (int(img.get_width() * width_scale), img.get_height()))
                squished_rect = squished_tile.get_rect(center=tile_rect.center)
                screen.blit(squished_tile, squished_rect.topleft)
        else:
            tile_pos = (x - img.get_width() // 2, y - img.get_height() // 2)
            screen.blit(img, tile_pos)
            
            if board_type == 'Expert':
                outline_thickness = 2
                outline_rect = pygame.Rect(tile_pos[0] - outline_thickness, tile_pos[1] - outline_thickness, img.get_width() + (outline_thickness * 2), img.get_height() + (outline_thickness * 2))
                pygame.draw.rect(screen, (0, 0, 0), outline_rect, outline_thickness)
                
            if display_square == 'FP' and game_state.get('free_parking_effect', False) and i == game_state.get('free_parking_position', -1):
                current_time = time.time()
                elapsed = current_time - game_state['free_parking_start_time']
                duration = game_state['free_parking_duration']
                progress = elapsed / duration
                pulse = abs(math.sin(progress * math.pi * 4))
                
                glow_size = int(img.get_width() * 2.0)
                glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                
                for radius in range(5, int(glow_size/2), 4):
                    opacity = int(220 * (1 - radius/(glow_size/2)) * pulse)
                    if opacity > 0:
                        pygame.draw.circle(glow_surface, (255, 255, 0, opacity), (glow_size//2, glow_size//2), radius)
                
                screen.blit(glow_surface, (x - glow_surface.get_width()//2, y - glow_surface.get_height()//2))
                            
                for j in range(4):
                    angle = progress * 4 * math.pi + (j * math.pi / 2)
                    target_car_x = squares_coords[i][0] + (30 * (0.8 + 0.2 * pulse)) * math.cos(angle)
                    target_car_y = squares_coords[i][1] + (30 * (0.8 + 0.2 * pulse)) * math.sin(angle)
                    # Use current screen dimensions for coordinate transformation to ensure correct placement on Expert board
                    car_x, car_y = camera.transform_coords(target_car_x, target_car_y, scale, game_state, screen.get_width(), screen.get_height())
                    car_size = int(20 * scale * camera_zoom * (0.8 + 0.2 * pulse))
                    car_surface = pygame.Surface((car_size, car_size), pygame.SRCALPHA)
                    pygame.draw.circle(car_surface, (255, 255, 0, 240), (car_size//2, car_size//2), car_size//2)
                    pygame.draw.circle(car_surface, (0, 0, 0, 240), (car_size//2, car_size//2), car_size//2, 2)
                    screen.blit(car_surface, (car_x - car_size//2, car_y - car_size//2))

    # Render jail
    jail_x, jail_y = camera.transform_coords(jail_pos[0], jail_pos[1], scale, game_state, screen.get_width(), screen.get_height())
    jail_img = current_tile_images['Jail']
    jail_rect = pygame.Rect(jail_x - jail_img.get_width() // 2, jail_y - jail_img.get_height() // 2, jail_img.get_width(), jail_img.get_height())
    
    if 'fade_start' in game_state:
        fade_time = time.time() - game_state['fade_start']
        if fade_time < 1.0:
            number_of_cycles = 6
            cycle_duration = 1.0 / number_of_cycles
            width_scale = (1 + math.sin(2 * math.pi * (fade_time / cycle_duration))) / 2
            squished_jail = pygame.transform.smoothscale(jail_img, (int(jail_img.get_width() * width_scale), jail_img.get_height()))
            squished_rect = squished_jail.get_rect(center=jail_rect.center)
            screen.blit(squished_jail, squished_rect.topleft)
    else:
        screen.blit(jail_img, (jail_x - jail_img.get_width() // 2, jail_y - jail_img.get_height() // 2))

    # Card decks
    die_pos_x, die_pos_y = DIE_POS
    if board_type == 'Secret':
        if 'die_pos' in game_state:
            die_pos_x, die_pos_y = game_state['die_pos']
            
    die_center_x, die_center_y = camera.transform_coords(die_pos_x + 25, die_pos_y + 25, scale, game_state, screen.get_width(), screen.get_height())
    deck_scale_factor = 0.45 * camera_zoom
    deck_offset = int(110 * scale * camera_zoom)

    # Static Bonus Deck (Left)
    z_deck_width = int(280 * scale * deck_scale_factor)
    z_deck_height = int(z_deck_width * 3 / 4)
    bonus_deck_img = pygame.transform.smoothscale(AssetRegistry.cover_bonus_original, (z_deck_width, z_deck_height))
    bonus_deck_rotated = pygame.transform.rotate(bonus_deck_img, 90)
    bonus_deck_rect = bonus_deck_rotated.get_rect(center=(die_center_x - deck_offset, die_center_y))
    screen.blit(bonus_deck_rotated, bonus_deck_rect.topleft)

    # Static Quiz Deck (Right)
    z_qdeck_width = int(280 * scale * deck_scale_factor)
    z_qdeck_height = int(z_qdeck_width * 3 / 4)
    quiz_deck_img = pygame.transform.smoothscale(AssetRegistry.cover_quiz_original, (z_qdeck_width, z_qdeck_height))
    quiz_deck_rotated = pygame.transform.rotate(quiz_deck_img, -90)
    quiz_deck_rect = quiz_deck_rotated.get_rect(center=(die_center_x + deck_offset, die_center_y))
    screen.blit(quiz_deck_rotated, quiz_deck_rect.topleft)

    # Render Dice
    die_screen_x, die_screen_y = camera.transform_coords(die_pos_x, die_pos_y, scale, game_state, screen.get_width(), screen.get_height())
    dice_rect = pygame.Rect(die_screen_x, die_screen_y, int(50 * scale * camera_zoom), int(50 * scale * camera_zoom))
    
    is_expert_board = board_type == 'Expert'
    if is_expert_board:
        dice_rect1 = pygame.Rect(die_screen_x - int(35 * scale * camera_zoom), die_screen_y, int(50 * scale * camera_zoom), int(50 * scale * camera_zoom))
        dice_rect2 = pygame.Rect(die_screen_x + int(35 * scale * camera_zoom), die_screen_y, int(50 * scale * camera_zoom), int(50 * scale * camera_zoom))
        total_text_pos = (die_screen_x, die_screen_y + int(60 * scale * camera_zoom))
    
    if game_state.get('rolling_dice', False):
        if time.time() - game_state['dice_start_time'] < 1:
            if is_expert_board:
                for _ in range(2):
                    dice_face = random.choice(current_dice_images)
                    rand_x, rand_y = _random_visible_dice_pos(screen, dice_face)
                    screen.blit(dice_face, (rand_x, rand_y))
            else:
                dice_face = random.choice(current_dice_images)
                rand_x, rand_y = _random_visible_dice_pos(screen, dice_face)
                screen.blit(dice_face, (rand_x, rand_y))
        else:
            roll = game_state['dice_roll']
            if is_expert_board:
                roll1 = game_state['dice_roll_1']
                roll2 = game_state['dice_roll_2']
                dice_face1 = current_dice_images[roll1 - 1]
                screen.blit(dice_face1, dice_rect1.topleft)
                dice_face2 = current_dice_images[roll2 - 1]
                screen.blit(dice_face2, dice_rect2.topleft)
                
                total_font = pygame.font.SysFont(None, int(30 * scale * camera_zoom))
                total_text = total_font.render(f"Total: {roll}", True, BLACK)
                screen.blit(total_text, (total_text_pos[0] - total_text.get_width() // 2, total_text_pos[1]))
                
                game_state['final_dice_roll_1'] = roll1
                game_state['final_dice_roll_2'] = roll2
                
                if game_state.get('is_doubles') and not game_state.get('doubles_sound_played', False):
                    stylish_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Sound Effects/Stylish.opus"))
                    stylish_sound.set_volume(0.5)
                    stylish_sound.play()
                    game_state['doubles_sound_played'] = True
            else:
                dice_face = current_dice_images[roll - 1]
                screen.blit(dice_face, dice_rect.topleft)
            
            game_state['final_dice_roll'] = roll
            game_state['movement_delay_start'] = time.time()
            game_state['rolling_dice'] = False
            
    elif 'movement_delay_start' in game_state:
        current_time = time.time()
        roll = game_state['dice_roll']
        
        if is_expert_board:
            roll1 = game_state.get('final_dice_roll_1', 1)
            roll2 = game_state.get('final_dice_roll_2', 1)
            dice_face1 = current_dice_images[roll1 - 1]
            screen.blit(dice_face1, dice_rect1.topleft)
            dice_face2 = current_dice_images[roll2 - 1]
            screen.blit(dice_face2, dice_rect2.topleft)
            
            total_font = pygame.font.SysFont(None, int(30 * scale * camera_zoom))
            total_text = total_font.render(f"Total: {roll}", True, BLACK)
            screen.blit(total_text, (total_text_pos[0] - total_text.get_width() // 2, total_text_pos[1]))
        else:
            dice_face = current_dice_images[roll - 1]
            screen.blit(dice_face, dice_rect.topleft)
        
        if current_time - game_state['movement_delay_start'] >= 0.5:
            del game_state['movement_delay_start']
            current_player = players[game_state['current_player']]
            current_player.position_history.append(current_player.position)
            if current_player.in_jail:
                if roll % 2 == 0:
                    current_player.in_jail = False
                    current_player.jail_from_x = None
                    current_player.jail_from_y = None
                    current_player.jail_marker_anim_start = None
                    anim = {
                        'player': current_player,
                        'start_pos': jail_pos,
                        'end_pos': squares_coords[current_player.prev_position],
                        'steps': 60,
                        'current_step': 0,
                        'last_time': time.time(),
                        'message': f"Player {current_player.id + 1} rolled {roll} (even). Escaping jail.",
                        'is_jail_move': True,
                        'delay': 0.0167,
                        'jail_action': 'exit'
                    }
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
                    game_state['spaces_remaining'] = roll
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
        if board_type == 'Expert':
            roll1 = game_state.get('final_dice_roll_1', 1)
            roll2 = game_state.get('final_dice_roll_2', 1)
            roll = game_state['final_dice_roll']
            
            dice_rect1 = pygame.Rect(int((die_pos_x - 35) * scale + offset_x), int(die_pos_y * scale + offset_y), int(50 * scale), int(50 * scale))
            dice_rect2 = pygame.Rect(int((die_pos_x + 35) * scale + offset_x), int(die_pos_y * scale + offset_y), int(50 * scale), int(50 * scale))
            total_text_pos = (int(die_pos_x * scale + offset_x), int((die_pos_y + 60) * scale + offset_y))
            
            dice_face1 = AssetRegistry.dice_images_scaled[roll1 - 1]
            screen.blit(dice_face1, dice_rect1.topleft)
            dice_face2 = AssetRegistry.dice_images_scaled[roll2 - 1]
            screen.blit(dice_face2, dice_rect2.topleft)
            
            total_font = pygame.font.SysFont(None, int(30 * scale))
            total_text = total_font.render(f"Total: {roll}", True, BLACK)
            screen.blit(total_text, (total_text_pos[0] - total_text.get_width() // 2, total_text_pos[1]))
        else:
            dice_face = AssetRegistry.dice_images_scaled[game_state['final_dice_roll'] - 1]
            screen.blit(dice_face, dice_rect.topleft)

    # Position staggering for player tokens
    position_counts = {}
    current_player = players[game_state['current_player']]
    
    for player in players:
        if not player.finished or player.position == len(squares) - 1:
            key = "jail" if player.in_jail else (player.current_x, player.current_y)
            if key in position_counts:
                position_counts[key].append(player)
            else:
                position_counts[key] = [player]

    for position, players_at_position in position_counts.items():
        for idx, player in enumerate(players_at_position):
            if player.in_jail:
                if player.jail_x is not None and player.jail_y is not None:
                    x, y = camera.transform_coords(player.jail_x, player.jail_y, scale, game_state, screen.get_width(), screen.get_height())
                else:
                    jail_focus_x, jail_focus_y = jail_pos
                    jail_offset_x = random.randint(-int(JAIL_SIZE/3), int(JAIL_SIZE/3))
                    jail_offset_y = random.randint(-int(JAIL_SIZE/3), int(JAIL_SIZE/3))
                    player.jail_x = jail_focus_x + jail_offset_x
                    player.jail_y = jail_focus_y + jail_offset_y
                    x, y = camera.transform_coords(player.jail_x, player.jail_y, scale, game_state, screen.get_width(), screen.get_height())
            else:
                target_x = player.current_x
                target_y = player.current_y
                
                if player.position == 0:
                    target_x = squares_coords[0][0]
                    target_y = squares_coords[0][1]
                
                if len(players_at_position) > 1:
                    if idx > 0:
                        offset_amount = 15
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
                            angle = 2 * math.pi * (idx / 4)
                            distance = offset_amount * (1 + (idx // 4) * 0.5)
                            target_x += math.cos(angle) * distance
                            target_y += math.sin(angle) * distance
                
                x, y = camera.transform_coords(target_x, target_y, scale, game_state, screen.get_width(), screen.get_height())
            
            if player.is_computer:
                img = current_cpu_difficulty_images.get(player.difficulty, current_cpu_difficulty_images.get('normal'))
            else:
                img = current_player_images[player.colour_index]

            if game_state.get('victory_cutscene', False) and player.finished:
                scale_factor = getattr(player, 'victory_scale_factor', 1.0)
                if scale_factor == 1.0:
                    for anim in player.active_animations:
                        if anim.get('type') == 'victory_glide':
                            progress = min(1.0, (time.time() - anim['start_time']) / anim['duration'])
                            scale_factor = 1.0 + (anim['scale_factor'] - 1.0) * progress
                            break
                
                if scale_factor > 1.0:
                    orig_width, orig_height = img.get_width(), img.get_height()
                    new_width = int(orig_width * scale_factor)
                    new_height = int(orig_height * scale_factor)
                    img = pygame.transform.smoothscale(img, (new_width, new_height))
                    
                if game_state.get('victory_cutscene', False) and player.finished:
                    shadow_surface = pygame.Surface((img.get_width(), img.get_height()), pygame.SRCALPHA)
                    shadow_offset_x = 4
                    shadow_offset_y = 4
                    shadow_color = (20, 20, 20, 120)
                    
                    for px in range(img.get_width()):
                        for py in range(img.get_height()):
                            try:
                                if img.get_at((px, py))[3] > 50:
                                    shadow_surface.set_at((px, py), shadow_color)
                            except IndexError:
                                pass
                    
                    shadow_img_width = img.get_width()
                    shadow_img_height = img.get_height()
                    smaller = pygame.transform.smoothscale(shadow_surface, (shadow_img_width // 2, shadow_img_height // 2))
                    shadow_surface = pygame.transform.smoothscale(smaller, (shadow_img_width, shadow_img_height))
                    
                    shadow_pos_x = x - img.get_width() // 2 + shadow_offset_x
                    shadow_pos_y = y - img.get_height() // 2 + shadow_offset_y
                    screen.blit(shadow_surface, (shadow_pos_x, shadow_pos_y))
                    
                    if not (game_state.get('victory_cutscene', False) and player.finished):
                        transparent_img = img.copy()
                        transparent_img.set_alpha(243)
                        screen.blit(transparent_img, (x - img.get_width() // 2, y - img.get_height() // 2))
                    else:
                        screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))
            else:
                if player.id == current_player.id:
                    shadow_surface = pygame.Surface((img.get_width(), img.get_height()), pygame.SRCALPHA)
                    shadow_offset_x = 3
                    shadow_offset_y = 3
                    shadow_color = (20, 20, 20, 120)
                    
                    for px in range(img.get_width()):
                        for py in range(img.get_height()):
                            try:
                                if img.get_at((px, py))[3] > 50:
                                    shadow_surface.set_at((px, py), shadow_color)
                            except IndexError:
                                pass
                    
                    shadow_img_width = img.get_width()
                    shadow_img_height = img.get_height()
                    smaller = pygame.transform.smoothscale(shadow_surface, (shadow_img_width // 2, shadow_img_height // 2))
                    shadow_surface = pygame.transform.smoothscale(smaller, (shadow_img_width, shadow_img_height))
                    
                    shadow_pos_x = x - img.get_width() // 2 + shadow_offset_x
                    shadow_pos_y = y - img.get_height() // 2 + shadow_offset_y
                    screen.blit(shadow_surface, (shadow_pos_x, shadow_pos_y))
                    
                    transparent_img = img.copy()
                    transparent_img.set_alpha(243)
                    screen.blit(transparent_img, (x - img.get_width() // 2, y - img.get_height() // 2))
                else:
                    screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))

            if player.has_jail_free_card and getattr(player, 'jail_free_card_visible', False):
                micro_offset_x = img.get_width() // 2 + int(12 * scale * camera_zoom)
                micro_offset_y = -img.get_height() // 2
                draw_jail_free_micro_card(
                    screen,
                    (x + micro_offset_x, y + micro_offset_y),
                    scale,
                    camera_zoom
                )

    next_id = (game_state['current_player'] + 1) % len(players)
    while next_id < len(players) and players[next_id].finished and len(game_state.get('finish_order', [])) < len(players):
        next_id = (next_id + 1) % len(players)
    
    if not game_state.get('use_modern_status_display', True):
        if next_id < len(players):
            next_player = players[next_id]
            render_player_text(screen, font, "Current Turn: ", current_player, int(50 * scale), scale, offset_y, player_colours)
            render_player_text(screen, font, "Next Turn: ", next_player, int(80 * scale), scale, offset_y, player_colours)
    
        if 'message' in game_state:
            render_coloured_message(screen, font, game_state['message'], int(50 * scale), int(500 * scale), offset_x, offset_y, players, player_colours)

    screen_height = screen.get_height()
    restart_button_rect, achievement_button_rect, settings_button_rect, magnify_button_rect = get_ui_button_rects(
        game_state, scale, offset_x, offset_y, screen_height
    )

    if 'fade_start' in game_state:
        fade_time = time.time() - game_state['fade_start']
        if fade_time < 0.7:
            angle = (fade_time * 1080 / 0.7) % 360
            rotated_button = pygame.transform.rotate(AssetRegistry.restart_button_scaled, angle)
            rotated_rect = rotated_button.get_rect(center=restart_button_rect.center)
            screen.blit(rotated_button, rotated_rect.topleft)
        elif fade_time < 1.0:
            alpha = int(255 * (1 - (fade_time - 0.7) / 0.3))
            faded_button = AssetRegistry.restart_button_scaled.copy()
            faded_button.set_alpha(alpha)
            screen.blit(faded_button, restart_button_rect.topleft)
    elif game_state.get('restart_hold_start') is not None:
        hold_time = time.time() - game_state['restart_hold_start']
        progress = min(hold_time / 1.5, 1.0)
        shake_offset = int(5 * math.sin(hold_time * 10))
        draw_pos = (restart_button_rect.x + shake_offset, restart_button_rect.y)
        screen.blit(AssetRegistry.restart_button_scaled, draw_pos)
        
        bar_width = int(AssetRegistry.restart_button_scaled.get_width() * progress)
        bar_height = int(5 * scale)
        bar_rect = pygame.Rect(draw_pos[0], draw_pos[1] + AssetRegistry.restart_button_scaled.get_height(), bar_width, bar_height)
        pygame.draw.rect(screen, GREEN, bar_rect)
    else:
        screen.blit(AssetRegistry.restart_button_scaled, restart_button_rect.topleft)
    
    screen.blit(AssetRegistry.achievement_button_scaled, achievement_button_rect.topleft)
    screen.blit(AssetRegistry.settings_button_scaled, settings_button_rect.topleft)
    screen.blit(AssetRegistry.magnify_button_scaled, magnify_button_rect.topleft)

    # Settings panel overlays
    if game_state.get('show_settings_menu', False):
        menu_width = int(200 * scale)
        menu_height = int(370 * scale)
        
        menu_x = settings_button_rect.x + (settings_button_rect.width // 2) - (menu_width // 2)
        menu_y = settings_button_rect.y - menu_height - int(10 * scale)
        
        window_width, window_height = screen.get_size()
        
        if menu_x + menu_width > window_width:
            menu_x = window_width - menu_width - int(5 * scale)
        if menu_x < 0:
            menu_x = int(5 * scale)
        if menu_y < 0:
            menu_y = int(5 * scale)
            
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        
        pygame.draw.rect(screen, (240, 240, 240), menu_rect)
        pygame.draw.rect(screen, (40, 40, 40), menu_rect, 2)
        
        title_font_settings = pygame.font.SysFont(None, int(28 * scale))
        settings_title = title_font_settings.render("Settings", True, (0, 0, 0))
        screen.blit(settings_title, (menu_x + int(10 * scale), menu_y + int(10 * scale)))
        
        pygame.draw.line(screen, (150, 150, 150), (menu_x + int(5 * scale), menu_y + int(40 * scale)), (menu_x + menu_width - int(5 * scale), menu_y + int(40 * scale)), 1)
        
        status_font = pygame.font.SysFont(None, int(22 * scale))
        status_text = status_font.render("Show Game Status:", True, (0, 0, 0))
        screen.blit(status_text, (menu_x + int(10 * scale), menu_y + int(55 * scale)))
        
        toggle_width = int(40 * scale)
        toggle_height = int(20 * scale)
        status_toggle_rect = pygame.Rect(menu_x + menu_width - toggle_width - int(10 * scale), menu_y + int(55 * scale), toggle_width, toggle_height)
        
        toggle_color = (100, 200, 100) if game_state.get('show_game_status', False) else (150, 150, 150)
        pygame.draw.rect(screen, toggle_color, status_toggle_rect, border_radius=int(10 * scale))
        
        handle_pos = status_toggle_rect.right - int(18 * scale) if game_state.get('show_game_status', False) else status_toggle_rect.left + int(2 * scale)
        handle_rect = pygame.Rect(handle_pos, status_toggle_rect.y + int(2 * scale), int(16 * scale), int(16 * scale))
        pygame.draw.rect(screen, (240, 240, 240), handle_rect, border_radius=int(8 * scale))
        
        game_state['status_toggle_rect'] = status_toggle_rect
        
        style_text = status_font.render("Status Display:", True, (0, 0, 0))
        screen.blit(style_text, (menu_x + int(10 * scale), menu_y + int(85 * scale)))
        
        style_toggle_rect = pygame.Rect(menu_x + menu_width - toggle_width - int(10 * scale), menu_y + int(85 * scale), toggle_width, toggle_height)
        
        toggle_color = (100, 200, 100) if game_state.get('use_modern_status_display', True) else (150, 150, 150)
        pygame.draw.rect(screen, toggle_color, style_toggle_rect, border_radius=int(10 * scale))
        
        handle_pos = style_toggle_rect.right - int(18 * scale) if game_state.get('use_modern_status_display', True) else style_toggle_rect.left + int(2 * scale)
        handle_rect = pygame.Rect(handle_pos, style_toggle_rect.y + int(2 * scale), int(16 * scale), int(16 * scale))
        pygame.draw.rect(screen, (240, 240, 240), handle_rect, border_radius=int(8 * scale))
        
        game_state['style_toggle_rect'] = style_toggle_rect
        
        timer_text = status_font.render("Show Timers:", True, (0, 0, 0))
        screen.blit(timer_text, (menu_x + int(10 * scale), menu_y + int(115 * scale)))
        
        timer_toggle_rect = pygame.Rect(menu_x + menu_width - toggle_width - int(10 * scale), menu_y + int(115 * scale), toggle_width, toggle_height)
        
        toggle_color = (100, 200, 100) if game_state.get('show_timers', True) else (150, 150, 150)
        pygame.draw.rect(screen, toggle_color, timer_toggle_rect, border_radius=int(10 * scale))
        
        handle_pos = timer_toggle_rect.right - int(18 * scale) if game_state.get('show_timers', True) else timer_toggle_rect.left + int(2 * scale)
        handle_rect = pygame.Rect(handle_pos, timer_toggle_rect.y + int(2 * scale), int(16 * scale), int(16 * scale))
        pygame.draw.rect(screen, (240, 240, 240), handle_rect, border_radius=int(8 * scale))
        
        game_state['timer_toggle_rect'] = timer_toggle_rect
        
        questions_text = status_font.render("Speak Quiz Questions:", True, (0, 0, 0))
        screen.blit(questions_text, (menu_x + int(10 * scale), menu_y + int(145 * scale)))
        
        questions_toggle_rect = pygame.Rect(menu_x + menu_width - toggle_width - int(10 * scale), menu_y + int(145 * scale), toggle_width, toggle_height)
        
        toggle_color = (100, 200, 100) if game_state.get('speak_quiz_questions', True) else (150, 150, 150)
        pygame.draw.rect(screen, toggle_color, questions_toggle_rect, border_radius=int(10 * scale))
        
        handle_pos = questions_toggle_rect.right - int(18 * scale) if game_state.get('speak_quiz_questions', True) else questions_toggle_rect.left + int(2 * scale)
        handle_rect = pygame.Rect(handle_pos, questions_toggle_rect.y + int(2 * scale), int(16 * scale), int(16 * scale))
        pygame.draw.rect(screen, (240, 240, 240), handle_rect, border_radius=int(8 * scale))
        
        game_state['questions_toggle_rect'] = questions_toggle_rect
        
        answers_text = status_font.render("Speak Quiz Answers:", True, (0, 0, 0))
        screen.blit(answers_text, (menu_x + int(10 * scale), menu_y + int(175 * scale)))
        
        answers_toggle_rect = pygame.Rect(menu_x + menu_width - toggle_width - int(10 * scale), menu_y + int(175 * scale), toggle_width, toggle_height)
        
        toggle_color = (100, 200, 100) if game_state.get('speak_quiz_answers', True) else (150, 150, 150)
        pygame.draw.rect(screen, toggle_color, answers_toggle_rect, border_radius=int(10 * scale))
        
        handle_pos = answers_toggle_rect.right - int(18 * scale) if game_state.get('speak_quiz_answers', True) else answers_toggle_rect.left + int(2 * scale)
        handle_rect = pygame.Rect(handle_pos, answers_toggle_rect.y + int(2 * scale), int(16 * scale), int(16 * scale))
        pygame.draw.rect(screen, (240, 240, 240), handle_rect, border_radius=int(8 * scale))
        
        game_state['answers_toggle_rect'] = answers_toggle_rect

        source_text = status_font.render("Device TTS:", True, (0, 0, 0))
        screen.blit(source_text, (menu_x + int(10 * scale), menu_y + int(205 * scale)))

        tts_source_toggle_rect = pygame.Rect(menu_x + menu_width - toggle_width - int(10 * scale), menu_y + int(205 * scale), toggle_width, toggle_height)

        toggle_color = (100, 200, 100) if game_state.get('use_device_tts', False) else (150, 150, 150)
        pygame.draw.rect(screen, toggle_color, tts_source_toggle_rect, border_radius=int(10 * scale))

        handle_pos = tts_source_toggle_rect.right - int(18 * scale) if game_state.get('use_device_tts', False) else tts_source_toggle_rect.left + int(2 * scale)
        handle_rect = pygame.Rect(handle_pos, tts_source_toggle_rect.y + int(2 * scale), int(16 * scale), int(16 * scale))
        pygame.draw.rect(screen, (240, 240, 240), handle_rect, border_radius=int(8 * scale))

        game_state['tts_source_toggle_rect'] = tts_source_toggle_rect
        
        volume_text = status_font.render("Master Volume:", True, (0, 0, 0))
        screen.blit(volume_text, (menu_x + int(10 * scale), menu_y + int(235 * scale)))
        
        slider_width = int(150 * scale)
        slider_height = int(10 * scale)
        slider_rect = pygame.Rect(menu_x + int(25 * scale), menu_y + int(260 * scale), slider_width, slider_height)
        
        pygame.draw.rect(screen, (150, 150, 150), slider_rect, border_radius=int(5 * scale))
        
        volume = game_state.get('master_volume', 1.0)
        handle_pos = slider_rect.left + int(volume * slider_width)
        handle_rect = pygame.Rect(handle_pos - int(8 * scale), slider_rect.y - int(5 * scale), int(16 * scale), int(20 * scale))
        pygame.draw.rect(screen, (80, 80, 230), handle_rect, border_radius=int(8 * scale))
        
        game_state['volume_slider_rect'] = slider_rect
        game_state['volume_slider_width'] = slider_width
        
        reset_button_width = int(150 * scale)
        reset_button_height = int(30 * scale)
        reset_button_x = menu_x + (menu_width - reset_button_width) // 2
        reset_button_y = menu_y + int(300 * scale)
        reset_button_rect = pygame.Rect(reset_button_x, reset_button_y, reset_button_width, reset_button_height)
        
        pygame.draw.rect(screen, (220, 220, 220), reset_button_rect, border_radius=int(5 * scale))
        pygame.draw.rect(screen, (100, 100, 100), reset_button_rect, 2, border_radius=int(5 * scale))
        
        reset_text = status_font.render("Reset to Default", True, (0, 0, 0))
        text_x = reset_button_rect.x + (reset_button_rect.width - reset_text.get_width()) // 2
        text_y = reset_button_rect.y + (reset_button_rect.height - reset_text.get_height()) // 2
        screen.blit(reset_text, (text_x, text_y))
        
        game_state['reset_button_rect'] = reset_button_rect
        
    # Modern status overlay panel
    if game_state.get('show_game_status', True) and game_state.get('use_modern_status_display', False):
        current_player = players[game_state['current_player']]
        next_player_idx = (game_state['current_player'] + 1) % len(players)
        while next_player_idx < len(players) and players[next_player_idx].finished and len(game_state['finish_order']) < len(players) - 1:
            next_player_idx = (next_player_idx + 1) % len(players)
        next_player = players[next_player_idx]
        
        status_font = pygame.font.SysFont(None, int(20 * scale))
        message_font = pygame.font.SysFont(None, int(18 * scale))
        
        right_panel_x = int(650 * scale + offset_x)
        right_panel_y = int(100 * scale + offset_y)
        max_panel_width = int(200 * scale)
        
        current_player_text = f"Current: Player {current_player.id + 1}"
        if current_player.finished:
            current_player_text += " (Finished)"
        elif current_player.in_jail:
            current_player_text += " (In Jail)"
        
        color = player_colours[current_player.colour_index]
        current_text = status_font.render(current_player_text, True, color)
        screen.blit(current_text, (right_panel_x, right_panel_y))
        
        next_y = right_panel_y + status_font.get_height() + int(5 * scale)
        if len(game_state['finish_order']) < len(players) - 1:
            next_player_text = f"Next: Player {next_player.id + 1}"
            if next_player.in_jail:
                next_player_text += " (In Jail)"
                
            next_color = player_colours[next_player.colour_index]
            next_text = status_font.render(next_player_text, True, next_color)
            screen.blit(next_text, (right_panel_x, next_y))
        
        if game_state.get('message'):
            message_y = next_y + status_font.get_height() + int(10 * scale)
            message_text = game_state['message']
            parts = message_text.split("Player ")
            
            if len(parts) == 1:
                render_wrapped_text(screen, message_font, message_text, max_panel_width, right_panel_x, message_y, (50, 50, 50))
            else:
                current_y = message_y
                current_x = right_panel_x
                line_height = message_font.get_height() + int(2 * scale)
                
                if parts[0]:
                    height = render_wrapped_text(screen, message_font, parts[0], max_panel_width, current_x, current_y, (50, 50, 50))
                    current_y += height + int(2 * scale)
                    current_x = right_panel_x
                
                for i, part in enumerate(parts[1:], 1):
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
                                player_text = message_font.render("Player ", True, (50, 50, 50))
                                if current_x + player_text.get_width() > right_panel_x + max_panel_width:
                                    current_x = right_panel_x
                                    current_y += line_height
                                
                                screen.blit(player_text, (current_x, current_y))
                                current_x += player_text.get_width()
                                
                                player_color = player_colours[players[player_idx].colour_index]
                                number_text = message_font.render(player_num, True, player_color)
                                screen.blit(number_text, (current_x, current_y))
                                current_x += number_text.get_width()
                                
                                if remainder:
                                    if current_x > right_panel_x:
                                        if current_x + message_font.size(remainder[:5])[0] > right_panel_x + max_panel_width:
                                            current_x = right_panel_x
                                            current_y += line_height
                                    
                                    height = render_wrapped_text(screen, message_font, remainder, max_panel_width - (current_x - right_panel_x), current_x, current_y, (50, 50, 50))
                                    current_y += height
                                    current_x = right_panel_x
                            else:
                                full_text = message_font.render(f"Player {part}", True, (50, 50, 50))
                                if current_x + full_text.get_width() > right_panel_x + max_panel_width:
                                    current_x = right_panel_x
                                    current_y += line_height
                                
                                screen.blit(full_text, (current_x, current_y))
                                current_x += full_text.get_width()
                        except ValueError:
                            full_text = message_font.render(f"Player {part}", True, (50, 50, 50))
                            if current_x + full_text.get_width() > right_panel_x + max_panel_width:
                                current_x = right_panel_x
                                current_y += line_height
                            
                            screen.blit(full_text, (current_x, current_y))
                            current_x += full_text.get_width()
                    else:
                        full_text = message_font.render(f"Player {part}", True, (50, 50, 50))
                        if current_x + full_text.get_width() > right_panel_x + max_panel_width:
                            current_x = right_panel_x
                            current_y += line_height
                        
                        screen.blit(full_text, (current_x, current_y))
                        current_x += full_text.get_width()

    # Active Bonus Cards
    if 'bonus_image_key' in game_state and 'bonus_image_state' in game_state:
        image = AssetRegistry.bonus_result_images_scaled[game_state['bonus_image_key']]
        state = game_state['bonus_image_state']

        if state == 'growing':
            elapsed = time.time() - game_state['bonus_grow_start']
            scale_factor = min(1.0, elapsed / 1.0)
            rotation = 90 * (1.0 - scale_factor)

            start_x = die_center_x - deck_offset
            current_x = start_x + (die_center_x - start_x) * scale_factor
            current_y = die_center_y

            anim_scale = (0.45 + (1.0 - 0.45) * scale_factor) * camera_zoom
            scaled_width = int(280 * anim_scale * scale)
            scaled_height = int(scaled_width * 3 / 4)
            scaled_image = pygame.transform.smoothscale(AssetRegistry.cover_bonus_original, (scaled_width, scaled_height))
            draw_card_with_shadow(screen, scaled_image, (current_x, current_y), rotation, scale, scale_factor)

        elif state == 'flipping':
            elapsed = time.time() - game_state['bonus_flip_start']
            t = elapsed / 0.5
            if t < 0.5:
                width_scale = 1 - 2 * t
                img = AssetRegistry.cover_bonus_scaled
            else:
                width_scale = 2 * (t - 0.5)
                img = image
            scaled_width = max(1, int(img.get_width() * width_scale))
            scaled_image = pygame.transform.smoothscale(img, (scaled_width, img.get_height()))
            draw_card_with_shadow(screen, scaled_image, (die_center_x, die_center_y), 0, scale, 1.0)
        elif state == 'showing':
            z_width = int(image.get_width() * camera_zoom)
            z_height = int(image.get_height() * camera_zoom)
            scaled_image = pygame.transform.smoothscale(image, (z_width, z_height))
            draw_card_with_shadow(screen, scaled_image, (die_center_x, die_center_y), 0, scale, 1.0)
        elif state == 'gliding_to_player':
            elapsed = time.time() - game_state['bonus_glide_start']
            progress = min(1.0, elapsed / 1.0)
            t = 1.0 - (1.0 - progress) * (1.0 - progress)
            target_player_id = game_state.get('bonus_target_player_id', game_state['current_player'])
            target_player = next((p for p in players if p.id == target_player_id), players[game_state['current_player']])
            target_x, target_y = camera.transform_coords(
                target_player.current_x,
                target_player.current_y,
                scale,
                game_state,
                screen.get_width(),
                screen.get_height()
            )
            target_x += int(28 * scale * camera_zoom)
            target_y -= int(18 * scale * camera_zoom)

            current_x = die_center_x + (target_x - die_center_x) * t
            current_y = die_center_y + (target_y - die_center_y) * t
            draw_jail_free_micro_card(screen, (current_x, current_y), scale, camera_zoom)
        elif state == 'flipping_back':
            elapsed = time.time() - game_state['bonus_flip_back_start']
            t = elapsed / 0.5
            if t < 0.5:
                width_scale = 1 - 2 * t
                img = image
            else:
                width_scale = 2 * (t - 0.5)
                img = AssetRegistry.cover_bonus_scaled
            scaled_width = max(1, int(img.get_width() * width_scale))
            scaled_image = pygame.transform.smoothscale(img, (scaled_width, img.get_height()))
            draw_card_with_shadow(screen, scaled_image, (die_center_x, die_center_y), 0, scale, 1.0)
        elif state == 'shrinking':
            elapsed = time.time() - game_state['bonus_shrink_start']
            scale_factor = max(0.0, 1.0 - elapsed / 1.0)
            rotation = 90 * (1.0 - scale_factor)

            end_x = die_center_x - deck_offset
            current_x = die_center_x + (end_x - die_center_x) * (1.0 - scale_factor)
            current_y = die_center_y

            anim_scale = (0.45 + (1.0 - 0.45) * scale_factor) * camera_zoom
            scaled_width = int(280 * anim_scale * scale)
            scaled_height = int(scaled_width * 3 / 4)
            scaled_image = pygame.transform.smoothscale(AssetRegistry.cover_bonus_original, (scaled_width, scaled_height))
            draw_card_with_shadow(screen, scaled_image, (current_x, current_y), rotation, scale, scale_factor)

    # Active Quiz Cards
    if game_state.get('show_quiz', False) and game_state.get('quiz_question'):
        _quiz_player = players[game_state['current_player']]
        if _quiz_player.is_computer:
            _quiz_player_label = f"CPU Player {_quiz_player.id + 1}"
        else:
            _quiz_player_label = f"Player {_quiz_player.id + 1}"
        _quiz_label_colour = player_colours[_quiz_player.colour_index]
        _quiz_label_font = pygame.font.SysFont(None, int(18 * scale), bold=True)
        current_time = time.time()
        elapsed = current_time - game_state['quiz_start_time']
        
        quiz_width = int(320 * scale)
        quiz_height = int(quiz_width * 3 / 4)
        
        if game_state['quiz_state'] == 'growing':
            scale_factor = min(1.0, elapsed / 1.0)
            rotation = -90 * (1.0 - scale_factor)
            
            start_x = die_center_x + deck_offset
            current_x = start_x + (die_center_x - start_x) * scale_factor
            current_y = die_center_y
            
            anim_scale = (0.45 + (1.0 - 0.45) * scale_factor) * camera_zoom
            width = int(320 * anim_scale * scale)
            height = int(width * 3 / 4)
            
            scaled_cover = pygame.transform.smoothscale(AssetRegistry.cover_quiz_original, (width, height))
            draw_card_with_shadow(screen, scaled_cover, (current_x, current_y), rotation, scale, scale_factor)
            
            if elapsed >= 1.0:
                game_state['quiz_state'] = 'flipping'
                game_state['quiz_flip_start'] = current_time
        elif game_state['quiz_state'] == 'flipping':
            elapsed_flip = current_time - game_state['quiz_flip_start']
            t = elapsed_flip / 0.5
            if t < 0.5:
                width_scale = 1 - 2 * t
                scaled_width = max(1, int(quiz_width * width_scale))
                scaled_img = pygame.transform.smoothscale(AssetRegistry.cover_quiz_scaled, (scaled_width, quiz_height))
                draw_card_with_shadow(screen, scaled_img, (die_center_x, die_center_y), 0, scale, 1.0)
            else:
                width_scale = 2 * (t - 0.5)
                scaled_width = max(1, int(quiz_width * width_scale))
                rect = pygame.Rect(die_center_x - scaled_width // 2, die_center_y - quiz_height // 2, scaled_width, quiz_height)
                
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
            shadow_offset = int(12 * scale)
            shadow_rect = rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
            pygame.draw.rect(screen, WHITE, rect)
            
            text_margin = int(10 * scale)
            badge_size = int(48 * scale)
            badge_pos = (rect.left, rect.top)
            draw_player_badge(screen, _quiz_player, badge_pos, badge_size, player_colours, AssetRegistry.cpu_difficulty_images_scaled, AssetRegistry.cpu_image_scaled, AssetRegistry.player_images_scaled)
            
            _label_surf = _quiz_label_font.render(_quiz_player_label, True, _quiz_label_colour)
            screen.blit(_label_surf, (rect.x + text_margin + int(20 * scale), rect.y + text_margin))
            _label_h = _label_surf.get_height() + int(4 * scale)
            question, options, _ = game_state['quiz_question']
            max_text_width = quiz_width - 2 * text_margin
            render_wrapped_text(screen, font, question, max_text_width, rect.x + text_margin, rect.y + text_margin + _label_h)
            if current_time >= game_state['quiz_timer']:
                game_state['quiz_state'] = 'buttons'
                game_state['pop_played'] = False
        elif game_state['quiz_state'] == 'buttons':
            if not game_state['pop_played']:
                audio.pop_sound.play()
                game_state['pop_played'] = True
                if game_state.get('speak_quiz_questions', True):
                    question, _, _ = game_state['quiz_question']
                    is_expert = game_state.get('selected_board') == 'Expert'
                    quiz_tts.play_quiz_tts(question, is_expert)
                game_state['quiz_tts_started'] = True
                if game_state.get('speak_quiz_answers', True):
                    _, options, _ = game_state['quiz_question']
                    is_expert = game_state.get('selected_board') == 'Expert'
                    quiz_tts.queue_answers(options, is_expert)
            rect = pygame.Rect(die_center_x - quiz_width // 2, die_center_y - quiz_height // 2, quiz_width, quiz_height)
            shadow_offset = int(12 * scale)
            shadow_rect = rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
            pygame.draw.rect(screen, WHITE, rect)
            
            text_margin = int(10 * scale)
            badge_size = int(48 * scale)
            badge_pos = (rect.left, rect.top)
            draw_player_badge(screen, _quiz_player, badge_pos, badge_size, player_colours, AssetRegistry.cpu_difficulty_images_scaled, AssetRegistry.cpu_image_scaled, AssetRegistry.player_images_scaled)
            
            _label_surf = _quiz_label_font.render(_quiz_player_label, True, _quiz_label_colour)
            screen.blit(_label_surf, (rect.x + text_margin + int(20 * scale), rect.y + text_margin))
            _label_h = _label_surf.get_height() + int(4 * scale)
            question, options, _ = game_state['quiz_question']
            max_text_width = quiz_width - 2 * text_margin
            question_height = render_wrapped_text(screen, font, question, max_text_width, rect.x + text_margin, rect.y + text_margin + _label_h)
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
                render_wrapped_text(screen, option_font, option, max_option_width - number_surface.get_width() - 5, option_text_x, button.y + option_margin, WHITE)
                quiz_buttons.append((button, i))
            game_state['quiz_buttons'] = quiz_buttons
        elif game_state['quiz_state'] == 'answered':
            rect = pygame.Rect(die_center_x - quiz_width // 2, die_center_y - quiz_height // 2, quiz_width, quiz_height)
            shadow_offset = int(12 * scale)
            shadow_rect = rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
            pygame.draw.rect(screen, WHITE, rect)
            
            text_margin = int(10 * scale)
            badge_size = int(48 * scale)
            badge_pos = (rect.left, rect.top)
            draw_player_badge(screen, _quiz_player, badge_pos, badge_size, player_colours, AssetRegistry.cpu_difficulty_images_scaled, AssetRegistry.cpu_image_scaled, AssetRegistry.player_images_scaled)
            
            _label_surf = _quiz_label_font.render(_quiz_player_label, True, _quiz_label_colour)
            screen.blit(_label_surf, (rect.x + text_margin + int(20 * scale), rect.y + text_margin))
            _label_h = _label_surf.get_height() + int(4 * scale)
            question, _, _ = game_state['quiz_question']
            max_text_width = quiz_width - 2 * text_margin
            render_wrapped_text(screen, font, question, max_text_width, rect.x + text_margin, rect.y + text_margin + _label_h)
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
                shadow_offset = int(12 * scale)
                shadow_rect = rect.copy()
                shadow_rect.x += shadow_offset
                shadow_rect.y += shadow_offset
                pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
                pygame.draw.rect(screen, WHITE, rect)
            else:
                width_scale = 2 * (t - 0.5)
                scaled_width = max(1, int(quiz_width * width_scale))
                scaled_img = pygame.transform.smoothscale(AssetRegistry.cover_quiz_scaled, (scaled_width, quiz_height))
                draw_card_with_shadow(screen, scaled_img, (die_center_x, die_center_y), 0, scale, 1.0)
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
            
            anim_scale = (0.45 + (1.0 - 0.45) * scale_factor) * camera_zoom
            width = int(320 * anim_scale * scale)
            height = int(width * 3 / 4)
            
            scaled_cover = pygame.transform.smoothscale(AssetRegistry.cover_quiz_original, (width, height))
            draw_card_with_shadow(screen, scaled_cover, (current_x, current_y), rotation, scale, scale_factor)
            
            if elapsed_shrink >= 1.0:
                quiz_tts.stop_quiz_tts()
                game_state.pop('quiz_tts_started', None)
                game_state['show_quiz'] = False
                del game_state['quiz_question']
                del game_state['quiz_shrink_start']
                if 'quiz_answer_delay_start' in game_state:
                    del game_state['quiz_answer_delay_start']

    # Draw path choice
    if game_state.get('show_path_choice_after_roll', False):
        current_player = players[game_state['current_player']]
        current_pos = current_player.position
        choices = next_positions[current_pos]
        remaining_spaces = game_state.get('spaces_remaining', 0)

        for choice in choices:
            full_path = get_movement_path_with_choice(current_pos, choice, remaining_spaces, squares, next_positions)
            ending_pos = full_path[-1]

            x, y = squares_coords[ending_pos]
            x = int(x * scale + offset_x)
            y = int(y * scale + offset_y)

            pygame.draw.circle(screen, (255, 255, 0), (x, y), int(20 * scale), 3)

            img = AssetRegistry.player_images_scaled[current_player.colour_index]
            img_copy = img.copy()
            img_copy.set_alpha(150)
            screen.blit(img_copy, (x - img_copy.get_width() // 2, y - img_copy.get_height() // 2))

        dialog_width = int(300 * scale)
        dialog_height = int(180 * scale)
        rect = pygame.Rect(die_center_x - dialog_width // 2, die_center_y - dialog_height // 2, dialog_width, dialog_height)

        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, (0, 0, 100), rect, 3)

        _path_label_font = pygame.font.SysFont(None, int(18 * scale))
        if current_player.is_computer:
            _path_player_label = f"CPU Player {current_player.id + 1} — Choose a Path!"
        else:
            _path_player_label = f"Player {current_player.id + 1} — Choose Your Path!"
        _path_label_colour = player_colours[current_player.colour_index]

        _path_label_shadow = _path_label_font.render(_path_player_label, True, (100, 100, 100))
        screen.blit(_path_label_shadow, (rect.x + int(12 * scale), rect.y + int(12 * scale)))
        _path_label_surf = _path_label_font.render(_path_player_label, True, _path_label_colour)
        screen.blit(_path_label_surf, (rect.x + int(10 * scale), rect.y + int(10 * scale)))

        spaces_text = font.render(f"Remaining Spaces: {remaining_spaces}", True, (100, 0, 0))
        screen.blit(spaces_text, (rect.x + int(10 * scale), rect.y + int(32 * scale)))

        # Use different labels for expert board
        if game_state.get('selected_board') == 'Expert':
            labels = ["West", "South"]
        else:
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
                int(300 * scale),
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

            friendly_name = _get_friendly_square_name(end_square_type)
            dest_text = font.render(f"Ends on: {friendly_name}", True, (100, 0, 0))
            screen.blit(dest_text, (button.x + int(100 * scale), button.y + int(5 * scale)))

            game_state['path_buttons'].append((button, choice))

    # Jail markers
    standee_positions = {}
    for player in players:
        if player.jail_from_x is not None and player.jail_from_y is not None:
            square_x = int(player.jail_from_x * scale + offset_x)
            square_y = int(player.jail_from_y * scale + offset_y)
            
            for i, coord in enumerate(squares_coords):
                scaled_x = int(coord[0] * scale + offset_x)
                scaled_y = int(coord[1] * scale + offset_y)
                
                if abs(scaled_x - square_x) < 10 and abs(scaled_y - square_y) < 10:
                    position_key = str(i)
                    if position_key in standee_positions:
                        standee_positions[position_key].append(player)
                    else:
                        standee_positions[position_key] = [player]
                    break

    for position_key, players_at_position in standee_positions.items():
        tile_index = int(position_key)
        scaled_x = int(squares_coords[tile_index][0] * scale + offset_x)
        scaled_y = int(squares_coords[tile_index][1] * scale + offset_y)
        
        square_type = squares[tile_index]
        if square_type in AssetRegistry.tile_images_scaled:
            img = AssetRegistry.tile_images_scaled[square_type]
        elif square_type == '1':
            if board_type in ['Expert', 'Secret']:
                img = get_expert_tile_image(tile_index, '1', AssetRegistry.tile_images_scaled, squares_coords, next_positions)
            else:
                if tile_index in [1, 6]:
                    img = AssetRegistry.tile_images_scaled['1_East']
                elif tile_index in [12, 14]:
                    img = AssetRegistry.tile_images_scaled['1_North']
                elif tile_index == 24 or tile_index == 31:
                    img = AssetRegistry.tile_images_scaled['1_West']
                else:
                    img = AssetRegistry.tile_images_scaled['1_East']
        elif square_type == '-2':
            if board_type in ['Expert', 'Secret']:
                img = get_expert_tile_image(tile_index, '-2', AssetRegistry.tile_images_scaled, squares_coords, next_positions)
            else:
                if tile_index == 4:
                    img = AssetRegistry.tile_images_scaled['-2_West']
                elif tile_index in [13, 15]:
                    img = AssetRegistry.tile_images_scaled['-2_South']
                elif tile_index == 19:
                    img = AssetRegistry.tile_images_scaled['-2_East']
                elif tile_index in [28, 33, 35]:
                    img = AssetRegistry.tile_images_scaled['-2_North']
                else:
                    img = AssetRegistry.tile_images_scaled['-2_West']
        else:
            continue
        
        offset_val = int(5 * scale)
        tile_width = img.get_width()
        tile_height = img.get_height()
        
        for i, player in enumerate(players_at_position):
            stagger_offset = i * int(8 * scale)
            marker_x = scaled_x + tile_width // 2 - offset_val
            marker_y = scaled_y - tile_height // 2 + offset_val + stagger_offset
            
            marker_color = GRAY if player.is_computer else player_colours[player.colour_index]
            current_time = time.time()
            marker_radius = int(6 * scale)
            
            if player.jail_marker_anim_start:
                anim_duration = 0.25
                elapsed = current_time - player.jail_marker_anim_start
                
                if elapsed < anim_duration:
                    anim_progress = elapsed / anim_duration
                    animated_radius = int(marker_radius * anim_progress)
                    alpha = int(242 * anim_progress) if player.colour_index in [4, 5] else int(200 * anim_progress)
                    
                    surface_size = max(2, marker_radius * 2)
                    marker_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
                    center = surface_size // 2
                    pygame.draw.circle(marker_surface, marker_color + (alpha,), (center, center), animated_radius)
                    if animated_radius > 0:
                        pygame.draw.circle(marker_surface, BLACK + (alpha,), (center, center), animated_radius, 1)
                    screen.blit(marker_surface, (marker_x - center, marker_y - center))
                else:
                    marker_surface = pygame.Surface((marker_radius * 2, marker_radius * 2), pygame.SRCALPHA)
                    opacity = 242 if player.colour_index in [4, 5] else 128
                    pygame.draw.circle(marker_surface, marker_color + (opacity,), (marker_radius, marker_radius), marker_radius)
                    pygame.draw.circle(marker_surface, BLACK + (opacity,), (marker_radius, marker_radius), marker_radius, 1)
                    screen.blit(marker_surface, (marker_x - marker_radius, marker_y - marker_radius))
            else:
                marker_surface = pygame.Surface((marker_radius * 2, marker_radius * 2), pygame.SRCALPHA)
                opacity = 242 if player.colour_index in [4, 5] else 128
                pygame.draw.circle(marker_surface, marker_color + (opacity,), (marker_radius, marker_radius), marker_radius)
                pygame.draw.circle(marker_surface, BLACK + (opacity,), (marker_radius, marker_radius), marker_radius, 1)
                screen.blit(marker_surface, (marker_x - marker_radius, marker_y - marker_radius))

    # Free Parking orbit car animation drawn at the very end
    if free_parking_x is not None and free_parking_y is not None and free_parking_img is not None and game_state.get('free_parking_effect', False):
        current_time = time.time()
        elapsed = current_time - game_state['free_parking_start_time']
        duration = game_state['free_parking_duration']
        progress = elapsed / duration
        pulse = abs(math.sin(progress * math.pi * 4))
        
        glow_size = int(free_parking_img.get_width() * 2.5)
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        
        for radius in range(5, int(glow_size/2), 4):
            opacity = int(250 * (1 - radius/(glow_size/2)) * pulse)
            if opacity > 0:
                pygame.draw.circle(glow_surface, (255, 255, 0, opacity), (glow_size//2, glow_size//2), radius)
        
        screen.blit(glow_surface, (free_parking_x - glow_surface.get_width()//2, free_parking_y - glow_surface.get_height()//2))
                    
        for j in range(4):
            angle = progress * 4 * math.pi + (j * math.pi / 2)
            radius_val = 32 * scale * (0.8 + 0.2 * pulse)
            car_x = free_parking_x + radius_val * math.cos(angle)
            car_y = free_parking_y + radius_val * math.sin(angle)
            
            car_size = int(22 * scale * (0.8 + 0.2 * pulse))
            car_surface = pygame.Surface((car_size, car_size), pygame.SRCALPHA)
            pygame.draw.circle(car_surface, (255, 255, 0, 255), (car_size//2, car_size//2), car_size//2)
            pygame.draw.circle(car_surface, (0, 0, 0, 255), (car_size//2, car_size//2), car_size//2, 2)
            screen.blit(car_surface, (car_x - car_size//2, car_y - car_size//2))

    quiz_answer_rects = game_state.get('quiz_buttons', [])
    return dice_rect, restart_button_rect, achievement_button_rect, settings_button_rect, magnify_button_rect, quiz_answer_rects if game_state.get('quiz_buttons') else []
