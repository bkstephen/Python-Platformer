import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

from gameutils import Player, Level

pygame.init()
pygame.display.set_caption("Ninja Judy")

FPS = 60

def main(window):
    clock = pygame.time.Clock()
    level = Level()

    block_size = 96
    # floor
    for i in range(-Level.WIDTH // block_size, Level.WIDTH * 2 // block_size):
        level.add_terain_block(i * block_size, Level.HEIGHT - block_size, block_size)
    
    level.add_terain_block(0, Level.HEIGHT - block_size * 2, block_size)
    level.add_terain_block(block_size * 3, Level.HEIGHT - block_size * 4, block_size)

    background, bg_image = level.get_background("Blue.png")

    player = Player(100, 100, 50, 50)

    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break            
        
        player.loop(FPS)
        level.handle_move(player)

        level.draw(window, background, bg_image, player)

        #scrolling background
        if (((player.rect.right - level.offset_x >= Level.WIDTH - level.scroll_area_width) and player.x_vel > 0) 
            or ((player.rect.left - level.offset_x <= level.scroll_area_width) and player.x_vel < 0) ):
            level.offset_x += player.x_vel

    pygame.quit()
    quit()
    
if __name__ == '__main__':
    window = pygame.display.set_mode((Level.WIDTH, Level.HEIGHT))
    main(window)