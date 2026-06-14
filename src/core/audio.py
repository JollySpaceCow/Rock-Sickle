import pygame
from src.core.assets import load_asset
import logging

logger = logging.getLogger()

SOUND_EFFECTS_DIR = "Assets/Audio/Sound Effects"

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
finished_sound = None
woosh_sound = None
car_horn_sound = None
bonk_cpu_sound = None
glug_cpu_sound = None
head_shake_cpu_sound = None
jump_cpu_sound = None
whiz_cpu_sound = None
wobble_cpu_sound = None
doubles_sound = None
info_sound = None
speak_quiz_questions_sound = None
speak_quiz_answers_sound = None
device_tts_off_sound = None
explosion_sound = None

def init_audio():
    """Initialize and load all audio assets."""
    global pong_sound, voltage_easy_sound, voltage_normal_sound, voltage_hard_sound
    global whit_sound, connect_sound, super_mario_sound, roll_sound, glug_sound
    global bonk_sound, head_shake_sound, whiz_sound, drip_drop_sound, drum_machine_sound
    global win_sound, pop_sound, bing_bong_sound, disconnect_sound, indigogo_sound
    global jump_sound, mac_os_dinbg_sound, mac_os_uh_ohh_sound, wobble_sound
    global fairlin_round1_sound, restart_sound, finished_sound, woosh_sound, car_horn_sound
    global bonk_cpu_sound, glug_cpu_sound, head_shake_cpu_sound, jump_cpu_sound, whiz_cpu_sound, wobble_cpu_sound, doubles_sound, info_sound
    global speak_quiz_questions_sound, speak_quiz_answers_sound, device_tts_off_sound
    global explosion_sound

    try:
        # Menus
        pong_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Pong (Player Not Set).wav"))
        voltage_easy_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Voltage (Easy CPU Player Selected).wav"))
        voltage_normal_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Voltage2 (Normal CPU Player Selected).wav"))
        voltage_hard_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Voltage3 (Hard CPU Player Selected).wav"))
        whit_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Whit (Player Set).wav"))
        connect_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Connect.wav"))
        super_mario_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/super_mario_64_soundtrack_correct_solution (Amount of Players has been Chosen).wav"))
        
        # Gameplay
        roll_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Drum Roll (Roll the Dice).wav"))
        glug_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Glug (Moving).wav"))
        bonk_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Bonk (Stay In Jail).wav"))
        head_shake_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Head Shake (Exit Jail).wav"))
        whiz_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Whiz2 (Moving to Jail).wav"))
        drip_drop_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Drip Drop (Pick up Bonus Card).wav"))
        drum_machine_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Drum Machine (Pick up Quiz Card).wav"))
        win_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Odesong (Win).wav"))
        pop_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/pop (Anser Buttons Appear).wav"))
        bing_bong_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/bing_bong (Incorrect Quiz Answer).wav"))
        disconnect_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Disconnect (Put Card Away).wav"))
        indigogo_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/indigogo (Path Chosen).wav"))
        jump_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Jump (Forward a Space).wav"))
        mac_os_dinbg_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/mac_os_dinbg (Quiz Answer Correct).wav"))
        mac_os_uh_ohh_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/mac_os_uh_ohh (Sent to Jail by Bonus Card).wav"))
        wobble_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Wobble (Back a Space).wav"))
        fairlin_round1_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/SE1_EVT_FAIRLIN_ROUND1 (Win).wav"))
        restart_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/SE4_F_MAWASU_ROUND1.wav"))
        finished_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Finished.mp3"))
        woosh_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Woosh.mp3"))
        doubles_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Doubles.mp3"))
        
        # New sound effects
        car_horn_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Car Horn.wav"))
        
        # CPU player sound variations
        bonk_cpu_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/BonkCPU.wav"))
        glug_cpu_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/GlugCPU.wav"))
        head_shake_cpu_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Head ShakeCPU.wav"))
        jump_cpu_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/JumpCPU.wav"))
        whiz_cpu_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/WhizCPU.wav"))
        wobble_cpu_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/WobbleCPU.wav"))
        
        # Test sound for volume adjustment
        info_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Info.wav"))
        
        # Get Out of Jail Free card explosion sound
        explosion_sound = pygame.mixer.Sound(load_asset(f"{SOUND_EFFECTS_DIR}/Breaking_Explosion_SeResourceStd2nd_00000541.wav"))
        
        # Settings toggle feedback sounds
        speak_quiz_questions_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Quiz Announcements/Speak quiz questions.mp3"))
        speak_quiz_answers_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Quiz Announcements/Speak quiz answers.mp3"))
        device_tts_off_sound = pygame.mixer.Sound(load_asset("Assets/Audio/Quiz Announcements/Device Text To Speech Off.mp3"))
        
        logger.info("Audio assets loaded successfully")
    except Exception as e:
        logger.error(f"Error loading audio assets: {e}")
        import traceback, sys
        traceback.print_exc(file=sys.stderr)

def apply_master_volume(volume):
    """Update all sound volumes based on the master volume setting (0.0 to 1.0)."""
    from src.core import quiz_tts
    quiz_tts.set_volume(volume)
    sounds = [
        roll_sound, glug_sound, bonk_sound, head_shake_sound, whiz_sound,
        drip_drop_sound, drum_machine_sound, win_sound, pop_sound,
        bing_bong_sound, connect_sound, disconnect_sound, indigogo_sound,
        jump_sound, mac_os_dinbg_sound, mac_os_uh_ohh_sound, super_mario_sound,
        wobble_sound, fairlin_round1_sound, pong_sound, voltage_easy_sound,
        voltage_normal_sound, voltage_hard_sound, whit_sound, restart_sound, finished_sound, woosh_sound,
        car_horn_sound, bonk_cpu_sound, glug_cpu_sound, head_shake_cpu_sound,
        jump_cpu_sound, whiz_cpu_sound, wobble_cpu_sound, doubles_sound, info_sound,
        speak_quiz_questions_sound, speak_quiz_answers_sound, device_tts_off_sound,
        explosion_sound
    ]
    for sound in sounds:
        if sound is not None:
            sound.set_volume(volume)
