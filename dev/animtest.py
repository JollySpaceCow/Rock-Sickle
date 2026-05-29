import pygame
import time

# Initialise Pygame
pygame.init()

# Original window size
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = 800, 600
screen = pygame.display.set_mode((ORIGINAL_WIDTH, ORIGINAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Card Animation with Sound")
clock = pygame.time.Clock()

# Load images (replace with your file paths)
cover_bonus = pygame.image.load("/Users/harrison/Desktop/Rock_Sickle/Assets/Images/CardCovers/CoverBonus.png")
cover_quiz = pygame.image.load("/Users/harrison/Desktop/Rock_Sickle/Assets/Images/CardCovers/CoverQuiz.png")
content_bonus = pygame.image.load("/Users/harrison/Desktop/Rock_Sickle/Assets/Images/Bonus Card Results/Forward2.png")

# Create a blank white surface for the Quiz card's back
content_quiz = pygame.Surface(cover_quiz.get_size())
content_quiz.fill((255, 255, 255))  # White color

# Load sound effects (replace with your file paths)
pick_up_quiz_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Drum Machine (Pick up Quiz Card).wav')
pick_up_bonus_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Drip Drop (Pick up Bonus Card).wav')
put_away_sound = pygame.mixer.Sound('/Users/harrison/Desktop/Rock_Sickle/Assets/Audio/Disconnect (Put Card Away).wav')

# Define constants with updated initial state
DIE_POS = (254, 177)  # Center reference point (die position)
BONUS_START_POS = (DIE_POS[0] - 120, DIE_POS[1])  # Updated: 120 pixels left of die
QUIZ_START_POS = (DIE_POS[0] + 120, DIE_POS[1])   # Updated: 120 pixels right of die
BONUS_START_ROTATION = 90  # Updated: from -90 to 90 degrees (rotated 180º)
QUIZ_START_ROTATION = -90  # Updated: from 90 to -90 degrees (rotated 180º)
START_SCALE = 0.2  # Initial card size (20% of full size)

# Animation durations (unchanged)
GROWING_DURATION = 2.0
FLIPPING_DURATION = 0.5
SHRINKING_DURATION = 2.0

# Animation state dictionary (unchanged)
anim_state = {
    'active': False,
    'type': None,
    'state': 'growing',
    'start_time': 0,
    'image': None,
    'content_image': None,
    'flipped': False,
    'pos': (0, 0),
    'rotation': 0,
    'scale_factor': START_SCALE,
    'width_scale': 1.0
}

# Helper functions (unchanged)
def get_scaled_pos(pos, scale):
    return (int(pos[0] * scale), int(pos[1] * scale))

def interpolate_position(start, end, t):
    return (start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1]))

def draw_card(screen, img, pos, scale_factor, width_scale, rotation, scale):
    scaled_width = int(img.get_width() * scale_factor * width_scale * scale)
    scaled_height = int(img.get_height() * scale_factor * scale)
    scaled_img = pygame.transform.scale(img, (scaled_width, scaled_height))
    rotated_img = pygame.transform.rotate(scaled_img, rotation)
    rect = rotated_img.get_rect(center=pos)
    screen.blit(rotated_img, rect)

# Main game loop remains unchanged
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if not anim_state['active']:
                if event.key == pygame.K_b:
                    pick_up_bonus_sound.play()
                    anim_state.update({
                        'type': 'bonus',
                        'image': cover_bonus,
                        'content_image': content_bonus,
                        'pos': BONUS_START_POS,
                        'rotation': BONUS_START_ROTATION,
                        'active': True,
                        'start_time': time.time(),
                        'state': 'growing',
                        'scale_factor': START_SCALE,
                        'width_scale': 1.0,
                        'flipped': False
                    })
                elif event.key == pygame.K_q:
                    pick_up_quiz_sound.play()
                    anim_state.update({
                        'type': 'quiz',
                        'image': cover_quiz,
                        'content_image': content_quiz,
                        'pos': QUIZ_START_POS,
                        'rotation': QUIZ_START_ROTATION,
                        'active': True,
                        'start_time': time.time(),
                        'state': 'growing',
                        'scale_factor': START_SCALE,
                        'width_scale': 1.0,
                        'flipped': False
                    })
            elif anim_state['state'] == 'showing':
                if (anim_state['type'] == 'bonus' and event.key == pygame.K_b) or \
                   (anim_state['type'] == 'quiz' and event.key == pygame.K_q):
                    put_away_sound.play()
                    anim_state.update({
                        'state': 'flipping_back',
                        'start_time': time.time(),
                        'flipped': False
                    })

    scale_x = screen.get_width() / ORIGINAL_WIDTH
    scale_y = screen.get_height() / ORIGINAL_HEIGHT
    scale = min(scale_x, scale_y)
    scaled_bonus_start = get_scaled_pos(BONUS_START_POS, scale)
    scaled_quiz_start = get_scaled_pos(QUIZ_START_POS, scale)
    scaled_end_pos = (screen.get_width() // 2, screen.get_height() // 2)

    if anim_state['active']:
        current_time = time.time()
        elapsed = current_time - anim_state['start_time']
        
        if anim_state['state'] == 'growing':
            if elapsed < GROWING_DURATION:
                t = elapsed / GROWING_DURATION
                start_pos = scaled_bonus_start if anim_state['type'] == 'bonus' else scaled_quiz_start
                anim_state['pos'] = interpolate_position(start_pos, scaled_end_pos, t)
                start_rotation = BONUS_START_ROTATION if anim_state['type'] == 'bonus' else QUIZ_START_ROTATION
                anim_state['rotation'] = start_rotation + t * (0 - start_rotation)
                anim_state['scale_factor'] = START_SCALE + t * (1.0 - START_SCALE)
            else:
                anim_state.update({
                    'state': 'flipping',
                    'start_time': current_time,
                    'pos': scaled_end_pos,
                    'rotation': 0,
                    'scale_factor': 1.0
                })
        
        elif anim_state['state'] == 'flipping':
            if elapsed < FLIPPING_DURATION:
                t = elapsed / FLIPPING_DURATION
                if t < 0.5:
                    anim_state['width_scale'] = 1 - 2 * t
                else:
                    anim_state['width_scale'] = 2 * (t - 0.5)
                    if not anim_state['flipped']:
                        anim_state['image'] = anim_state['content_image']
                        anim_state['flipped'] = True
            else:
                anim_state.update({
                    'state': 'showing',
                    'start_time': current_time,
                    'width_scale': 1.0
                })
        
        elif anim_state['state'] == 'showing':
            pass
        
        elif anim_state['state'] == 'flipping_back':
            if elapsed < FLIPPING_DURATION:
                t = elapsed / FLIPPING_DURATION
                if t < 0.5:
                    anim_state['width_scale'] = 1 - 2 * t
                else:
                    anim_state['width_scale'] = 2 * (t - 0.5)
                    if not anim_state['flipped']:
                        anim_state['image'] = cover_bonus if anim_state['type'] == 'bonus' else cover_quiz
                        anim_state['flipped'] = True
            else:
                anim_state.update({
                    'state': 'shrinking',
                    'start_time': current_time,
                    'width_scale': 1.0
                })
        
        elif anim_state['state'] == 'shrinking':
            if elapsed < SHRINKING_DURATION:
                t = elapsed / SHRINKING_DURATION
                end_pos = scaled_bonus_start if anim_state['type'] == 'bonus' else scaled_quiz_start
                anim_state['pos'] = interpolate_position(scaled_end_pos, end_pos, t)
                end_rotation = BONUS_START_ROTATION if anim_state['type'] == 'bonus' else QUIZ_START_ROTATION
                anim_state['rotation'] = 0 + t * (end_rotation - 0)
                anim_state['scale_factor'] = 1.0 + t * (START_SCALE - 1.0)
            else:
                anim_state['active'] = False

    screen.fill((255, 255, 255))
    if anim_state['active']:
        draw_card(screen, anim_state['image'], anim_state['pos'], anim_state['scale_factor'], 
                  anim_state['width_scale'], anim_state['rotation'], scale)
    else:
        draw_card(screen, cover_bonus, scaled_bonus_start, START_SCALE, 1.0, BONUS_START_ROTATION, scale)
        draw_card(screen, cover_quiz, scaled_quiz_start, START_SCALE, 1.0, QUIZ_START_ROTATION, scale)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()