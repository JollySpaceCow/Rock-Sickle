import random

def roll_die(difficulty=None):
    """Roll the die based on difficulty level."""
    if difficulty == 'easy':
        return random.choice([1, 1, 2, 2, 3, 4])
    elif difficulty == 'hard':
        return random.choice([3, 4, 5, 6, 6, 6])
    else:
        return random.randint(1, 6)

def interpolate_position(start_pos, end_pos, steps, current_step):
    """Calculate position between start and end for animations."""
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    x = start_x + (end_x - start_x) * current_step / steps
    y = start_y + (end_y - start_y) * current_step / steps
    return x, y

def get_movement_path(start_pos, spaces, game_state, squares, next_positions, in_jail=False):
    """Get the path for moving a certain number of spaces."""
    path = [start_pos]
    current_pos = start_pos
    if in_jail:
        return path
    for i in range(spaces):
        if current_pos >= len(squares) - 1:
            path.append(len(squares) - 1)
            break
        next_pos = next_positions[current_pos]
        if isinstance(next_pos, list):
            # Move to the choice point and stop
            path.append(current_pos)  # Stop at the choice point
            game_state['spaces_remaining'] = spaces - i  # Remaining spaces after reaching choice point
            break
        else:
            current_pos = next_pos if next_pos is not None else current_pos
            path.append(current_pos)
    else:
        game_state['spaces_remaining'] = 0  # Used all spaces if we didn't break
    return path

def get_movement_path_with_choice(start_pos, choice, remaining_spaces, squares, next_positions, started_on_choice=False):
    """Get the path when a player chooses a direction at a fork."""
    # If player started on the choice point, the first position is their current position (start_pos)
    # and their first move is from start_pos to the chosen path
    if started_on_choice:
        # Since the player is already on a P square, start_pos is where they are
        # and the first step is to move to the chosen path
        path = [start_pos]
        current_pos = start_pos
    else:
        # Player landed on the choice point during movement, so add both positions
        path = [start_pos, choice]
        current_pos = choice
    
    # Calculate remaining spaces after first move
    # If started on choice point, we use 1 space to move to choice, leaving (remaining_spaces-1)
    # If landed on choice during movement, we also subtract 1 because moving to choice uses 1 space
    spaces_to_move = remaining_spaces - 1
    
    # Move the first step to the chosen path if started on choice point
    if started_on_choice:
        current_pos = choice
        path.append(choice)
    
    # Move remaining spaces from the chosen path
    for _ in range(spaces_to_move):
        if current_pos >= len(squares) - 1:
            path.append(len(squares) - 1)
            break
        next_pos = next_positions[current_pos]
        if isinstance(next_pos, list):
            break
        else:
            current_pos = next_pos if next_pos is not None else current_pos
            path.append(current_pos)
    return path

def get_ending_position_after_choice(start_pos, choice, steps, squares, next_positions):
    """Determine final position after choosing a path."""
    path = get_movement_path_with_choice(start_pos, choice, steps, squares, next_positions)
    return path[-1]
