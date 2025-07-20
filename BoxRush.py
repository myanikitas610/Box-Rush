import pygame
import sys
import random
import time

# Initialize pygame modules
pygame.init()

pygame.mixer.init()
coin_sound = pygame.mixer.Sound('audio/coin_collect.wav')
# Set screen dimensions and create display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Box Rush")

# Define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
YELLOW = (255, 215, 0)

clock = pygame.time.Clock()
FPS = 60  # Frames per second

# Game physics constants
GRAVITY = 0.8
JUMP_POWER = -15
SCROLL_SPEED = 5  # Speed at which platforms, obstacles, and coins move left

# Player properties and starting position
player_size = 40
player_x = 100  # Fixed horizontal position
player_y = HEIGHT - 100
player_vel_y = 0  # Vertical velocity for jumping and falling
alive = True
game_started = False
start_time = 0
elapsed_time = 0

# Ground properties
GROUND_HEIGHT = 50
GROUND_Y = HEIGHT - GROUND_HEIGHT

# Initialize joystick (Xbox controller) if connected
pygame.joystick.init()
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Controller connected:", joystick.get_name())

# Font for displaying text
font = pygame.font.SysFont(None, 36)

# Platforms represented by pygame.Rect objects (x, y, width, height)
platforms = [
    pygame.Rect(500, GROUND_Y - 100, 200, 20),
    pygame.Rect(900, GROUND_Y - 200, 200, 20),
    pygame.Rect(1300, GROUND_Y - 100, 200, 20)
]

# Obstacles that cause death on collision
obstacles = [
    pygame.Rect(700, GROUND_Y - 40, 30, 40),
    pygame.Rect(1100, GROUND_Y - 140, 30, 40)
]

# Coins to collect, represented as small rectangles/ellipses
coins = [
    pygame.Rect(550, GROUND_Y - 120, 15, 15),
    pygame.Rect(950, GROUND_Y - 220, 15, 15),
    pygame.Rect(1350, GROUND_Y - 120, 15, 15)
]

score = 0  # Player's collected coins count
on_ground = False  # Track if player is on ground or platform
jump_count = 0  # Number of jumps done without landing (for double jump)

last_jump_time = 0  # Timestamp of last jump (for jump cooldown)
jump_cooldown = 0.2  # Minimum seconds between jumps


def reset_game():
    """Reset game state to initial conditions for restarting."""
    global player_y, player_vel_y, alive, platforms, obstacles, coins, score, jump_count, on_ground, game_started, elapsed_time
    elapsed_time = 0
    player_y = GROUND_Y - player_size
    player_vel_y = 0
    alive = True
    game_started = False
    score = 0
    jump_count = 0
    on_ground = False

    # Reset platforms positions
    platforms[:] = [
        pygame.Rect(500, GROUND_Y - 100, 200, 20),
        pygame.Rect(900, GROUND_Y - 200, 200, 20),
        pygame.Rect(1300, GROUND_Y - 100, 200, 20)
    ]
    # Reset obstacles positions
    obstacles[:] = [
        pygame.Rect(700, GROUND_Y - 40, 30, 40),
        pygame.Rect(1100, GROUND_Y - 140, 30, 40)
    ]
    # Reset coins positions
    coins[:] = [
        pygame.Rect(550, GROUND_Y - 120, 15, 15),
        pygame.Rect(950, GROUND_Y - 220, 15, 15),
        pygame.Rect(1350, GROUND_Y - 120, 15, 15)
    ]
    print("Game Reset")


def start_game():
    """Initialize variables to start the game."""
    global game_started, alive, player_y, player_vel_y, jump_count, on_ground, start_time
    game_started = True
    alive = True
    player_y = GROUND_Y - player_size
    player_vel_y = 0
    jump_count = 0
    on_ground = True
    start_time = time.time()
    print("Game Started")


# Main game loop
while True:
    screen.fill(WHITE)  # Clear screen each frame
    keys = pygame.key.get_pressed()

    # Event handling loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Quit game if ESC pressed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        # Quit game if B button on Xbox controller pressed
        if joystick and event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:  # B button index
                pygame.quit()
                sys.exit()

        # Start game on Space bar or A button press (if game not started yet)
        if not game_started:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
               (joystick and event.type == pygame.JOYBUTTONDOWN and event.button == 0):
                start_game()

        # Handle jumping when alive
        elif alive:
            if ((event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or
                (joystick and event.type == pygame.JOYBUTTONDOWN and event.button == 0)):
                current_time = time.time()
                # Allow jump only if double jump not exceeded and cooldown passed
                if jump_count < 2 and current_time - last_jump_time > jump_cooldown:
                    player_vel_y = JUMP_POWER
                    jump_count += 1
                    on_ground = False
                    last_jump_time = current_time

        # Restart game if dead and player presses R key or Y button
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()
            if joystick and event.type == pygame.JOYBUTTONDOWN:
                if event.button == 3:  # Y button index
                    reset_game()

    # Game logic when started and player is alive
    if game_started and alive:
        # Apply gravity to vertical velocity and update vertical position
        player_vel_y += GRAVITY
        player_y += player_vel_y

        # Player's rectangle for collision detection
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        on_ground = False  # Reset on_ground each frame

        elapsed_time = time.time() - start_time

        # Move platforms left; reposition if offscreen
        for plat in platforms:
            plat.x -= SCROLL_SPEED
            if plat.right < 0:
                plat.x = WIDTH + 200
                plat.y = random.choice([GROUND_Y - 100, GROUND_Y - 150, GROUND_Y - 200])

        # Move obstacles left; reposition if offscreen
        for obs in obstacles:
            obs.x -= SCROLL_SPEED
            if obs.right < 0:
                obs.x = WIDTH + 500

        # Move coins left; respawn on platforms or ground if offscreen
        for coin in coins:
            coin.x -= SCROLL_SPEED
            if coin.right < 0:
                coin.x = WIDTH + random.randint(300, 600)
                # Pick a platform top or ground level for coin Y position
                platform_tops = [GROUND_Y] + [plat.top for plat in platforms]
                chosen_top = random.choice(platform_tops)
                coin.y = chosen_top - coin.height  # position coin on top

        for plat in platforms:
            if player_rect.colliderect(plat):
                if player_vel_y > 0 and player_rect.bottom - player_vel_y <= plat.top + 5:
                    player_y = plat.top - player_size
                    player_vel_y = 0
                    on_ground = True
                    jump_count = 0
                    break
                elif player_vel_y < 0 and player_rect.top - player_vel_y >= plat.bottom - 5:
                    player_y = plat.bottom
                    player_vel_y = 0

        # Check collision with ground (if not on platform)
        if not on_ground and player_y + player_size >= GROUND_Y:
            player_y = GROUND_Y - player_size
            player_vel_y = 0
            on_ground = True
            jump_count = 0

        # Update player rect after position adjustments
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        # Check if player hit an obstacle (death)
        for obs in obstacles:
            if player_rect.colliderect(obs):
                alive = False
                print("You Died!")
                print ("You survived for", {int(elapsed_time)} ,"seconds and earned", score, "coins")
                print ("Press R or Y on Controller to Restart.")

        # Check if player collected any coins, increment score and respawn coin
        for coin in coins:
            if player_rect.colliderect(coin):
                score += 1
                coin_sound.play()
                # Respawn coin offscreen at random platform or ground height
                coin.x = WIDTH + random.randint(300, 600)
                platform_tops = [GROUND_Y] + [plat.top for plat in platforms]
                chosen_top = random.choice(platform_tops)
                coin.y = chosen_top - coin.height

        # If player falls below screen bottom, trigger death
        if player_y > HEIGHT:
            alive = False
            print("You Died! Press R or Y on Controller to Restart.")

    # Draw the player (blue if alive, red if dead)
    pygame.draw.rect(screen, BLUE if alive else RED, (player_x, player_y, player_size, player_size))

    # Draw the ground as a black rectangle
    pygame.draw.rect(screen, BLACK, (0, GROUND_Y, WIDTH, GROUND_HEIGHT))

    # Draw all platforms as black rectangles
    for plat in platforms:
        pygame.draw.rect(screen, BLACK, plat)

    # Draw all obstacles as red rectangles
    for obs in obstacles:
        pygame.draw.rect(screen, RED, obs)

    # Draw all coins as yellow ellipses
    for coin in coins:
        pygame.draw.ellipse(screen, YELLOW, coin)

    # Draw the coin score in top-left corner
    score_text = font.render(f"Coins: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    #Display elapsed time
    timer_text = font.render (f"Time: {int(elapsed_time)}s", True, BLACK)
    screen.blit(timer_text, (10,40))

    # Draw start message if game hasn't started yet
    if not game_started:
        start_text = font.render("Press SPACE or A to Start", True, BLACK)
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(start_text, start_rect)

    # Draw game over message if player is dead
    elif not alive:
        game_over_text = font.render("GAME OVER! Press Y or R to Restart", True, RED)
        over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, over_rect)
        results_text = font.render(
            f"You survived for {int(elapsed_time)} seconds and earned {score} coins", 
            True, BLUE
            )
        results_rect = results_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        screen.blit(results_text, results_rect)

    # Draw exit instruction text at bottom-right corner (red color)
    exit_text = font.render("Press B or ESC to Exit", True, RED)
    exit_rect = exit_text.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
    screen.blit(exit_text, exit_rect)

    # Update the display every frame
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)
