import pygame, sys
from settings import *
from level import Level
from game_data import level_map

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
level = Level(level_map, screen)
background = pygame.image.load("Assets\Background.png")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.blit(background,(0,0))
    level.run()

    pygame.display.update()
    clock.tick(60)