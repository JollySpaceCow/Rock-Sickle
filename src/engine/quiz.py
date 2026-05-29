import time
from src.core import audio, quiz_tts
from src.core.progress import increment_stat
import src.game.cards as cards

def apply_quiz_effect(player, correct, game_state, scale):
    """Apply effects based on quiz answer correctness."""
    quiz_tts.stop_quiz_tts()
    if correct:
        game_state['message'] = f"Player {player.id + 1} answered correctly!"
        audio.mac_os_dinbg_sound.play()
        increment_stat("quiz_correct")

        player.turn_ended = True
        game_state['quiz_state'] = 'answered'
        game_state['quiz_answer_delay_start'] = time.time()
        if 'quiz_buttons' in game_state:
            del game_state['quiz_buttons']
        
        # Set has_rolled to true to ensure turn ends properly
        player.has_rolled = True
        
        # If this quiz came from a bonus card, make sure the bonus processing is completed
        if game_state.get('processing_bonus_card', False):
            # Mark that a quiz from a bonus card was answered correctly
            game_state['quiz_from_bonus_completed'] = True
    else:
        game_state['message'] = f"Player {player.id + 1} answered wrong. Moving back 2 spaces."
        audio.bing_bong_sound.play()
        
        # Move back 2 spaces (or to the start)
        num_back = 2
        
        # Create movement path
        movement_path = [player.position]
        
        # If position is 2 or greater, go back 2 spaces
        if player.position >= num_back:
            for i in range(1, num_back + 1):
                movement_path.append(player.position - i)
        # Otherwise go back to the start
        else:
            for i in range(1, player.position + 1):
                movement_path.append(player.position - i)
        
        anim = {
            'player': player,
            'path': movement_path,
            'index': 0,
            'last_time': time.time(),
            'message': "Moving back 2 spaces.",
            'is_backwards': True,
            'delay': 0.5
        }
        player.active_animations.append(anim)
        game_state['quiz_state'] = 'answered'
        game_state['quiz_answer_delay_start'] = time.time()
        if 'quiz_buttons' in game_state:
            del game_state['quiz_buttons']
        player.turn_ended = True  # Ensure turn ends even on wrong answer
        
        # If this quiz came from a bonus card, make sure the bonus processing is completed
        if game_state.get('processing_bonus_card', False):
            # Mark that a quiz from a bonus card was answered (incorrectly)
            game_state['quiz_from_bonus_completed'] = True

def trigger_quiz(player, game_state):
    """Draw a quiz card from the appropriate deck and trigger the quiz overlay."""
    quiz_tts.stop_quiz_tts()
    game_state.pop('quiz_tts_started', None)
    message = ""
    # Determine which quiz deck to use based on the board type
    if game_state.get('selected_board') == "Expert" and cards.expert_quiz_card_index < len(cards.expert_quiz_cards):
        # Use expert quiz cards on the expert board
        question, options, correct = cards.expert_quiz_cards[cards.expert_quiz_card_index]
        game_state['quiz_question'] = (question, options, correct)
        game_state['show_quiz'] = True
        game_state['quiz_state'] = 'growing'
        game_state['quiz_start_time'] = time.time()
        game_state['pop_played'] = False
        audio.drum_machine_sound.play()
        cards.expert_quiz_card_index = (cards.expert_quiz_card_index + 1) % len(cards.expert_quiz_cards)
        message = f"Player {player.id + 1} faces an expert quiz."
    elif cards.quiz_card_index < len(cards.quiz_cards):
        # Use regular quiz cards on the classic board
        question, options, correct = cards.quiz_cards[cards.quiz_card_index]
        game_state['quiz_question'] = (question, options, correct)
        game_state['show_quiz'] = True
        game_state['quiz_state'] = 'growing'
        game_state['quiz_start_time'] = time.time()
        game_state['pop_played'] = False
        audio.drum_machine_sound.play()
        cards.quiz_card_index = (cards.quiz_card_index + 1) % len(cards.quiz_cards)
        message = f"Player {player.id + 1} faces a quiz."
    else:
        message = f"Player {player.id + 1} has no quiz cards left."
        
    return message
