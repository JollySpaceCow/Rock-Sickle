"""Camera operations and coordinate transformations.

Provides functions to transform world coordinates to screen coordinates
and update camera target zoom/focus based on the camera mode.
"""

def transform_coords(x, y, scale, game_state, screen_width, screen_height):
    """Transform world coordinates to screen coordinates based on camera state.
    
    All inputs and calculations use Australian English spelling conventions.
    """
    camera_zoom = game_state.get('camera_zoom', 1.0)
    camera_focus_x = game_state.get('camera_focus_x', 400.0)
    camera_focus_y = game_state.get('camera_focus_y', 300.0)
    
    # Position relative to focus point (using centre of board)
    rel_x = x - camera_focus_x
    rel_y = y - camera_focus_y
    
    # Scale by camera zoom and window scale
    screen_x = rel_x * camera_zoom * scale + screen_width / 2
    screen_y = rel_y * camera_zoom * scale + screen_height / 2
    
    return int(screen_x), int(screen_y)

def update_camera_targets(game_state, players):
    """Calculate target camera focus and zoom based on current mode."""
    mode = game_state.get('camera_mode', 0)
    
    # Default values (using centre of 800x600 board)
    target_zoom = 1.0
    target_focus_x = 400.0
    target_focus_y = 300.0
    
    if mode == 1:  # All Players
        active_players = [p for p in players if not p.finished]
        if active_players:
            min_x = min(p.current_x for p in active_players)
            max_x = max(p.current_x for p in active_players)
            min_y = min(p.current_y for p in active_players)
            max_y = max(p.current_y for p in active_players)
            
            target_focus_x = (min_x + max_x) / 2
            target_focus_y = (min_y + max_y) / 2
            
            # Add padding
            width = (max_x - min_x) + 200
            height = (max_y - min_y) + 200
            
            # Calculate required zoom to fit this bounding box
            zoom_x = 800 / max(1, width)
            zoom_y = 600 / max(1, height)
            target_zoom = min(zoom_x, zoom_y, 4.0)  # Cap zoom at 4.0
            target_zoom = max(target_zoom, 1.0)  # Don't zoom out past 1.0
        
    elif mode == 2:  # Current Player
        cp_idx = game_state.get('current_player', 0)
        if cp_idx < len(players):
            cp = players[cp_idx]
            target_focus_x = cp.current_x
            target_focus_y = cp.current_y
            target_zoom = 2.5  # Nice close up
            
    game_state['camera_target_zoom'] = target_zoom
    game_state['camera_target_focus_x'] = target_focus_x
    game_state['camera_target_focus_y'] = target_focus_y
