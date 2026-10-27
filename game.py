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


screen.fill(BLUE)
