import pygame
import array
from .snake import Snake
from .food import Food

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0)

def generate_beep_sound(frequency=440, duration=0.1, sample_rate=22050):
    """Generates a simple synthetic sound effect using raw PCM audio buffer."""
    import math
    num_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        t = float(i) / sample_rate
        # Generate sine wave sample (16-bit audio)
        val = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * frequency * t))
        buf[i] = val
    return pygame.mixer.Sound(buffer=buf)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        self.font = pygame.font.SysFont("Arial", 30)
        self.large_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)

        # Initialize Pygame audio mixer and sounds
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
        self.eat_sound = None
        self.game_over_sound = None
        self._init_sounds()

        self.moves_per_second = 8
        self.reset(self.moves_per_second)

    def _init_sounds(self):
        """Loads sound effects from files or generates fallback tone effects."""
        try:
            self.eat_sound = pygame.mixer.Sound("assets/eat.wav")
        except (FileNotFoundError, pygame.error):
            # High pitched short blip for eating food
            self.eat_sound = generate_beep_sound(frequency=880, duration=0.08)

        try:
            self.game_over_sound = pygame.mixer.Sound("assets/gameover.wav")
        except (FileNotFoundError, pygame.error):
            # Lower pitched tone for game over
            self.game_over_sound = generate_beep_sound(frequency=220, duration=0.4)

    def play_sound(self, sound):
        if sound:
            sound.play()

    def reset(self, moves_per_second=None):
        if moves_per_second:
            self.moves_per_second = moves_per_second

        self.snake = Snake(self.grid_width // 2, self.grid_height // 2, self.cell_size)
        self.food = Food(self.grid_width, self.grid_height, self.cell_size)
        self.score = 0
        self._frame_counter = 0
        self.game_over = False

    def handle_keydown(self, key):
        if self.game_over:
            if key in (pygame.K_1, pygame.K_e):
                self.reset(moves_per_second=5)
            elif key in (pygame.K_2, pygame.K_m):
                self.reset(moves_per_second=10)
            elif key in (pygame.K_3, pygame.K_h):
                self.reset(moves_per_second=15)
            elif key in (pygame.K_ESCAPE, pygame.K_q):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if key in (pygame.K_UP, pygame.K_w):
            self.snake.set_direction(0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.snake.set_direction(0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.snake.set_direction(-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.set_direction(1, 0)

    def handle_input(self):
        pass

    def update(self):
        if self.game_over:
            return

        self._frame_counter += 1
        frames_per_move = max(1, 60 // self.moves_per_second)
        if self._frame_counter < frames_per_move:
            return
        self._frame_counter = 0

        self.snake.move()

        if self.snake.collides_with_wall(self.grid_width, self.grid_height) or self.snake.collides_with_self():
            self.game_over = True
            self.play_sound(self.game_over_sound)
            return

        if self.snake.head_rect().colliderect(self.food.rect()):
            self.snake.grow()
            self.score += 1
            self.play_sound(self.eat_sound)
            self.food.respawn(self.snake.body)

    def render(self, screen):
        # Draw food
        pygame.draw.rect(screen, RED, self.food.rect())

        # Draw snake
        for rect in self.snake.segment_rects():
            pygame.draw.rect(screen, GREEN, rect)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Render Game Over Overlay
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(210)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            go_surf = self.large_font.render("GAME OVER", True, RED)
            screen.blit(go_surf, go_surf.get_rect(center=(self.width // 2, self.height // 2 - 100)))

            score_surf = self.font.render(f"Final Score: {self.score}", True, WHITE)
            screen.blit(score_surf, score_surf.get_rect(center=(self.width // 2, self.height // 2 - 40)))

            opt_title = self.small_font.render("Select Difficulty to Play Again:", True, YELLOW)
            screen.blit(opt_title, opt_title.get_rect(center=(self.width // 2, self.height // 2 + 20)))

            opt1 = self.small_font.render("[1] Easy   (Slow)", True, WHITE)
            opt2 = self.small_font.render("[2] Medium (Normal)", True, WHITE)
            opt3 = self.small_font.render("[3] Hard   (Fast)", True, WHITE)
            opt4 = self.small_font.render("[Q / ESC]  Quit Game", True, WHITE)

            screen.blit(opt1, opt1.get_rect(center=(self.width // 2, self.height // 2 + 55)))
            screen.blit(opt2, opt2.get_rect(center=(self.width // 2, self.height // 2 + 85)))
            screen.blit(opt3, opt3.get_rect(center=(self.width // 2, self.height // 2 + 115)))
            screen.blit(opt4, opt4.get_rect(center=(self.width // 2, self.height // 2 + 155)))