import os
import sys
import logging
import threading
import subprocess
import pygame
from src.core.assets import load_asset

logger = logging.getLogger()

CLASSIC_TTS_DIR = "Assets/Classic Quiz Questions TTS"
EXPERT_TTS_DIR = "Assets/Expert Quiz Questions TTS"
ANSWERS_TTS_DIR = "Assets/Quiz Answers TTS"

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
_answers_tts_dir = None
_answer_sound_cache = {}
_answer_channel = None
_answer_queue = []
_say_proc = None
_say_lock = threading.Lock()

_master_volume = 1.0
_playing = False


def _normalize(text):
    return text.strip().lower()


def _load_tts_index(relative_dir):
    dir_path = load_asset(relative_dir)
    index = {}
    for fname in os.listdir(dir_path):
        if fname.lower().endswith(".mp3"):
            stem = fname[:-4]
            index[_normalize(stem)] = os.path.join(dir_path, fname)
    return index


def init_quiz_tts():
    """Load quiz question TTS file paths keyed by normalised question text."""
    global classic_tts_index, expert_tts_index, _answers_tts_dir, _answer_channel
    try:
        classic_tts_index = _load_tts_index(CLASSIC_TTS_DIR)
        expert_tts_index = _load_tts_index(EXPERT_TTS_DIR)
        logger.info(
            "Quiz TTS loaded: %d classic, %d expert",
            len(classic_tts_index),
            len(expert_tts_index),
        )
    except Exception as e:
        logger.error("Error loading quiz TTS: %s", e)
        classic_tts_index = {}
        expert_tts_index = {}

    try:
        _answers_tts_dir = load_asset(ANSWERS_TTS_DIR)
        logger.info("Quiz answer TTS directory found: %s", _answers_tts_dir)
    except FileNotFoundError:
        _answers_tts_dir = None

    _answer_channel = pygame.mixer.Channel(7)


def _lookup_path(question, is_expert):
    index = expert_tts_index if is_expert else classic_tts_index
    alias = QUESTION_TTS_ALIASES.get(question)
    key = _normalize(alias if alias else question)
    return index.get(key)


def _answer_mp3_path(answer_text):
    if not _answers_tts_dir:
        return None
    path = os.path.join(_answers_tts_dir, f"{answer_text}.mp3")
    return path if os.path.isfile(path) else None


def _get_answer_sound(answer_text):
    if answer_text in _answer_sound_cache:
        return _answer_sound_cache[answer_text]
    path = _answer_mp3_path(answer_text)
    if not path:
        return None
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(_master_volume)
        _answer_sound_cache[answer_text] = sound
        return sound
    except Exception as e:
        logger.error("Failed to load answer TTS %s: %s", path, e)
        return None


def _stop_say():
    global _say_proc
    with _say_lock:
        if _say_proc is not None and _say_proc.poll() is None:
            _say_proc.terminate()
        _say_proc = None


def stop_answer_tts():
    """Stop answer narration only, leaving question playback untouched."""
    global _answer_queue
    _answer_queue = []
    if _answer_channel and _answer_channel.get_busy():
        _answer_channel.stop()
    _stop_say()


def _speak_fallback(answer_text):
    """Speak answer text via macOS say when no recorded MP3 exists."""
    if sys.platform != "darwin":
        return

    def run():
        global _say_proc
        with _say_lock:
            if _say_proc is not None and _say_proc.poll() is None:
                _say_proc.terminate()
            try:
                proc = subprocess.Popen(["say", answer_text])
                _say_proc = proc
            except Exception as e:
                logger.error("Failed to speak answer: %s", e)
                return
        proc.wait()

    threading.Thread(target=run, daemon=True).start()


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


def stop_question_tts():
    """Stop question narration only."""
    global _playing
    if _playing or pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    _playing = False


def stop_quiz_tts():
    """Stop any quiz question or answer narration currently playing."""
    stop_question_tts()
    stop_answer_tts()


def queue_answers(options):
    """Queue answer options to speak after the question narration finishes."""
    global _answer_queue
    _answer_queue = list(options)


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

    answer_text = _answer_queue.pop(0)
    sound = _get_answer_sound(answer_text)
    if sound and _answer_channel:
        _answer_channel.play(sound)
    elif _answers_tts_dir or sys.platform == "darwin":
        _speak_fallback(answer_text)


def play_quiz_tts(question, is_expert=False):
    """Play narration for the given quiz question, if a matching file exists."""
    global _playing
    path = _lookup_path(question, is_expert)
    if not path:
        logger.warning("No quiz TTS found for: %s", question)
        return

    stop_question_tts()
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(_master_volume)
        pygame.mixer.music.play()
        _playing = True
    except Exception as e:
        logger.error("Failed to play quiz TTS %s: %s", path, e)
        _playing = False
