
import pygame
import random
import time
# ==========================================
# 1. INITIALIZATION & CONSTANTS
# ==========================================
pygame.init()
pygame.mixer.init()  # Required for music playback

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sub-Zero Submarine")
clock = pygame.time.Clock()

SKY_BLUE = (135, 206, 235) 
YELLOW = (255, 255, 150)
WHITE = (255, 255, 255)
BLUE = (0, 0, 200)
BLACK = (0, 0, 0)
DEEP_OCEAN = (18, 57, 122)
OXYGEN_GREEN = (0, 255, 100)
GLACIER_BLUE = (105, 196, 219)
SONAR_GOLD = (176, 151, 60)
RED = (176, 36, 26)

# ==========================================
# 2. GLOBAL GAME STATE VARIABLES
# ==========================================
game_state = "MENU"  # States: "MENU", "LEVEL_1", "LEVEL_2", "GAME_OVER", "VICTORY"
current_level = 1
depth = 0
oxygen = 100.0       # Ticks down over time

# Player properties
player_x = 380
player_y = 150
player_speed = 2
player_width = 40
player_height = 25

# Power-up variables
is_sonar_active = False
sonar_timer = 0.0
visibility_radius = 12
level_num = 1
trench_center = 400

# Dynamic Object Lists
walls = []
air_canisters = []
sonar_pickups = []

# For track expansion logic
highest_generated_y = 0
lowest_generated_y = 0

# ==========================================
# 3. GAME LOGIC FUNCTIONS
# ==========================================

def load_level_layout(level_num):
    """
    Clears all active object arrays and dynamically populates 
    glacier wall boundaries based on the selected level track.
    """
    global walls, air_canisters, sonar_pickups, current_level
    walls.clear()
    air_canisters.clear()
    sonar_pickups.clear()
    current_level = level_num # current_level = 1

    
    trench_center = 400
    trench_width = 300 if level_num == 1 else 180
    half_width = trench_width // 2
    
    # Track the current vertical drawing position manually to handle variable wall heights
    y_pos = 0
    highest_generated_y = 0
    segment_index = 0
    
    # Loop until we have generated walls down past the screen height
    segment_index = 0
    while y_pos < 800:
        # Randomize the height of this specific wall segment (between 20 and 65 pixels)
        # This makes the walls look jagged, uneven
        wall_height = random.randint(20, 65)
        
        # Slowly drift the center of the trench left or right
        trench_center += random.randint(-25, 25)
        
        # Keep the trench centered enough so it doesn't drift completely off-screen
        trench_center = max(half_width + 50, min(WIDTH - half_width - 50, trench_center))
        
        # Left wall segment
        left_wall_width = trench_center - half_width
        walls.append(pygame.Rect(0, y_pos, left_wall_width, wall_height))
        
        # Right wall segment
        right_wall_x = trench_center + half_width
        walls.append(pygame.Rect(right_wall_x, y_pos, WIDTH - right_wall_x, wall_height))
        
        # Oxygen canisters spawn all the way down, locked to the exact center line of the trench
        if random.random() < 0.40:  # 40% chance to spawn a canister
            # Centers the 15px wide canister on the trench center line
            air_x = trench_center - 7 
            # Centers the canister vertically inside this specific segment's unique height
            air_y = y_pos + (wall_height // 2) - 10
            air_canisters.append(pygame.Rect(air_x, air_y, 15, 20))

        if random.random() < 0.40:  # 40% chance to spawn a canister on any vertical spot
            # Centers the  canister exactly on the trench center line
            air_x = trench_center - 7 
            # Centers the canister vertically inside this specific segment's unique height
            air_y = y_pos + (wall_height // 2) - 10
            air_canisters.append(pygame.Rect(air_x, air_y, 15, 20))
            
            
        # Place sonar pickup perfectly centered roughly halfway down the map
        if segment_index == 10:
            sonar_y = y_pos + (wall_height // 2) - 10
            sonar_pickups.append(pygame.Rect(trench_center - 10, sonar_y, 20, 20))
            
        # Move y_pos forward by the unique height of this segment so the next blocks stack perfectly
        y_pos += wall_height
        segment_index += 1
        lowest_generated_y = y_pos

def draw_text(text, font_size, x, y, color):
    """
    Handles font assembly, surface allocation, and blitting 
    operations to clean up repetitive interface text rendering tasks.
    """
    font = pygame.font.SysFont("Helvetica", font_size, bold=True)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

 def extend_level_layout():
    """
     Generates new trench segments below the screen as old ones scroll up,
    making sure there is an infinite, path
    """
    global walls, air_canisters, sonar_pickups, trench_center, lowest_generated_y
    
    trench_width = 300 if current_level == 1 else 180
    half_width = trench_width // 2
    
    while lowest_generated_y < HEIGHT + 100:
        wall_height = random.randint(30, 65)
        trench_center += random.randint(-25, 25)
        trench_center = max(half_width + 50, min(WIDTH - half_width - 50, trench_center))
        
        walls.append(pygame.Rect(0, lowest_generated_y, trench_center - half_width, wall_height))
        right_wall_x = trench_center + half_width
        walls.append(pygame.Rect(right_wall_x, lowest_generated_y, WIDTH - right_wall_x, wall_height))
        
        # Continuously generate oxygen all the way down
        if random.random() < 0.20:
            air_x = trench_center - 7
            air_y = lowest_generated_y + (wall_height // 2) - 10
            air_canisters.append(pygame.Rect(air_x, air_y, 15, 20))
            
        # Occasional extra sonar pickups can appear as depth increases
        if random.random() < 0.03 and len(sonar_pickups) == 0:
            sonar_y = lowest_generated_y + (wall_height // 2) - 10
            sonar_pickups.append(pygame.Rect(trench_center - 10, sonar_y, 20, 20))
            
        lowest_generated_y += wall_height   
    
    
def handle_scrolling_and_movement():
    """
    Manages background shifting to simulate continuous 
    submarine diving depth, while bounding player movement.
    """
    global depth,  lowest_generated_y
    
    # Automatically moves objects up to show submarine falling/diving down
    scroll_speed = 3 if current_level == 1 else 4
    depth += 1 
    
    for wall in walls:
        wall.y -= scroll_speed
        # Loop walls back to bottom once they scroll past top boundary
        if wall.y < -40:
            wall.y = HEIGHT + random.randint(0, 20)

    for air in air_canisters:
        air.y -= scroll_speed
        if air.y < -40:
            air.y = HEIGHT + random.randint(10, 100)

    for sonar in sonar_pickups:
        sonar.y -= scroll_speed
        if sonar.y < -40:
            sonar.y = HEIGHT + random.randint(200, 400)

def manage_powerups():
    """
    Tracks and the power ups and the different levels
    """   
    global is_sonar_active, visibility_radius
    if is_sonar_active:
        if time.time() > sonar_timer:
            is_sonar_active = False
            visibility_radius = 20  # Drop back down to a dark window

    if depth == 700: 
        level_num =+ 1 
             

def check_collisions(player_rect):
    """
    Evaluates cross-intersections between the submarine and active lists. 
    
    """
    global oxygen, game_state, is_sonar_active, sonar_timer, visibility_radius

    # 1. Check Glacier Wall Collision (Immediate Damage/Failure)
    for wall in walls:
        if player_rect.colliderect(wall):
            game_state = "GAME_OVER"


    # 2. Check Oxygen Canister Collection
    for air in air_canisters:
        if player_rect.colliderect(air):
            oxygen = min(100.0, oxygen + 25.0)  # Ends at 100% capacity maximum boundary
            air_canisters.remove(air)

    # 3. Check Sonar Pickups (Power-up Modifier)
    for sonar in sonar_pickups:
        if player_rect.colliderect(sonar):
            is_sonar_active = True
            sonar_timer = time.time() + 6.0  # Power-up  changes game for 6 seconds
            visibility_radius = 800         # lights the entire trench area
            sonar_pickups.remove(sonar)

        load_level_layout(current_level)

# ==========================================
# 4. MAIN PROGRAM GAME LOOP
# ==========================================
load_level_layout(1)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
 
       
        elif event.type == pygame.KEYDOWN:
            
            # If spacebar is pressed running = true
            if event.key == pygame.K_SPACE and not running:
                running = True
            
            # Handle menu to level transition
            if game_state == "MENU" and event.key == pygame.K_SPACE:
                game_state = "LEVEL_1"
                oxygen = 100.0
                depth = 0
                load_level_layout(1)
                
            # Handle restart from Game Over or Victory screens
            elif (game_state == "GAME_OVER" or game_state == "VICTORY") and event.key == pygame.K_r:
                game_state = "MENU"
      
        # Continuous Key Input for Active Movement
    if game_state == "LEVEL_1" or game_state == "LEVEL_2":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
                player_x += player_speed
            if keys[pygame.K_UP] and player_y > 0:
                player_y -= player_speed
            if keys[pygame.K_DOWN] and player_y < HEIGHT - player_height:
                player_y += player_speed

    # Drains oxygen resource progressively per frame loop
            oxygen -= 0.08
            if oxygen <= 0:
                game_state = "GAME_OVER"

            # Tracks depth limit checkpoints to switch between level spaces
            if current_level == 1 and depth >= 1000:
                game_state = "LEVEL_2"
                load_level_layout(2)  # Swaps entire structural wall layout matrix dynamically
            elif current_level == 2 and depth >= 2500:
                game_state = "VICTORY"

            # Applys continuous simulation loop steps
            handle_scrolling_and_movement()
            manage_powerups()
            
            # Builds the tracking rect for collision check call
            sub_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            check_collisions(sub_rect)   # Drain oxygen resource progressively per frame loop
            oxygen -= 0.08
            if oxygen <= 0:
                    game_state = "GAME_OVER"
            

    # ==========================================
    # 5. DRAWING & RENDERING (Polish Architecture)
    # ==========================================
    screen.fill(DEEP_OCEAN)
    if game_state == "MENU":
            draw_text("SUB-ZERO SUBMARINE", 50, 140, 200, GLACIER_BLUE)
            draw_text("Press SPACEBAR to Begin Mission", 24, 230, 320, WHITE)
            draw_text("Controls: Arrow Keys | Avoid walls, collect green oxygen cores.", 18, 170, 450, WHITE)

    elif game_state == "LEVEL_1" or game_state == "LEVEL_2":
            # Create surfaces for the objects
            for wall in walls:
                pygame.draw.rect(screen, GLACIER_BLUE, wall)
            for air in air_canisters:
                pygame.draw.rect(screen, OXYGEN_GREEN, air)
            for sonar in sonar_pickups:
                pygame.draw.rect(screen, SONAR_GOLD, sonar)
                # Draw Player Submarine
            
            pygame.draw.rect(screen, RED, (player_x, player_y, player_width, player_height))

            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 50))
            draw_text(f"level: {level_num}", 18, 20, 15, GLACIER_BLUE)
            draw_text(f"DEPTH: {depth}m", 18, 180, 15, WHITE)
            draw_text(f"OXYGEN: {int(oxygen)}%", 18, 380, 15, OXYGEN_GREEN if oxygen > 30 else RED)
        
    if is_sonar_active:
            draw_text("SONAR OVERDRIVE ACTIVE", 16, 560, 15, SONAR_GOLD)
    elif game_state == "GAME_OVER":
            draw_text("SYSTEMS FAILURE", 46, 110, 200, RED)
            draw_text(f"Your sub was lost at deep depth: {depth} meters.", 20, 210, 300, WHITE)
            draw_text("Press 'R' Key to Return to Base Menu", 18, 240, 400, WHITE)
    
    elif game_state == "VICTORY":
        draw_text("TRENCH EXPLORATION COMPLETE", 44, 70, 200, OXYGEN_GREEN)

    # manages time and frames per second
    clock.tick(75)

    # update the display
    pygame.display.flip()

            



