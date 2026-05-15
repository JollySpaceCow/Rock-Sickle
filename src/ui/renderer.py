import pygame

# Constants needed for rendering text
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GREY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

def format_time(seconds):
    """Format elapsed time into MM:SS format."""
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02d}:{seconds:02d}"

def get_player_position_text(player, game_state):
    """Get the text describing the player's current position."""
    from src.game.board import get_board_squares
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
        # Give a descriptive name based on the square type
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
    import time
    title = font.render("Player Times:", True, BLACK)
    screen.blit(title, (x, y_start))
    
    # Create a list of players to sort
    def sort_key(p):
        if p.finished and p.elapsed_time is not None:
            return (0, p.elapsed_time)  # Finished players first, sorted by time
        elif p.start_time is not None:
            # Active players next, sorted by current elapsed time (longest first)
            return (1, -(time.time() - p.start_time))
        else:
            return (2, 0)  # Haven't started yet
            
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
                
    # Fallback to normal rendering if not matching "Player X ..."
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
