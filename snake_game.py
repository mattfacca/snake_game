#!/usr/bin/env python3
"""
Terminal Snake Game
------------------
A classic snake game that runs in the terminal using Python's curses library.
Use arrow keys to control the snake, eat food to grow, and avoid hitting walls or yourself.
"""

import curses
import random
import time
from curses import textpad

def main(stdscr):
    """Main game function."""
    # Setup initial screen
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Set input timeout for snake speed
    
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Food
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # UI elements
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Border

    # Start the game loop
    while True:
        # Get terminal dimensions
        height, width = stdscr.getmaxyx()
        
        # Check if terminal is large enough
        if height < 10 or width < 30:
            stdscr.clear()
            display_too_small_message(stdscr)
            stdscr.refresh()
            time.sleep(0.5)
            continue
            
        # Start a new game
        score = game_loop(stdscr, height, width)
        
        # Display game over screen
        if not display_game_over(stdscr, score):
            break

def display_too_small_message(stdscr):
    """Display a message when the terminal is too small."""
    height, width = stdscr.getmaxyx()
    y = max(0, height // 2 - 1)
    x = max(0, width // 2 - 15)
    stdscr.addstr(y, x, "Terminal too small!", curses.color_pair(3))
    stdscr.addstr(y+1, x, "Please resize and try again.", curses.color_pair(3))

def create_food(snake, box):
    """Create food at a random position that isn't on the snake."""
    food = None
    while food is None:
        # Generate random position within boundaries
        food = [
            random.randint(box[0][0]+1, box[1][0]-1),
            random.randint(box[0][1]+1, box[1][1]-1)
        ]
        # Check if food is on snake
        if food in snake:
            food = None
    return food

def display_score(stdscr, score, height, width):
    """Display the current score."""
    score_text = f"Score: {score}"
    stdscr.addstr(0, width // 2 - len(score_text) // 2, score_text, curses.color_pair(3))

def display_game_over(stdscr, score):
    """Display game over screen and ask if player wants to play again."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # Display game over and score
    game_over_text = "GAME OVER"
    score_text = f"Final Score: {score}"
    play_again_text = "Play again? (y/n)"
    
    center_y = height // 2
    
    stdscr.addstr(center_y - 2, width // 2 - len(game_over_text) // 2, 
                 game_over_text, curses.A_BOLD | curses.color_pair(2))
    stdscr.addstr(center_y, width // 2 - len(score_text) // 2, 
                 score_text, curses.color_pair(3))
    stdscr.addstr(center_y + 2, width // 2 - len(play_again_text) // 2, 
                 play_again_text, curses.color_pair(3))
    
    stdscr.refresh()
    
    # Wait for valid input (y/n)
    while True:
        key = stdscr.getch()
        if key in [ord('y'), ord('Y')]:
            return True
        elif key in [ord('n'), ord('N')]:
            return False

def display_instructions(stdscr, height, width):
    """Display the game instructions."""
    instructions = "Use arrow keys to move. Press 'q' to quit."
    stdscr.addstr(height-1, width // 2 - len(instructions) // 2, instructions, curses.color_pair(3))

def game_loop(stdscr, height, width):
    """Main game loop."""
    # Reset and clear screen
    stdscr.clear()
    
    # Calculate game area
    max_y, max_x = height - 2, width - 2
    box = [[1, 1], [max_y, max_x]]
    
    # Draw border
    textpad.rectangle(stdscr, box[0][0], box[0][1], box[1][0], box[1][1])
    
    # Initialize snake in the middle of the screen
    snake = [[height // 2, width // 4]]
    direction = curses.KEY_RIGHT  # Start moving right
    
    # Create initial food
    food = create_food(snake, box)
    
    # Initialize score
    score = 0
    
    # Display instructions and score
    display_instructions(stdscr, height, width)
    display_score(stdscr, score, height, width)
    
    # Game loop
    while True:
        # Display score
        display_score(stdscr, score, height, width)
        
        # Get user input
        key = stdscr.getch()
        
        # Handle input - prevent 180 degree turns
        if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            if key == curses.KEY_UP and direction != curses.KEY_DOWN:
                direction = key
            elif key == curses.KEY_DOWN and direction != curses.KEY_UP:
                direction = key
            elif key == curses.KEY_LEFT and direction != curses.KEY_RIGHT:
                direction = key
            elif key == curses.KEY_RIGHT and direction != curses.KEY_LEFT:
                direction = key
        
        # Quit game with 'q'
        elif key == ord('q'):
            return score
        
        # Calculate new head position based on direction
        new_head = snake[0].copy()
        if direction == curses.KEY_UP:
            new_head[0] -= 1
        elif direction == curses.KEY_DOWN:
            new_head[0] += 1
        elif direction == curses.KEY_LEFT:
            new_head[1] -= 1
        elif direction == curses.KEY_RIGHT:
            new_head[1] += 1
        
        # Add new head to snake
        snake.insert(0, new_head)
        
        # Check for collisions with walls
        if (snake[0][0] <= box[0][0] or 
            snake[0][0] >= box[1][0] or 
            snake[0][1] <= box[0][1] or 
            snake[0][1] >= box[1][1]):
            return score
        
        # Check for collisions with self (skip the head)
        if snake[0] in snake[1:]:
            return score
        
        # Check if snake ate food
        if snake[0] == food:
            # Create new food
            food = create_food(snake, box)
            score += 1
            
            # Speed up the game as score increases
            new_timeout = max(50, 100 - (score * 2))
            stdscr.timeout(new_timeout)
        else:
            # Remove tail if no food eaten
            tail = snake.pop()
            # Clear the old tail position
            stdscr.addch(tail[0], tail[1], ' ')
        
        # Draw food
        stdscr.addch(food[0], food[1], '*', curses.color_pair(2))
        
        # Draw snake
        for i, segment in enumerate(snake):
            if i == 0:  # Head
                stdscr.addch(segment[0], segment[1], '@', curses.color_pair(1) | curses.A_BOLD)
            else:  # Body
                stdscr.addch(segment[0], segment[1], 'o', curses.color_pair(1))
        
        # Update border (in case it was overwritten)
        textpad.rectangle(stdscr, box[0][0], box[0][1], box[1][0], box[1][1])
        
        # Display instructions
        display_instructions(stdscr, height, width)
        
        # Refresh screen
        stdscr.refresh()

def start_screen(stdscr):
    """Display the start screen with instructions."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    title = "SNAKE GAME"
    
    # Display title
    stdscr.addstr(height // 2 - 5, width // 2 - len(title) // 2,
                 title, curses.A_BOLD | curses.color_pair(1))
    
    # Display instructions
    instructions = [
        "How to play:",
        "Use arrow keys to move the snake",
        "Eat food (*) to grow and earn points",
        "Avoid hitting walls and yourself",
        "Press 'q' any time to quit",
        "",
        "Press any key to start!"
    ]
    
    for i, line in enumerate(instructions):
        y = height // 2 - 2 + i
        x = width // 2 - len(line) // 2
        if y < height and x > 0:
            stdscr.addstr(y, x, line, curses.color_pair(3))
    
    stdscr.refresh()
    stdscr.getch()  # Wait for any key press

if __name__ == "__main__":
    # Initialize curses and start the game
    try:
        curses.wrapper(lambda stdscr: (start_screen(stdscr), main(stdscr)))
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    finally:
        # Ensure terminal is restored to normal state
        curses.endwin()
        print("Thanks for playing Snake Game!")

