import os
import sys
import logging
import pygame
from src.constants import GAP_BETWEEN_TILES

logger = logging.getLogger()

# Work out the base path for assets
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def load_asset(relative_path):
    """Load an asset from the given relative path."""
    full_path = os.path.join(base_path, relative_path)
    if not os.path.exists(full_path):
        logger.error(f"Asset not found: {full_path}")
        raise FileNotFoundError(f"Asset not found: {full_path}")
    return full_path

class AssetRegistry:
    """Centralised registry for original and scaled game assets."""
    # Original assets loaded from disk
    tile_images_original = {}
    expert_tile_images_original = {}
    board_tile_images = {}
    board_buttons = {}
    player_images_original = []
    cpu_image_original = None
    dice_images_original = []
    difficulty_images_original = {}
    cpu_difficulty_images_original = {}
    bonus_result_images_original = {}
    cover_bonus_original = None
    cover_quiz_original = None
    
    # Scaled assets (re-scaled on screen resize or board selection)
    player_images_scaled = []
    cpu_image_scaled = None
    cpu_difficulty_images_scaled = {}
    dice_images_scaled = []
    tile_images_scaled = {}
    restart_button_scaled = None
    settings_button_scaled = None
    achievement_button_scaled = None
    magnify_button_scaled = None
    bonus_result_images_scaled = {}
    cover_bonus_scaled = None
    cover_quiz_scaled = None
    
    # Camera asset cache to speed up dynamic zoom calculations
    camera_asset_cache = {
        'zoom': 1.0,
        'scale': 1.0,
        'board_type': None,
        'tiles': {},
        'players': [],
        'cpu': {},
        'dice': []
    }

def load_and_convert(path):
    """Load an image and convert it to 32-bit RGBA format for proper scaling."""
    img = pygame.image.load(load_asset(path))
    return img.convert_alpha()

def initialise_all_assets():
    """Initialise and load all original game assets into the AssetRegistry.
    
    Should be called inside main() after the display mode has been set.
    """
    logger.info("Starting asset loading and registration")
    try:
        # Load classic tile images - convert all to 32-bit RGBA format
        forward_one_original = load_and_convert("Assets/Images/Tiles/Forward One.png")
        back_two_original = load_and_convert("Assets/Images/Tiles/Back Two.png")
        restart_button_original = load_and_convert("Assets/Images/Tiles/Restart.png")
        settings_button_original = load_and_convert("Assets/Images/Tiles/Mr Geary.png")
        achievement_button_original = load_and_convert("Assets/Images/Tiles/Target.png")
        e_achievement_button_original = load_and_convert("Assets/Images/Tiles/eTarget.png")
        
        AssetRegistry.tile_images_original = {
            'Go': load_and_convert("Assets/Images/Tiles/Go.png"),
            '1_East': forward_one_original,
            '1_South': pygame.transform.rotate(forward_one_original, 90),
            '1_West': pygame.transform.rotate(forward_one_original, 180),
            '1_North': pygame.transform.rotate(forward_one_original, 270),
            '-2_East': pygame.transform.rotate(back_two_original, 180),
            '-2_South': pygame.transform.rotate(back_two_original, 270),
            '-2_West': back_two_original,
            '-2_North': pygame.transform.rotate(back_two_original, 90),
            'B': load_and_convert("Assets/Images/Tiles/Bonus.png"),
            'Q': load_and_convert("Assets/Images/Tiles/Quiz.png"),
            'J': load_and_convert("Assets/Images/Tiles/Go To Jail.png"),
            '0': load_and_convert("Assets/Images/Tiles/Safe Space.png"),
            'P': load_and_convert("Assets/Images/Tiles/Choose Your Path.png"),
            'F': load_and_convert("Assets/Images/Tiles/Finish.png"),
            'Jail': load_and_convert("Assets/Images/Tiles/Jail Location.png"),
        }
        
        e_forward_one_original = load_and_convert("Assets/Images/Tiles/eForward One.png")
        e_back_two_original = load_and_convert("Assets/Images/Tiles/eBack Two.png")
        e_restart_button_original = load_and_convert("Assets/Images/Tiles/eRestart.png")
        e_settings_button_original = load_and_convert("Assets/Images/Tiles/eMr Geary.png")
        
        AssetRegistry.expert_tile_images_original = {
            'Go': load_and_convert("Assets/Images/Tiles/Go.png"),  # Reusing Go tile for expert
            '1_East': e_forward_one_original,
            '1_South': pygame.transform.rotate(e_forward_one_original, 90),
            '1_West': pygame.transform.rotate(e_forward_one_original, 180),
            '1_North': pygame.transform.rotate(e_forward_one_original, 270),
            '-2_East': pygame.transform.rotate(e_back_two_original, 180),
            '-2_South': pygame.transform.rotate(e_back_two_original, 270),
            '-2_West': e_back_two_original,
            '-2_North': pygame.transform.rotate(e_back_two_original, 90),
            'B': load_and_convert("Assets/Images/Tiles/eBonus.png"),
            'Q': load_and_convert("Assets/Images/Tiles/eQuiz.png"),
            'J': load_and_convert("Assets/Images/Tiles/eGo To Jail.png"),
            '0': load_and_convert("Assets/Images/Tiles/eSafe Space.png"),
            'P': load_and_convert("Assets/Images/Tiles/eChoose Your Path.png"),
            'F': load_and_convert("Assets/Images/Tiles/eFin.png"),
            'Jail': load_and_convert("Assets/Images/Tiles/eJail Location.png"),
            'FP': load_and_convert("Assets/Images/Tiles/Free Parking.png"),
        }
        
        # Store both sets
        AssetRegistry.board_tile_images = {
            'Classic': AssetRegistry.tile_images_original,
            'Expert': AssetRegistry.expert_tile_images_original,
            'Secret': AssetRegistry.tile_images_original  # Reuse Classic tiles for Secret board
        }
        
        AssetRegistry.board_buttons = {
            'Classic': {
                'restart': restart_button_original,
                'settings': settings_button_original,
                'achievement': achievement_button_original
            },
            'Expert': {
                'restart': e_restart_button_original,
                'settings': e_settings_button_original,
                'achievement': e_achievement_button_original
            },
            'Secret': {
                'restart': restart_button_original,
                'settings': settings_button_original,
                'achievement': achievement_button_original
            }
        }
        
        logger.info("Classic and expert tile images loaded successfully")
        
        player_image_paths = [
            "Assets/Images/Players/Player Red.png",
            "Assets/Images/Players/Player Orange.png",
            "Assets/Images/Players/Player Yellow.png",
            "Assets/Images/Players/Player Green.png",
            "Assets/Images/Players/Player Blue.png",
            "Assets/Images/Players/Player Purple.png",
        ]
        AssetRegistry.player_images_original = [load_and_convert(img) for img in player_image_paths]
        logger.info("Original player images loaded successfully")
        
        AssetRegistry.cpu_image_original = load_and_convert("Assets/Images/Players/Player CPU.png")
        logger.info("Original CPU image loaded successfully")
        
        AssetRegistry.dice_images_original = [
            load_and_convert(f"Assets/Images/Dices/{i}.png") for i in range(1, 7)
        ]
        logger.info("Original dice images loaded successfully")
        
        AssetRegistry.difficulty_images_original = {
            'easy': load_and_convert("Assets/Images/DifficultyButtons/1Baby.png"),
            'normal': load_and_convert("Assets/Images/DifficultyButtons/3Consentrated.png"),
            'hard': load_and_convert("Assets/Images/DifficultyButtons/4Angery.png"),
        }
        logger.info("Original difficulty images loaded successfully")
        
        # Load CPU difficulty images
        AssetRegistry.cpu_difficulty_images_original = {
            'easy': load_and_convert("Assets/Images/Players/CPUEasy.png"),
            'normal': load_and_convert("Assets/Images/Players/CPUNormal.png"),
            'hard': load_and_convert("Assets/Images/Players/CPUHard.png"),
        }
        logger.info("CPU difficulty images loaded successfully")
        
        # Load bonus result images as 32-bit surfaces with per-pixel alpha
        bonus_result_paths = {
            'back1': "Assets/Images/Bonus Card Results/Back1.png",
            'back1alt': "Assets/Images/Bonus Card Results/Back1Alt.png",
            'back3': "Assets/Images/Bonus Card Results/Back3.png",
            'back5': "Assets/Images/Bonus Card Results/Back5.png",
            'forward2': "Assets/Images/Bonus Card Results/Forward2.png",
            'forward3': "Assets/Images/Bonus Card Results/Forward3.png",
            'forward3alt': "Assets/Images/Bonus Card Results/Forward3Alt.png",
            'forward4': "Assets/Images/Bonus Card Results/Forward4.png",
            'jail1': "Assets/Images/Bonus Card Results/Go To Jail 1.png",
            'jail2': "Assets/Images/Bonus Card Results/Go To Jail 2.png",
            'jail3': "Assets/Images/Bonus Card Results/Go To Jail 3.png",
            'jail4': "Assets/Images/Bonus Card Results/Go To Jail 4.png",
            'pickquiz': "Assets/Images/Bonus Card Results/PickQuizCard.png",
            'pickquizalt': "Assets/Images/Bonus Card Results/PickQuizCardAlt.png",
            'pickquizaltalt': "Assets/Images/Bonus Card Results/PickQuizCardAltAlt.png",
            # Expert bonus card images
            'expert_back2_1': "Assets/Images/Bonus Card Results Expert/Back2.png",
            'expert_back2_2': "Assets/Images/Bonus Card Results Expert/Back2Alt.png",
            'expert_back5_1': "Assets/Images/Bonus Card Results Expert/Back5.png",
            'expert_back5_2': "Assets/Images/Bonus Card Results Expert/Back5Alt.png",
            'expert_forward2_1': "Assets/Images/Bonus Card Results Expert/Forward2 1.png",
            'expert_forward2_2': "Assets/Images/Bonus Card Results Expert/Forward2 2.png",
            'expert_forward2_3': "Assets/Images/Bonus Card Results Expert/Forward2 3.png",
            'expert_forward2_4': "Assets/Images/Bonus Card Results Expert/Forward2 4.png",
            'expert_forward2_5': "Assets/Images/Bonus Card Results Expert/Forward2 5.png",
            'expert_forward2_6': "Assets/Images/Bonus Card Results Expert/Forward2 6.png",
            'expert_forward5': "Assets/Images/Bonus Card Results Expert/Forward5.png",
            'expert_jail1': "Assets/Images/Bonus Card Results Expert/Go To Jail 1.png",
            'expert_jail2': "Assets/Images/Bonus Card Results Expert/Go To Jail 2.png",
            'expert_jail3': "Assets/Images/Bonus Card Results Expert/Go To Jail 3.png",
            'expert_jail4': "Assets/Images/Bonus Card Results Expert/Go To Jail 4.png",
            'expert_jail_free': "Assets/Images/Bonus Card Results Expert/Jail Free.png",
            'expert_jail_free_micro': "Assets/Images/Bonus Card Results Expert/Jail Free Micro.png",
        }
        AssetRegistry.bonus_result_images_original = {}
        for key, path in bonus_result_paths.items():
            AssetRegistry.bonus_result_images_original[key] = load_and_convert(path)
            
        # Load card covers for flipping animation
        AssetRegistry.cover_bonus_original = load_and_convert("Assets/Images/CardCovers/CoverBonus.png")
        AssetRegistry.cover_quiz_original = load_and_convert("Assets/Images/CardCovers/CoverQuiz.png")
        
        logger.info("All graphics assets loaded and registered successfully")
    except Exception as e:
        logger.error(f"Error loading original assets: {e}", exc_info=True)
        raise e
