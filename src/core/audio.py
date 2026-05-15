import pygame
from src.core.assets import load_asset
import logging

logger = logging.getLogger()

# Audio variables
pong_sound = None
voltage_easy_sound = None
voltage_normal_sound = None
voltage_hard_sound = None
whit_sound = None
connect_sound = None
super_mario_sound = None
roll_sound = None
glug_sound = None
bonk_sound = None
head_shake_sound = None
whiz_sound = None
drip_drop_sound = None
drum_machine_sound = None
win_sound = None
pop_sound = None
bing_bong_sound = None
disconnect_sound = None
indigogo_sound = None
jump_sound = None
mac_os_dinbg_sound = None
mac_os_uh_ohh_sound = None
wobble_sound = None
fairlin_round1_sound = None
restart_sound = None
car_horn_sound = None
bonk_cpu_sound = None
glug_cpu_sound = None
head_shake_cpu_sound = None
jump_cpu_sound = None
whiz_cpu_sound = None
wobble_cpu_sound = None

def init_audio():
    """Initialize and load all audio assets."""
    global pong_sound, voltage_easy_sound, voltage_normal_sound, voltage_hard_sound
    global whit_sound, connect_sound, super_mario_sound, roll_sound, glug_sound
    global bonk_sound, head_shake_sound, whiz_sound, drip_drop_sound, drum_machine_sound
    global win_sound, pop_sound, bing_bong_sound, disconnect_sound, indigogo_sound
    global jump_sound, mac_os_dinbg_sound, mac_os_uh_ohh_sound, wobble_sound
    global fairlin_round1_sound, restart_sound, car_horn_sound
    global bonk_cpu_sound, glug_cpu_sound, head_shake_cpu_sound, jump_cpu_sound, whiz_cpu_sound, wobble_cpu_sound

    try:
        # Menus
        pong_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Pong (Player Not Set).wav"))
        voltage_easy_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Voltage (Easy CPU Player Selected).wav"))
        voltage_normal_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Voltage2 (Normal CPU Player Selected).wav"))
        voltage_hard_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Voltage3 (Hard CPU Player Selected).wav"))
        whit_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Whit (Player Set).wav"))
        connect_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Connect.wav"))
        super_mario_sound = pygame.mixer.Sound(load_asset("Assets/Audio/super_mario_64_soundtrack_correct_solution (Amount of Players has been Chosen).wav"))
        
        # Gameplay
        roll_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Drum Roll (Roll the Dice).wav"))
        glug_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Glug (Moving).wav"))
        bonk_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Bonk (Stay In Jail).wav"))
        head_shake_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Head Shake (Exit Jail).wav"))
        whiz_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Whiz2 (Moving to Jail).wav"))
        drip_drop_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Drip Drop (Pick up Bonus Card).wav"))
        drum_machine_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Drum Machine (Pick up Quiz Card).wav"))
        win_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Odesong (Win).wav"))
        pop_sound = pygame.mixer.Sound(load_asset("Assets/Audio/pop (Anser Buttons Appear).wav"))
        bing_bong_sound = pygame.mixer.Sound(load_asset("Assets/Audio/bing_bong (Incorrect Quiz Answer).wav"))
        disconnect_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Disconnect (Put Card Away).wav"))
        indigogo_sound = pygame.mixer.Sound(load_asset("Assets/Audio/indigogo (Path Chosen).wav"))
        jump_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Jump (Forward a Space).wav"))
        mac_os_dinbg_sound = pygame.mixer.Sound(load_asset("Assets/Audio/mac_os_dinbg (Quiz Answer Correct).wav"))
        mac_os_uh_ohh_sound = pygame.mixer.Sound(load_asset("Assets/Audio/mac_os_uh_ohh (Sent to Jail by Bonus Card).wav"))
        wobble_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Wobble (Back a Space).wav"))
        fairlin_round1_sound = pygame.mixer.Sound(load_asset("Assets/Audio/SE1_EVT_FAIRLIN_ROUND1 (Win).wav"))
        restart_sound = pygame.mixer.Sound(load_asset("Assets/Audio/SE4_F_MAWASU_ROUND1.wav"))
        
        # New sound effects
        car_horn_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Car Horn.wav"))
        
        # CPU player sound variations
        bonk_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/BonkCPU.wav"))
        glug_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/GlugCPU.wav"))
        head_shake_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Head ShakeCPU.wav"))
        jump_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/JumpCPU.wav"))
        whiz_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/WhizCPU.wav"))
        wobble_cpu_sound = pygame.mixer.Sound(load_asset("Assets/Audio/WobbleCPU.wav"))
        
        logger.info("Audio assets loaded successfully")
    except Exception as e:
        logger.error(f"Error loading audio assets: {e}")
        import traceback, sys
        traceback.print_exc(file=sys.stderr)

def apply_master_volume(volume):
    """Update all sound volumes based on the master volume setting (0.0 to 1.0)."""
    sounds = [
        roll_sound, glug_sound, bonk_sound, head_shake_sound, whiz_sound,
        drip_drop_sound, drum_machine_sound, win_sound, pop_sound,
        bing_bong_sound, connect_sound, disconnect_sound, indigogo_sound,
        jump_sound, mac_os_dinbg_sound, mac_os_uh_ohh_sound, super_mario_sound,
        wobble_sound, fairlin_round1_sound, pong_sound, voltage_easy_sound,
        voltage_normal_sound, voltage_hard_sound, whit_sound, restart_sound,
        car_horn_sound, bonk_cpu_sound, glug_cpu_sound, head_shake_cpu_sound,
        jump_cpu_sound, whiz_cpu_sound, wobble_cpu_sound
    ]
    for sound in sounds:
        if sound is not None:
            sound.set_volume(volume)
