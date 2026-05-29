class GameState(dict):
    """Subclass of dict representing the central game state.
    
    Provides dictionary-style access with default initialisation values
    for layout and camera states, maintaining backwards compatibility
    during modularisation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamic layout parameters
        self.setdefault('scale', 1.0)
        self.setdefault('offset_x', 0)
        self.setdefault('offset_y', 0)
        self.setdefault('screen_width', 800)
        self.setdefault('screen_height', 600)
        
        # Camera states
        self.setdefault('camera_zoom', 1.0)
        self.setdefault('camera_focus_x', 400.0)
        self.setdefault('camera_focus_y', 300.0)
        self.setdefault('camera_mode', 0)
        self.setdefault('camera_target_zoom', 1.0)
        self.setdefault('camera_target_focus_x', 400.0)
        self.setdefault('camera_target_focus_y', 300.0)
        
        # Game loop control
        self.setdefault('running', True)
        self.setdefault('selected_board', 'Classic')
