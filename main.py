#!/usr/bin/env python3
"""
Snake Game using PyGame
A classic implementation of the Snake game where the player controls a snake
that grows as it eats food while avoiding collisions with walls and itself.
"""

import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

# Define constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SNAKE_SPEED = 15  # Frames per second

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    """
    Snake class to manage the snake's body segments, movement, and behavior.
    """
    def __init__(self):
        """Initialize the snake with a default position and direction."""
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]  # Start at the center
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grew = False
        self.color = GREEN

    def get_head_position(self):
        """Return the position of the snake's head."""
        return self.positions[0]

    def change_direction(self, direction):
        """
        Change the snake's direction ensuring it can't reverse directly into itself.
        """
        if self.next_direction != self._get_opposite_direction(direction):
            self.next_direction = direction

    def _get_opposite_direction(self, direction):
        """Returns the opposite direction."""
        if direction == UP:
            return DOWN
        elif direction == DOWN:
            return UP
        elif direction == LEFT:
            return RIGHT
        elif direction == RIGHT:
            return LEFT

    def move(self):
        """Move the snake by updating its position."""
        self.direction = self.next_direction
        head = self.get_head_position()
        x, y = self.direction
        new_position = (((head[0] + x) % GRID_WIDTH), ((head[1] + y) % GRID_HEIGHT))
        
        # Check for collision with self
        if new_position in self.positions[1:]:
            return False  # Game over
        
        # Update positions
        self.positions.insert(0, new_position)
        if not self.grew:
            self.positions.pop()
        else:
            self.grew = False
        return True

    def grow(self):
        """Grow the snake by one segment."""
        self.grew = True

    def draw(self, surface):
        """Draw the snake on the game surface."""
        for i, p in enumerate(self.positions):
            r = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            # Use a slightly different color for the head
            pygame.draw.rect(surface, BLUE if i == 0 else self.color, r)
            pygame.draw.rect(surface, BLACK, r, 1)  # Draw a black border


class Food:
    """
    Food class to manage food spawning and collision with the snake.
    """
    def __init__(self):
        """Initialize food with a random position."""
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        """Place food at a random position on the grid."""
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def draw(self, surface):
        """Draw the food on the game surface."""
        r = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, BLACK, r, 1)  # Draw a black border


class Game:
    """
    Main Game class to manage the game state, logic, and rendering.
    """
    def __init__(self):
        """Initialize the game with a window, snake, food, and score."""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.reset_game()

    def reset_game(self):
        """Reset the game state to start a new game."""
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False

    def handle_events(self):
        """Process user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    # Change direction based on arrow key presses
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.change_direction(RIGHT)

    def update(self):
        """Update game state - move snake, check collisions, update score."""
        if not self.game_over:
            # Move snake and check for self collision
            if not self.snake.move():
                self.game_over = True
                return

            # Check for food collision
            if self.snake.get_head_position() == self.food.position:
                self.snake.grow()
                self.score += 1
                
                # Ensure food doesn't spawn on snake
                while True:
                    self.food.randomize_position()
                    if self.food.position not in self.snake.positions:
                        break

    def draw(self):
        """Render the game elements to the screen."""
        self.screen.fill(BLACK)
        
        # Draw snake and food
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (5, 5))
        
        # Draw game over message if applicable
        if self.game_over:
            game_over_text = self.font.render('Game Over! Press R to Restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        pygame.display.update()

    def run(self):
        """Main game loop."""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(SNAKE_SPEED)


if __name__ == "__main__":
    game = Game()
    game.run()

