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

# Define game states
MENU = 0
OPTIONS = 1
PLAYING = 2
GAME_OVER = 3

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Options:
    """
    Options class to store and manage game settings.
    """
    def __init__(self):
        # Difficulty affects starting snake speed
        self.difficulties = ["Easy", "Medium", "Hard", "Very Hard", "Extreme"]
        self.difficulty_idx = 1  # Default to Medium
        
        # Snake colors
        self.snake_colors = [GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE]
        self.snake_color_idx = 0  # Default to GREEN
        
        # Food colors
        self.food_colors = [RED, ORANGE, YELLOW, PURPLE, CYAN, WHITE]
        self.food_color_idx = 0  # Default to RED
        
        # Speed settings (FPS)
        self.speeds = [10, 15, 20, 25, 30, 60, 120, 240]
        self.speed_idx = 1  # Default to 15 FPS
    
    @property
    def difficulty(self):
        return self.difficulties[self.difficulty_idx]
    
    @property
    def snake_color(self):
        return self.snake_colors[self.snake_color_idx]
    
    @property
    def food_color(self):
        return self.food_colors[self.food_color_idx]
    
    @property
    def speed(self):
        return self.speeds[self.speed_idx]
    
    def next_difficulty(self):
        self.difficulty_idx = (self.difficulty_idx + 1) % len(self.difficulties)
    
    def prev_difficulty(self):
        self.difficulty_idx = (self.difficulty_idx - 1) % len(self.difficulties)
    
    def next_snake_color(self):
        self.snake_color_idx = (self.snake_color_idx + 1) % len(self.snake_colors)
    
    def prev_snake_color(self):
        self.snake_color_idx = (self.snake_color_idx - 1) % len(self.snake_colors)
    
    def next_food_color(self):
        self.food_color_idx = (self.food_color_idx + 1) % len(self.food_colors)
    
    def prev_food_color(self):
        self.food_color_idx = (self.food_color_idx - 1) % len(self.food_colors)
    
    def next_speed(self):
        self.speed_idx = (self.speed_idx + 1) % len(self.speeds)
    
    def prev_speed(self):
        self.speed_idx = (self.speed_idx - 1) % len(self.speeds)


class Snake:
    """
    Snake class to manage the snake's body segments, movement, and behavior.
    """
    def __init__(self, color=GREEN):
        """Initialize the snake with a default position and direction."""
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]  # Start at the center
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grew = False
        self.color = color

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
    def __init__(self, color=RED):
        """Initialize food with a random position."""
        self.position = (0, 0)
        self.color = color
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
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.options = Options()
        self.game_state = MENU
        self.selected_option = 0  # For menu navigation
        self.menu_options = ["Play Game", "Options", "Quit"]
        self.options_menu_items = ["Difficulty", "Snake Color", "Food Color", "Back"]
        self.reset_game()

    def reset_game(self):
        """Reset the game state to start a new game."""
        self.snake = Snake(self.options.snake_color)
        self.food = Food(self.options.food_color)
        self.score = 0

    def handle_events(self):
        """Process user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_state == MENU:
                    self.handle_menu_input(event.key)
                elif self.game_state == OPTIONS:
                    self.handle_options_input(event.key)
                elif self.game_state == PLAYING:
                    self.handle_game_input(event.key)
                elif self.game_state == GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.game_state = PLAYING
                    elif event.key == pygame.K_m:
                        self.game_state = MENU

    def handle_menu_input(self, key):
        """Handle input in the main menu."""
        if key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.selected_option == 0:  # Play Game
                self.reset_game()
                self.game_state = PLAYING
            elif self.selected_option == 1:  # Options
                self.game_state = OPTIONS
                self.selected_option = 0
            elif self.selected_option == 2:  # Quit
                pygame.quit()
                sys.exit()

    def handle_options_input(self, key):
        """Handle input in the options menu."""
        if key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.options_menu_items)
        elif key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options_menu_items)
        elif key == pygame.K_LEFT:
            if self.selected_option == 0:  # Difficulty
                self.options.prev_difficulty()
            elif self.selected_option == 1:  # Snake Color
                self.options.prev_snake_color()
            elif self.selected_option == 2:  # Food Color
                self.options.prev_food_color()
        elif key == pygame.K_RIGHT:
            if self.selected_option == 0:  # Difficulty
                self.options.next_difficulty()
            elif self.selected_option == 1:  # Snake Color
                self.options.next_snake_color()
            elif self.selected_option == 2:  # Food Color
                self.options.next_food_color()
        elif key == pygame.K_RETURN or key == pygame.K_SPACE or key == pygame.K_ESCAPE:
            if self.selected_option == 3 or key == pygame.K_ESCAPE:  # Back
                self.game_state = MENU
                self.selected_option = 0

    def handle_game_input(self, key):
        """Handle input during gameplay."""
        if key == pygame.K_UP or key == pygame.K_w:
            self.snake.change_direction(UP)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.snake.change_direction(DOWN)
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.snake.change_direction(LEFT)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.snake.change_direction(RIGHT)
        elif key == pygame.K_ESCAPE:
            self.game_state = MENU

    def update(self):
        """Update game state."""
        if self.game_state == PLAYING:
            # Move snake and check for self collision
            if not self.snake.move():
                self.game_state = GAME_OVER
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

    def draw_menu(self):
        """Draw the main menu."""
        self.screen.fill(BLACK)
        
        # Draw title
        title = self.title_font.render("Snake Game", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        # Draw menu options
        for i, option in enumerate(self.menu_options):
            color = YELLOW if i == self.selected_option else WHITE
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + i * 50))
            self.screen.blit(text, text_rect)
        
        # Draw instructions
        instructions = self.font.render("Use Arrow Keys to Navigate, Enter to Select", True, WHITE)
        instructions_rect = instructions.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        self.screen.blit(instructions, instructions_rect)

    def draw_options_menu(self):
        """Draw the options menu."""
        self.screen.fill(BLACK)
        
        # Draw title
        title = self.title_font.render("Options", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//6))
        self.screen.blit(title, title_rect)
        
        # Draw option items
        y_offset = SCREEN_HEIGHT // 3
        option_values = [
            self.options.difficulty,
            "< Preview >",
            "< Preview >",
            ""
        ]
        
        for i, option in enumerate(self.options_menu_items):
            # Highlight selected option
            color = YELLOW if i == self.selected_option else WHITE
            
            # Draw option name
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(midright=(SCREEN_WIDTH//2 - 20, y_offset + i * 60))
            self.screen.blit(text, text_rect)
            
            # Draw option value
            if i == 1:  # Snake color preview
                pygame.draw.rect(self.screen, self.options.snake_color, 
                                pygame.Rect(SCREEN_WIDTH//2 + 20, y_offset + i * 60 - 15, 30, 30))
                pygame.draw.rect(self.screen, BLACK, 
                                pygame.Rect(SCREEN_WIDTH//2 + 20, y_offset + i * 60 - 15, 30, 30), 1)
            elif i == 2:  # Food color preview
                pygame.draw.rect(self.screen, self.options.food_color, 
                                pygame.Rect(SCREEN_WIDTH//2 + 20, y_offset + i * 60 - 15, 30, 30))
                pygame.draw.rect(self.screen, BLACK, 
                                pygame.Rect(SCREEN_WIDTH//2 + 20, y_offset + i * 60 - 15, 30, 30), 1)
            else:
                value_text = self.font.render(option_values[i], True, color)
                value_rect = value_text.get_rect(midleft=(SCREEN_WIDTH//2 + 20, y_offset + i * 60))
                self.screen.blit(value_text, value_rect)
        
        # Draw instructions
        instructions = self.font.render("Use Arrow Keys to Navigate and Change Values", True, WHITE)
        instructions_rect = instructions.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        self.screen.blit(instructions, instructions_rect)

    def draw_game(self):
        """Draw the game elements."""
        self.screen.fill(BLACK)
        
        # Draw snake and food
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (5, 5))

    def draw_game_over(self):
        """Draw the game over screen."""
        self.screen.fill(BLACK)
        
        # Draw game over message
        game_over_text = self.title_font.render('Game Over', True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.screen.blit(game_over_text, text_rect)
        
        # Draw score
        score_text = self.font.render(f'Final Score: {self.score}', True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        # Draw restart instructions
        restart_text = self.font.render('Press R to Restart or M for Menu', True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        """Render the game elements based on current state."""
        if self.game_state == MENU:
            self.draw_menu()
        elif self.game_state == OPTIONS:
            self.draw_options_menu()
        elif self.game_state == PLAYING:
            self.draw_game()
        elif self.game_state == GAME_OVER:
            self.draw_game_over()
        
        pygame.display.update()

    def run(self):
        """Main game loop."""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            
            # Use the selected speed when playing, otherwise use a standard fps
            if self.game_state == PLAYING:
                if self.options.difficulty == "Easy":
                    self.clock.tick(10)
                elif self.options.difficulty == "Medium":
                    self.clock.tick(15)
                elif self.options.difficulty == "Hard":
                    self.clock.tick(30)
                elif self.options.difficulty == "Very Hard":
                    self.clock.tick(60)
                elif self.options.difficulty == "Extreme":
                    self.clock.tick(120)
            else:
                self.clock.tick(30)  # Standard FPS for menus


if __name__ == "__main__":
    game = Game()
    game.run()

