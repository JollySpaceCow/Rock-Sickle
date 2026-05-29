class Player:
    """Class to represent a player in the game."""
    def __init__(self, id, colour_index, is_computer=False, difficulty=None, start_coords=(0,0)):
        self.id = id
        self.colour_index = colour_index
        self.is_computer = is_computer
        self.difficulty = difficulty
        self.position = 0
        self.in_jail = False
        self.finished = False
        self.finish_order = None
        self.has_rolled = False
        self.prev_position = 0
        
        # Initialize player position based on the coordinates of GO square (position 0)
        # Add centering adjustment to ensure player is in the center of the GO tile
        self.current_x = start_coords[0]
        self.current_y = start_coords[1]
        
        self.turn_ended = False
        self.position_history = []
        self.active_animations = []
        self.path_choices = {}  # Store path choices for each choice point
        self.jail_x, self.jail_y = None, None  # Store player-specific jail position
        self.quiz_cards = 3
        # Add these new attributes for jail standee markers
        self.jail_from_x = None  # X-coordinate of the position before jail
        self.jail_from_y = None  # Y-coordinate of the position before jail
        self.jail_marker_anim_start = None  # Time when the standee animation begins
        # Add player timer attributes
        self.start_time = None  # Time when player starts the game
        self.finish_time = None  # Time when player finishes the game
        self.elapsed_time = None  # Total time taken to finish the game
        # Add victory cutscene attributes
        self.victory_x = None
        self.victory_y = None  # Final Y position in victory formation
        self.victory_scale_factor = 1.0  # Scale factor for victory pose
        
        # Add jail free card flag
        self.has_jail_free_card = False
        self.jail_free_card_visible = False
