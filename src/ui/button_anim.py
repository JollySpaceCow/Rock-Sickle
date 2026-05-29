"""Fly-in animation for bottom-bar UI buttons at game start."""
import time

FLY_DURATION = 0.55
STAGGER = 0.05
BUTTON_X_BASES = (610, 670, 730, 790)  # restart, achievement, settings, magnify
FINAL_Y_BASE = 540


def ease_out_back(t):
    """Ease 0→1 with slight overshoot past the destination."""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def get_fly_in_y_offset(game_state, button_index, scale, screen_height, offset_y):
    """Pixels below final position; 0 when the button has settled."""
    start = game_state.get('ui_buttons_fly_in_start')
    if start is None:
        return 0

    final_y = FINAL_Y_BASE * scale + offset_y
    fly_distance = screen_height - final_y + int(80 * scale)

    elapsed = time.time() - start - button_index * STAGGER
    if elapsed <= 0:
        return int(fly_distance)
    t = min(1.0, elapsed / FLY_DURATION)
    if t >= 1.0:
        return 0

    progress = ease_out_back(t)
    return int(fly_distance * (1 - progress))


def update_ui_buttons_fly_in(game_state):
    """Clear fly-in state once every button has finished animating."""
    start = game_state.get('ui_buttons_fly_in_start')
    if start is None:
        return
    total_time = FLY_DURATION + STAGGER * (len(BUTTON_X_BASES) - 1)
    if time.time() - start >= total_time:
        del game_state['ui_buttons_fly_in_start']


def get_ui_button_rects(game_state, scale, offset_x, offset_y, screen_height):
    """Return screen rects for bottom UI buttons (with fly-in offset applied)."""
    import pygame

    button_size = int(50 * scale)
    rects = []
    for i, x_base in enumerate(BUTTON_X_BASES):
        y_offset = get_fly_in_y_offset(game_state, i, scale, screen_height, offset_y)
        rects.append(pygame.Rect(
            int(x_base * scale + offset_x),
            int(FINAL_Y_BASE * scale + offset_y + y_offset),
            button_size,
            button_size,
        ))
    return rects
