import os
import sys
import logging
import threading
import subprocess
import re
import pygame
from src.core.assets import load_asset

logger = logging.getLogger()

CLASSIC_TTS_DIR = "Assets/Audio/Quiz Announcements/Classic Quiz Questions TTS"
EXPERT_TTS_DIR = "Assets/Audio/Quiz Announcements/Expert Quiz Questions TTS"
CLASSIC_ANSWERS_TTS_DIR = "Assets/Audio/Quiz Announcements/Classic Answers"
EXPERT_ANSWERS_TTS_DIR = "Assets/Audio/Quiz Announcements/Expert Answers"
QUESTION_MARK_FILENAME_TOKEN = "QQQ"

# Game question text -> TTS filename stem when spelling differs
QUESTION_TTS_ALIASES = {
    "What rock contains lead?": "What rock contains led?",
    "What is your favourite flavour of math, true or false?": (
        "What is your favourite flavor of math, true or false?"
    ),
    (
        "Which factor most directly influences the rate of mineral "
        "crystallisation in cooling magma?"
    ): (
        "Which factor most directly influences the rate of mineral "
        "crystallization in cooling magma?"
    ),
}

classic_tts_index = {}
expert_tts_index = {}
classic_answers_tts_index = {}
expert_answers_tts_index = {}
_answer_sound_cache = {}
_answer_channel = None
_answer_queue = []
_answer_source = "rendered"
_say_proc = None
_say_lock = threading.Lock()
_say_generation = 0

_master_volume = 1.0
_playing = False


def _normalize(text):
    normalized = text.strip().lower()
    replacements = {
        "crystallization": "crystallisation",
        "recrystallization": "recrystallisation",
        "color": "colour",
        "flavor": "flavour",
        "vapor": "vapour",
        "luster": "lustre",
    }
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized


def _normalize_audio_key(text):
    return re.sub(r"[^a-z0-9]+", "", _normalize(text))


def _tts_lookup_keys(stem):
    keys = {_normalize(stem)}
    if stem.endswith(QUESTION_MARK_FILENAME_TOKEN):
        keys.add(_normalize(f"{stem[:-len(QUESTION_MARK_FILENAME_TOKEN)]}?"))
    return keys


def _load_tts_index(relative_dir):
    dir_path = load_asset(relative_dir)
    index = {}
    for fname in os.listdir(dir_path):
        if fname.lower().endswith(".mp3"):
            stem = fname[:-4]
            path = os.path.join(dir_path, fname)
            for key in _tts_lookup_keys(stem):
                index[key] = path
    return index


def _answers_stem(options):
    return "".join(f"{index + 1}. {option}" for index, option in enumerate(options))


def _load_answers_tts_index(relative_dir):
    dir_path = load_asset(relative_dir)
    index = {}
    for fname in os.listdir(dir_path):
        if fname.lower().endswith(".mp3"):
            stem = fname[:-4]
            index[_normalize_audio_key(stem)] = os.path.join(dir_path, fname)
    return index


def init_quiz_tts():
    """Load quiz question TTS file paths keyed by normalised question text."""
    global classic_tts_index, expert_tts_index, classic_answers_tts_index
    global expert_answers_tts_index, _answer_channel
    try:
        classic_tts_index = _load_tts_index(CLASSIC_TTS_DIR)
        expert_tts_index = _load_tts_index(EXPERT_TTS_DIR)
        classic_answers_tts_index = _load_answers_tts_index(CLASSIC_ANSWERS_TTS_DIR)
        expert_answers_tts_index = _load_answers_tts_index(EXPERT_ANSWERS_TTS_DIR)
        logger.info(
            "Quiz TTS loaded: %d classic questions, %d expert questions, %d classic answers, %d expert answers",
            len(classic_tts_index),
            len(expert_tts_index),
            len(classic_answers_tts_index),
            len(expert_answers_tts_index),
        )
    except Exception as e:
        logger.error("Error loading quiz TTS: %s", e)
        classic_tts_index = {}
        expert_tts_index = {}
        classic_answers_tts_index = {}
        expert_answers_tts_index = {}

    _answer_channel = pygame.mixer.Channel(7)


def _lookup_path(question, is_expert):
    index = expert_tts_index if is_expert else classic_tts_index
    alias = QUESTION_TTS_ALIASES.get(question)
    key = _normalize(alias if alias else question)
    return index.get(key)


def _answer_mp3_path(answer_item):
    if isinstance(answer_item, tuple):
        options, is_expert = answer_item
        index = expert_answers_tts_index if is_expert else classic_answers_tts_index
        return index.get(_normalize_audio_key(_answers_stem(options)))
    return None


def _get_answer_sound(answer_item):
    cache_key = repr(answer_item)
    if cache_key in _answer_sound_cache:
        return _answer_sound_cache[cache_key]
    path = _answer_mp3_path(answer_item)
    if not path:
        return None
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(_master_volume)
        _answer_sound_cache[cache_key] = sound
        return sound
    except Exception as e:
        logger.error("Failed to load answer TTS %s: %s", path, e)
        return None


def _stop_say():
    global _say_proc, _say_generation
    with _say_lock:
        _say_generation += 1
        if _say_proc is not None and _say_proc.poll() is None:
            proc = _say_proc
            proc.terminate()
            try:
                proc.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                proc.kill()
        _say_proc = None


def stop_answer_tts():
    """Stop answer narration only, leaving question playback untouched."""
    global _answer_queue
    _answer_queue = []
    if _answer_channel and _answer_channel.get_busy():
        _answer_channel.stop()
    _stop_say()


def _speak_device(text):
    """Speak quiz narration via the device TTS voice."""
    if sys.platform != "darwin":
        logger.warning("Device TTS is only available on macOS.")
        return

    with _say_lock:
        scheduled_generation = _say_generation

    def run():
        global _say_proc
        with _say_lock:
            if scheduled_generation != _say_generation:
                return
            if _say_proc is not None and _say_proc.poll() is None:
                _say_proc.terminate()
            try:
                proc = subprocess.Popen(["say", text])
                _say_proc = proc
            except Exception as e:
                logger.error("Failed to speak quiz narration: %s", e)
                return
        proc.wait()

    threading.Thread(target=run, daemon=True).start()


def speak_device_announcement(text):
    """Speak settings announcements via the device TTS voice."""
    _speak_device(text)


def _say_busy():
    with _say_lock:
        return _say_proc is not None and _say_proc.poll() is None


def set_volume(volume):
    """Apply master volume to quiz TTS playback."""
    global _master_volume
    _master_volume = volume
    if _playing:
        pygame.mixer.music.set_volume(volume)
    for sound in _answer_sound_cache.values():
        sound.set_volume(volume)


def set_answer_source(use_device_tts):
    """Select whether quiz narration uses device speech or rendered clips."""
    global _answer_source
    _answer_source = "device" if use_device_tts else "rendered"


def stop_question_tts():
    """Stop question narration only."""
    global _playing
    if _playing or pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    if _answer_source == "device":
        _stop_say()
    _playing = False


def stop_quiz_tts():
    """Stop any quiz question or answer narration currently playing."""
    stop_question_tts()
    stop_answer_tts()


def is_quiz_tts_busy():
    """Return True while quiz question or answer narration is active or queued."""
    global _playing
    music_busy = pygame.mixer.music.get_busy()
    if _playing and not music_busy:
        _playing = False
    question_busy = _playing or music_busy
    answer_busy = bool(_answer_queue)
    answer_busy = answer_busy or bool(_answer_channel and _answer_channel.get_busy())
    return question_busy or answer_busy or _say_busy()


def queue_answers(options, is_expert=False):
    """Queue answer options to speak after the question narration finishes."""
    global _answer_queue
    if _answer_source == "device":
        _answer_queue = list(options)
    else:
        _answer_queue = [(list(options), is_expert)]


def tick_answers():
    """Advance the answer narration queue (call once per frame during a quiz)."""
    if not _answer_queue:
        return
    if pygame.mixer.music.get_busy():
        return
    if _answer_channel and _answer_channel.get_busy():
        return
    if _say_busy():
        return

    answer_item = _answer_queue.pop(0)
    sound = _get_answer_sound(answer_item)
    if sound and _answer_channel:
        _answer_channel.play(sound)
    elif isinstance(answer_item, str) and sys.platform == "darwin":
        _speak_device(answer_item)
    elif isinstance(answer_item, tuple):
        logger.warning("No rendered answer TTS found for: %s", _answers_stem(answer_item[0]))


def play_quiz_tts(question, is_expert=False):
    """Play narration for the given quiz question, if a matching file exists."""
    global _playing
    stop_question_tts()

    if _answer_source == "device":
        _speak_device(question)
        return

    path = _lookup_path(question, is_expert)
    if not path:
        logger.warning("No quiz TTS found for: %s", question)
        return

    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(_master_volume)
        pygame.mixer.music.play()
        _playing = True
    except Exception as e:
        logger.error("Failed to play quiz TTS %s: %s", path, e)
        _playing = False
