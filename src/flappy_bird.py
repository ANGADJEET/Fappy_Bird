import pygame
import cv2
import numpy as np
import mediapipe as mp

# Define game constants
width, height = 600, 800
bird_speed = 5
gravity = 0.5
jump_force = -10  # Adjust as needed
pipe_width = 50
pipe_gap = 200
pipe_interval = 200
pipes = []

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flappy Bird (Gesture Control)")
clock = pygame.time.Clock()

# Initialize Mediapipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Initialize OpenCV webcam capture
cap = cv2.VideoCapture(0)

class Bird:
    def __init__(self, y):
        self.y = y

    def jump(self):
        global bird_speed
        bird_speed = jump_force

def draw_game(screen, bird, pipes):
    # Display background, bird, and pipes
    screen.fill((0, 0, 0))  # Clear the screen
    pygame.draw.circle(screen, (255, 255, 255), (50, bird.y), 20)  # Draw bird
    # Draw pipes
    for pipe in pipes:
        pygame.draw.rect(screen, (0, 255, 0), pipe)  # Green pipes

def check_collision(bird, pipes):
    bird_rect = pygame.Rect(50, bird.y, 40, 40)  # Bird rectangle
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return True  # Collision detected
    return False

def update_game(bird, pipes):
    global bird_speed
    bird.y += bird_speed
    bird_speed += gravity

    for pipe in pipes:
        pipe.x -= 1

    if pipes[-1].x < width - pipe_interval:
        top_pipe_height = np.random.randint(100, height - pipe_gap - 100)
        bottom_pipe_height = height - pipe_gap - top_pipe_height
        pipes.append(pygame.Rect(width, 0, pipe_width, top_pipe_height))
        pipes.append(pygame.Rect(width, height - bottom_pipe_height, pipe_width, bottom_pipe_height))
    
    pipes[:] = [pipe for pipe in pipes if pipe.x > -pipe_width]

    if check_collision(bird, pipes):
        print("Game Over")
        return True

def track_hand(results):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            if thumb_tip.y < index_tip.y:
                return 'up'  # Hand is in an upward position
            else:
                return 'down'  # Hand is in a downward position
    return None

def main():
    running = True
    bird = Bird(height // 2)
    pipes = []
    top_pipe_height = np.random.randint(100, height - pipe_gap - 100)
    bottom_pipe_height = height - pipe_gap - top_pipe_height
    pipes.append(pygame.Rect(width, 0, pipe_width, top_pipe_height))
    pipes.append(pygame.Rect(width, height - bottom_pipe_height, pipe_width, bottom_pipe_height))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ret, frame = cap.read()
        if not ret:
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Hand Tracking", frame)

        detected_gesture = track_hand(results)
        if detected_gesture == 'up':
            bird.jump()

        if update_game(bird, pipes):
            break

        draw_game(screen, bird, pipes)
        pygame.display.flip()
        clock.tick(60)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
