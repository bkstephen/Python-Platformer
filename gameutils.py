import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    PLAYER_VEL = 5
    GRAVITY = 1.5
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width, height) -> None:
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = 'left'
        self.animation_count = 0
        self.falling_count = 0
        self.SPRITES = Level().load_sprite_sheets('MainCharacters', 'NinjaFrog', 32, 32, True)
        self.jump_count = 0
    
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != 'left':
            self.direction = 'left'
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != 'right':
            self.direction = 'right'
            self.animation_count = 0
    
    def loop(self, fps):
        self.y_vel += min(1, (self.falling_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.falling_count += 1
        self.update_sprite()

    def draw(self, window: pygame.image, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        
    def landed(self):
        self.falling_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1
        
    def update_sprite(self):
        sprite_sheet = 'idle'
        
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = 'double_jump'
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = 'fall'
        elif self.x_vel != 0:
            sprite_sheet = 'run'

        sprite_sheet_name = f'{sprite_sheet}_{self.direction}'
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

class Level:
    WIDTH, HEIGHT = 1000, 800

    def __init__(self) -> None:
        self.terrain = []
        self.scroll_area_width = 200
        self.offset_x = 0

    def handle_vertical_collision(self, player: Player):
        collidect_objects = []
        for object in self.terrain:
            if pygame.sprite.collide_mask(player, object):
                if player.y_vel > 0:
                    player.rect.bottom = object.rect.top
                    player.landed()
                elif player.y_vel < 0:
                    player.rect.top = object.rect.bottom
                    player.hit_head()
            collidect_objects.append(object)
        return collidect_objects

    def handle_move(self, player: Player):
        keys = pygame.key.get_pressed()

        player.x_vel = 0
        if keys[pygame.K_LEFT]:
            player.move_left(player.PLAYER_VEL)
        if keys[pygame.K_RIGHT]:
            player.move_right(player.PLAYER_VEL)        
        if keys[pygame.K_SPACE] and player.jump_count < 2:
            player.jump()

        self.handle_vertical_collision(player)

    def get_background(self, name: str):
        image = pygame.image.load(join('assets', 'Background', name))
        _, _, width, height = image.get_rect()

        # To fill the background with tiles of a type you need to calculate how many you need 
        tiles = []
        for i in range(self.WIDTH //  width + 1):
            for j in range(self.HEIGHT // height + 1):
                # draw from right to left
                pos = [i * width, j * height]
                tiles.append(pos)

        return tiles, image
    
    def draw(self, window: pygame.image, background: list, bg_image, player: Player):
        for tile in background:
            window.blit(bg_image, tile)
        
        for obj in self.terrain:
            obj.draw(window, self.offset_x)

        player.draw(window, self.offset_x)
        pygame.display.update()

    def flip(self, sprites: list) -> list:
        return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

    def load_sprite_sheets(self, dir_1, dir_2, width, height, direction=False) -> dict:
        path = join('assets', dir_1, dir_2)
        images = [f for f in listdir(path) if isfile(join(path, f))]

        all_sprites = {}
        for image in images:
            sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

            sprites = []
            for i in range(sprite_sheet.get_width() // width):
                surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
                rect = pygame.Rect(i * width, 0, width, height)
                surface.blit(sprite_sheet, (0,0), rect)
                sprites.append(pygame.transform.scale2x(surface))
            
            if direction:
                all_sprites[image.replace('.png', '') + '_right'] = sprites
                all_sprites[image.replace('.png', '') + '_left'] = self.flip(sprites)
            else:
                all_sprites[image.replace('.png', '')] = sprites
        print(all_sprites)
        return all_sprites
    
    def add_terain_block(self, x, y, size, img_coord_x = 96, img_coord_y = 0, terrain_pic = 'Terrain.png'):
        self.terrain.append(Block(x, y, size, img_coord_x, img_coord_y, terrain_pic))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None) -> None:
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window: pygame.image, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size, img_coord_x, img_coord_y, terrain_pic) -> None:
        super().__init__(x, y, size, size)
        block = self.load_block(size, img_coord_x, img_coord_y, terrain_pic)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)
    
    def load_block(self, size, img_coord_x, img_coord_y, terrain_pic):
        path = join('assets', 'Terrain', terrain_pic)
        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        rect = pygame.Rect(img_coord_x, img_coord_y, size, size)
        surface.blit(image, (0, 0), rect)
        return pygame.transform.scale2x(surface)

    