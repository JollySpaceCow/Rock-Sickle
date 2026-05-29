import random

# Cache randomised secret board to prevent flashing on rendering
# Complies with Australian English spelling conventions
_cached_secret_squares = None
_cached_secret_next_positions = None

# Define a small gap between squares (represents 1mm)
GAP_BETWEEN_TILES = 2  # Pixels representing gap between tiles

def get_board_squares(board_type="Classic"):
    global _cached_secret_squares, _cached_secret_next_positions
    
    if board_type == "Classic":
        return [
            'Go', '1', '0', 'Q', '-2', 'J', '1', 'B', '0', '0',
            'J', '0', '1', '-2', '1', '-2', '0',
            'B', '0', '-2', 'Q', 'B', 'P',
            '0', '1', 'B', 'J', 'Q', '-2', '0',
            '0', '1', 'J', '-2', 'Q', '-2', '0',
            'F'
        ], list(range(1, 23)) + [[23, 30]] + list(range(24, 30)) + [37] + list(range(31, 37)) + [37] + [None]
    elif board_type == "Secret":
        if _cached_secret_squares is not None:
            return _cached_secret_squares, _cached_secret_next_positions
            
        # Initialise seed-based random generator to ensure consistency
        # Complies with Australian English spelling conventions
        local_random = random.Random("secret")
        
        # Create a 1000-space secret board with a winding pattern
        secret_squares = ['Go']
        
        # Fill the board with 998 random spaces (ensuring a good mix of types)
        square_types = ['0', '1', '-2', 'B', 'J', 'Q']
        weights = [3, 3, 3, 2, 2, 2]  # Weights for more balanced distribution
        
        # Generate 998 spaces with weighted random distribution, avoiding problematic sequences
        prev_two_squares = []  # Keep track of the last two squares
        
        for i in range(998):
            # For the first two spaces (index 1 and 2), do not allow '-2' to avoid going back to Go
            if i < 2:
                valid_types = [t for t in square_types if t != '-2']
                valid_weights = [weights[square_types.index(t)] for t in valid_types]
                space_type = local_random.choices(valid_types, weights=valid_weights, k=1)[0]
            # Prevent problematic sequences like "1, 1, -2" that could cause softlocks
            elif len(prev_two_squares) >= 2 and prev_two_squares[-2:] == ['1', '1']:
                # If we have "1, 1", don't allow "-2" next
                valid_types = [t for t in square_types if t != '-2']
                valid_weights = [weights[square_types.index(t)] for t in valid_types]
                space_type = local_random.choices(valid_types, weights=valid_weights, k=1)[0]
            elif len(prev_two_squares) >= 2 and prev_two_squares[-2:] == ['-2', '-2']:
                # If we have "-2, -2", don't allow another "-2" to avoid excessive backtracking
                valid_types = [t for t in square_types if t != '-2']
                valid_weights = [weights[square_types.index(t)] for t in valid_types]
                space_type = local_random.choices(valid_types, weights=valid_weights, k=1)[0]
            else:
                # Normal random selection
                space_type = local_random.choices(square_types, weights=weights, k=1)[0]
            
            # Add the selected space type
            secret_squares.append(space_type)
            
            # Update the history of previous squares
            prev_two_squares.append(space_type)
            if len(prev_two_squares) > 2:
                prev_two_squares.pop(0)
        
        # Add the finish at the end
        secret_squares.append('F')
        
        # Simple sequential next positions (no branching paths)
        secret_next_positions = list(range(1, 1000)) + [None]
        
        _cached_secret_squares = secret_squares
        _cached_secret_next_positions = secret_next_positions
        
        return _cached_secret_squares, _cached_secret_next_positions
    else:  # Expert board
        # Properly structured expert board based on Kong.rtf
        expert_squares = []
        
        # [Direction East] 1, Q, -2, J, 1, B, -2, 1, J, Q, Q, J, 1, Q, -2
        expert_squares.extend(['Go', '1', 'Q', '-2', 'J', '1', 'B', '-2', '1', 'J', 'Q', 'Q', 'J', '1', 'Q', '-2'])
        
        # [Direction South] 1, B, 1, 0, 0, -2, P
        expert_squares.extend(['1', 'B', '1', 'FP', '0', '-2', 'P'])
        
        # Path directions after P - here we need to account for all possible paths
        # (Path West) [Direction West] 0, -2, J, 1, 1
        west_path_1 = ['0', '-2', 'J', '1', '1']
        
        # (Path West) [Direction South] 0
        west_path_2 = ['0']
        
        # (Path West) [Direction West] 1
        west_path_3 = ['1']
        
        # (Path West) [Direction South] -2, 0
        west_path_4 = ['-2', '0']
        
        # (Path West) [Direction East] 0
        west_path_5 = ['0']
        
        # (Path West) [Direction South] 0, 0
        west_path_6 = ['0', '0']
        
        # (Path West) [Direction West] B, 0, 1, -2, 1, -2, J, 1, B, -2
        west_path_7 = ['B', '0', '1', '-2', '1', '-2', 'J', '1', 'B', '-2']
        
        # (Path West) [Direction North] 1, 1, B, Q, 1, 1, J, -2, Q, B, Finish
        west_path_8 = ['1', '1', 'B', 'Q', '1', '1', 'J', '-2', 'Q', 'B', 'F']
        
        # (Path South) [Direction South] 0, 1, Q, -2, B
        # Adjust to end with the B square that should be at the corner
        south_path_1 = ['0', '1', 'Q', '-2', 'B']
        
        # (Path South) [Direction West] 1, J, 1, -2, 0, B, 0, 1, -2, 1, -2, J, 1, B, -2
        # Update to match the requested layout exactly
        south_path_2 = ['1', 'J', '1', '-2', '0', 'B', '0', '1', '-2', '1', '-2', 'J', '1', 'B', '-2']
        
        # (Path South) [Direction North] 1, 1, B, Q, 1, 1, J, -2, Q, B, Finish
        # Update to match the requested layout exactly
        south_path_3 = ['1', '1', 'B', 'Q', '1', '1', 'J', '-2', 'Q', 'B', 'F']
        
        # Now we need to add junction/path selection logic - this will be handled in next_positions
        # For now, we're just creating the complete board
        west_path = west_path_1 + west_path_2 + west_path_3 + west_path_4 + west_path_5 + west_path_6 + west_path_7 + west_path_8
        south_path = south_path_1 + south_path_2 + south_path_3
        
        # Build next_positions for expert board
        # This is complex and needs to account for the multiple paths
        expert_next_positions = []
        
        # First, handle the straight parts (East and South until P)
        main_path_length = len(expert_squares)
        for i in range(main_path_length - 1):  # All but P
            expert_next_positions.append(i + 1)
        
        # At P, we have a choice - west path or south path
        # The choice will be represented as a list of options
        # We'll add path choice at the P position
        pick_path_pos = main_path_length - 1  # P's position
        west_path_start = main_path_length
        south_path_start = main_path_length + len(west_path)
        expert_next_positions.append([west_path_start, south_path_start])
        
        # Add the west path positions
        for i in range(len(west_path) - 1):
            expert_next_positions.append(west_path_start + i + 1)
        # Last position on west path leads to finish
        expert_next_positions.append(None)  # Finish
        
        # Add the south path positions
        for i in range(len(south_path) - 1):
            expert_next_positions.append(south_path_start + i + 1)
        # Last position on south path leads to finish
        expert_next_positions.append(None)  # Finish
        
        # Complete expert board with all paths
        complete_expert_squares = expert_squares + west_path + south_path
        
        return complete_expert_squares, expert_next_positions

# Modified squares_coords with gaps between adjacent tiles - this is for the Classic board
def get_classic_squares_coords():
    return [
        (60, 60),                                  # Go - corner
        (120 + GAP_BETWEEN_TILES, 60),             # Horizontal row - top
        (180 + 2*GAP_BETWEEN_TILES, 60),
        (240 + 3*GAP_BETWEEN_TILES, 60),
        (300 + 4*GAP_BETWEEN_TILES, 60),
        (360 + 5*GAP_BETWEEN_TILES, 60),
        (420 + 6*GAP_BETWEEN_TILES, 60),
        (480 + 7*GAP_BETWEEN_TILES, 60),
        (540 + 8*GAP_BETWEEN_TILES, 60),
        (600 + 9*GAP_BETWEEN_TILES, 60),           # Corner
        
        (600 + 9*GAP_BETWEEN_TILES, 120 + GAP_BETWEEN_TILES),    # Vertical column - right
        (600 + 9*GAP_BETWEEN_TILES, 180 + 2*GAP_BETWEEN_TILES),
        (600 + 9*GAP_BETWEEN_TILES, 240 + 3*GAP_BETWEEN_TILES),
        (600 + 9*GAP_BETWEEN_TILES, 300 + 4*GAP_BETWEEN_TILES),
        (600 + 9*GAP_BETWEEN_TILES, 360 + 5*GAP_BETWEEN_TILES),
        (600 + 9*GAP_BETWEEN_TILES, 420 + 6*GAP_BETWEEN_TILES),
        (600 + 9*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),  # Corner
        
        (540 + 8*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),  # Horizontal row - bottom 
        (480 + 7*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        (420 + 6*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        (360 + 5*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        (300 + 4*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        (240 + 3*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        
        (240 + 3*GAP_BETWEEN_TILES, 420 + 6*GAP_BETWEEN_TILES),  # Vertical column - central
        (240 + 3*GAP_BETWEEN_TILES, 360 + 5*GAP_BETWEEN_TILES),
        (180 + 2*GAP_BETWEEN_TILES, 360 + 5*GAP_BETWEEN_TILES),  # Horizontal row - central
        (120 + GAP_BETWEEN_TILES, 360 + 5*GAP_BETWEEN_TILES),
        (60, 360 + 5*GAP_BETWEEN_TILES),
        (60, 300 + 4*GAP_BETWEEN_TILES),           # Vertical column - left (part 1)
        (60, 240 + 3*GAP_BETWEEN_TILES),
        
        (180 + 2*GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),  # Another path from bottom
        (120 + GAP_BETWEEN_TILES, 480 + 7*GAP_BETWEEN_TILES),
        (60, 480 + 7*GAP_BETWEEN_TILES),           # Corner
        (60, 420 + 6*GAP_BETWEEN_TILES),           # Vertical column - left (part 2) 
        (60, 360 + 5*GAP_BETWEEN_TILES),
        (60, 300 + 4*GAP_BETWEEN_TILES),
        (60, 240 + 3*GAP_BETWEEN_TILES),
        
        (60, 155 + 2*GAP_BETWEEN_TILES - 5)            # Finish line
    ]

# For the Expert board, we create a more complex layout for the larger board
def get_expert_squares_coords():
    # Make the tile size smaller to fit the larger expert board on screen
    tile_size = 40  # Smaller tiles for expert board to fit everything
    gap = 1  # Smaller gap between tiles to make everything more compact
    
    coords = []
    
    # Starting point (Go) - keep near top-left corner
    base_x = 50
    base_y = 50
    
    # [Direction East] - First row going east - compacted
    east_row_length = 16  # 'Go' + 15 tiles
    for i in range(east_row_length):
        coords.append((base_x + i * (tile_size + gap), base_y))
    
    # [Direction South] - Column going south from the east end
    south_col_length = 7
    last_x = base_x + (east_row_length - 1) * (tile_size + gap)
    for i in range(1, south_col_length + 1):
        coords.append((last_x, base_y + i * (tile_size + gap)))
    
    # P square position - this is where we branch
    p_position = len(coords) - 1
    
    # Path West positions
    # (Path West) [Direction West] - First segment going west
    west_path_1_length = 5
    west_path_start_x = last_x - (tile_size + gap)
    west_path_start_y = base_y + south_col_length * (tile_size + gap)
    for i in range(1, west_path_1_length + 1):
        coords.append((west_path_start_x - (i - 1) * (tile_size + gap), west_path_start_y))
    
    # (Path West) [Direction South] - First southern segment on west path
    west_path_south_1_y = west_path_start_y + (tile_size + gap)
    coords.append((west_path_start_x - (west_path_1_length - 1) * (tile_size + gap), west_path_south_1_y))
    
    # (Path West) [Direction West] - Continue west
    west_path_2_x = west_path_start_x - west_path_1_length * (tile_size + gap)
    coords.append((west_path_2_x, west_path_south_1_y))
    
    # (Path West) [Direction South] - Second southern segment
    west_path_south_2_length = 2
    for i in range(1, west_path_south_2_length + 1):
        coords.append((west_path_2_x, west_path_south_1_y + i * (tile_size + gap)))
    
    # (Path West) [Direction East] - Go east after south
    coords.append((west_path_2_x + (tile_size + gap), west_path_south_1_y + west_path_south_2_length * (tile_size + gap)))
    
    # (Path West) [Direction South] - Third southern segment
    west_path_south_3_start_x = west_path_2_x + (tile_size + gap)
    west_path_south_3_start_y = west_path_south_1_y + west_path_south_2_length * (tile_size + gap)
    west_path_south_3_length = 2
    for i in range(1, west_path_south_3_length + 1):
        coords.append((west_path_south_3_start_x, west_path_south_3_start_y + i * (tile_size + gap)))
    
    # (Path West) [Direction West] - Long segment going west
    west_path_3_length = 10
    west_path_3_start_x = west_path_south_3_start_x
    west_path_3_start_y = west_path_south_3_start_y + west_path_south_3_length * (tile_size + gap)
    for i in range(1, west_path_3_length + 1):
        # Shift one more tile west by adding an extra tile_size to the calculation
        coords.append((west_path_3_start_x - (i - 1) * (tile_size + gap) - (tile_size + gap), west_path_3_start_y))
    
    # (Path West) [Direction North] - Final segment going north to finish
    west_path_north_length = 11
    # Adjust the starting x position based on our shifted western path
    west_path_north_start_x = west_path_3_start_x - (west_path_3_length - 1) * (tile_size + gap) - (tile_size + gap)
    west_path_north_start_y = west_path_3_start_y
    for i in range(1, west_path_north_length + 1):
        # Shift one more tile up by adding an extra tile_size to the calculation
        coords.append((west_path_north_start_x, west_path_north_start_y - (i - 1) * (tile_size + gap) - (tile_size + gap)))
    
    # Path South positions
    # (Path South) [Direction South] - First segment going south
    south_path_1_length = 5  # matching the 5 squares in south_path_1
    south_path_start_x = last_x
    south_path_start_y = base_y + (south_col_length + 1) * (tile_size + gap)
    for i in range(1, south_path_1_length + 1):
        coords.append((south_path_start_x, south_path_start_y + (i - 1) * (tile_size + gap)))
    
    # (Path South) [Direction West] - Going west after south
    south_path_west_length = 15  # matching the 15 squares in south_path_2
    south_path_west_start_x = south_path_start_x
    south_path_west_start_y = south_path_start_y + (south_path_1_length - 1) * (tile_size + gap)
    for i in range(1, south_path_west_length + 1):
        # Shift one more tile west by adding an extra tile_size to the calculation
        coords.append((south_path_west_start_x - (i - 1) * (tile_size + gap) - (tile_size + gap), south_path_west_start_y))
    
    # (Path South) [Direction North] - Final segment going north to finish
    south_path_north_length = 11  # matching the 11 squares in south_path_3
    # Adjust the starting x position based on our shifted western path
    south_path_north_start_x = south_path_west_start_x - (south_path_west_length - 1) * (tile_size + gap) - (tile_size + gap)
    south_path_north_start_y = south_path_west_start_y
    for i in range(1, south_path_north_length + 1):
        # Shift one more tile up by adding an extra tile_size to the calculation
        coords.append((south_path_north_start_x, south_path_north_start_y - (i - 1) * (tile_size + gap) - (tile_size + gap)))
    
    return coords

# Secret board coordinates - create a winding spiral pattern with 1000 spaces
def get_secret_squares_coords():
    # Create a more consistent grid-based spiral pattern for the Secret board
    coordinates = []
    
    # Center point of the pattern
    center_x, center_y = 350, 300
    
    # Use a fixed spacing between tiles to prevent overlaps
    # Spacing of 16 allows all 1000 squares to fit within screen bounds without clamping
    fixed_spacing = 16  # Consistent spacing between points
    
    # Generate coordinates using a spiral pattern with consistent spacing
    # This will create an outward spiral from the center
    
    def generate_consistent_spiral(max_points):
        # Parameters for the spiral
        x, y = center_x, center_y
        # Start with a small step size
        step_size = fixed_spacing
        
        # Direction vectors for movement (right, down, left, up)
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        direction_index = 0
        
        # How many steps to take in the current direction
        steps_in_direction = 1
        
        # Track steps taken in current direction
        steps_taken = 0
        
        # Whether we need to increase the number of steps after changing direction
        increase_steps = False
        
        spiral_points = []
        spiral_points.append((x, y))  # Start at the center
        
        for _ in range(1, max_points):
            # Calculate next position
            dx, dy = directions[direction_index]
            x += dx * step_size
            y += dy * step_size
            
            # Add point to our list
            spiral_points.append((int(x), int(y)))
            
            # Increment steps taken in current direction
            steps_taken += 1
            
            # Check if we need to change direction
            if steps_taken == steps_in_direction:
                steps_taken = 0
                direction_index = (direction_index + 1) % 4
                
                # Increase steps every second direction change
                if increase_steps:
                    steps_in_direction += 1
                
                increase_steps = not increase_steps
        
        return spiral_points
    
    # Generate a consistent spiral with 1000 points
    coordinates = generate_consistent_spiral(1000)
    
    return coordinates[:1000]  # Return exactly 1000 coordinates
