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
DEEP_OCEAN = (10, 25, 50)
OXYGEN_GREEN = (0, 255, 100)

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
player_speed = 5
player_width = 40
player_height = 25

# Power-up variables
is_sonar_active = False
sonar_timer = 0.0
visibility_radius = 12

# Dynamic Object Lists
walls = []
air_canisters = []
sonar_pickups = []

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
    current_level = level_num

    # Creative Logic: Dynamically generate an unpredictable vertical cavern trench
    # This avoids hardcoding every single wall piece
    trench_center = 400
    trench_width = 300 if level_num == 1 else 180  # Level 2 is significantly narrower
    # Generate segments down the screen
    for i in range(0, 20):
        y_pos = i * 40
        # Slowly drift the center of the trench left or right
        trench_center += random.randint(-25, 25)
        
        # Left wall segment
        left_wall_width = trench_center - (trench_width // 2)
        walls.append(pygame.Rect(0, y_pos, left_wall_width, 35))
        
        # Right wall segment
        right_wall_x = trench_center + (trench_width // 2)
        walls.append(pygame.Rect(right_wall_x, y_pos, WIDTH - right_wall_x, 35))

        # Randomly place items inside the safe trench zones
        if i % 4 == 2:
            air_canisters.append(pygame.Rect(trench_center + random.randint(-40, 40), y_pos, 15, 20))
        if i == 10:
            sonar_pickups.append(pygame.Rect(trench_center, y_pos, 20, 20))

def draw_text(text, font_size, x, y, color):
    """
    Handles font assembly, surface allocation, and blitting 
    operations to clean up repetitive interface text rendering tasks.
    """
    font = pygame.font.SysFont("Helvetica", font_size, bold=True)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))
    
    
def handle_scrolling_and_movement():
    """
    Manages background matrix shifting to simulate continuous 
    submarine diving depth, while bounding player movement.
    """
    global depth, player_y
    
    # Automatically move objects upward to simulate submarine falling/diving down
    scroll_speed = 3 if current_level == 1 else 4
    depth += scroll_speed // 2
    
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
    global is_sonar_active  visibility_radius
    if is_sonar_active:
        if time.time() > sonar_timer:
            is_sonar_active = False
            visibility_radius = 120  # Drop back down to a dark window

def check_collisions(player_rect):
    """
    Evaluates cross-intersections between the submarine and active lists. 
    Triggers state changes or updates tracking metrics based on contact rules.
    """
    global oxygen, game_state, is_sonar_active, sonar_timer, visibility_radius

    # 1. Check Glacier Wall Collision (Immediate Damage/Failure)
    for wall in walls:
        if player_rect.colliderect(wall):
            game_state = "GAME_OVER"

    # 2. Check Oxygen Canister Collection
    for air in air_canisters:
        if player_rect.colliderect(air):
            oxygen = min(100.0, oxygen + 25.0)  # Caps at 100% capacity maximum boundary
            air_canisters.remove(air)

    # 3. Check Sonar Pickups (Power-up Modifier)
    for sonar in sonar_pickups:
        if player_rect.colliderect(sonar):
            is_sonar_active = True
            sonar_timer = time.time() + 6.0  # Power-up behavior changes game for 6 seconds
            visibility_radius = 800         # Illuminates the entire trench area
            sonar_pickups.remove(sonar)  







screen.fill(BLUE)



