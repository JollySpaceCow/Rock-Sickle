from src.core import audio

def toggle_player_state(index, player_states, difficulties):
    """Toggle a player's state between not set, human, or CPU."""
    player_states[index] = (player_states[index] + 1) % 3
    if player_states[index] == 0:
        audio.pong_sound.play()
        difficulties[index] = None
    elif player_states[index] == 1:
        audio.whit_sound.play()
        difficulties[index] = None
    elif player_states[index] == 2:
        difficulties[index] = 'normal'
        audio.voltage_normal_sound.play()

def cycle_difficulty(index, difficulties):
    """Cycle through CPU difficulty levels."""
    if difficulties[index] == 'easy':
        difficulties[index] = 'normal'
        audio.voltage_normal_sound.play()
    elif difficulties[index] == 'normal':
        difficulties[index] = 'hard'
        audio.voltage_hard_sound.play()
    elif difficulties[index] == 'hard':
        difficulties[index] = 'easy'
        audio.voltage_easy_sound.play()
