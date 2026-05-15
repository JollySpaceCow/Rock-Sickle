# Screen settings
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = 800, 600

# Define some colours for the game
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
PINK = (255, 192, 203)
DULL_PINK = (219, 172, 183)  # A more muted pink for the expert board background
DARK_GREY = (64, 64, 64)
player_colours = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

# Define a small gap between squares (represents 1mm)
GAP_BETWEEN_TILES = 2  # Pixels representing gap between tiles

# Jail positions
CLASSIC_JAIL_POS = (510 + 7*GAP_BETWEEN_TILES, 390 + 5*GAP_BETWEEN_TILES)
EXPERT_JAIL_POS = (563, 440)  
SECRET_JAIL_POS = (700, 50)  

DIE_POS = (300 + 4*GAP_BETWEEN_TILES, 210 + 2*GAP_BETWEEN_TILES)
JAIL_SIZE = 60
