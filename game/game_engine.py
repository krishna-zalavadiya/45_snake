import pygame
from .snake import Snake
from .food import Food

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        self.snake = Snake(self.grid_width // 2, self.grid_height // 2, self.cell_size)
        self.food = Food(self.grid_width, self.grid_height, self.cell_size)

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.large_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self.moves_per_second = 8
        self._frame_counter = 0

        self.game_over = False

    def handle_keydown(self, key):
        if self.game_over:
            # Gracefully handle input while on game over screen
            return

        # Direction changes are applied immediately on key press.
        if key in (pygame.K_UP, pygame.K_w):
            self.snake.set_direction(0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.snake.set_direction(0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.snake.set_direction(-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.set_direction(1, 0)

    def handle_input(self):
        # Reserved for continuously-held-key input
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

        if self.snake.collides_with_wall(self.grid_width, self.grid_height):
            self.game_over = True
            return

        if self.snake.collides_with_self():
            self.game_over = True
            return

        if self.snake.head_rect().colliderect(self.food.rect()):
            self.snake.grow()
            self.score += 1
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
            # Semi-transparent dark overlay background
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            # Game Over Heading
            game_over_surface = self.large_font.render("GAME OVER", True, RED)
            go_rect = game_over_surface.get_rect(center=(self.width // 2, self.height // 2 - 50))
            screen.blit(game_over_surface, go_rect)

            # Final Score
            final_score_surface = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = final_score_surface.get_rect(center=(self.width // 2, self.height // 2 + 10))
            screen.blit(final_score_surface, score_rect)

            # Prompt Instruction
            prompt_surface = self.small_font.render("Press ANY KEY to Exit", True, WHITE)
            prompt_rect = prompt_surface.get_rect(center=(self.width // 2, self.height // 2 + 60))
            screen.blit(prompt_surface, prompt_rect)