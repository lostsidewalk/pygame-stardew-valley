import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree
from pytmx.util_pygame import load_pygame
from support import import_folder

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()  # screen

        self.all_sprites = CameraGroup()  # sprite groups

        self.setup()

        self.overlay = Overlay(self.player)

    def setup(self):
        tmx_data = load_pygame('data/map.tmx')

        # house floor/furniture bottom
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:  # order is significant here
            for x, y, surface in tmx_data.get_layer_by_name(layer).tiles():
                Generic(pos=(x * TILE_SIZE, y * TILE_SIZE), surface=surface, groups=self.all_sprites,
                        z=LAYERS['house-bottom'])
        # house walls/furniture top
        for layer in ['HouseWalls', 'HouseFurnitureTop']:  # order is significant here
            for x, y, surface in tmx_data.get_layer_by_name(layer).tiles():
                Generic(pos=(x * TILE_SIZE, y * TILE_SIZE), surface=surface, groups=self.all_sprites)
        # fence
        for x, y, surface in tmx_data.get_layer_by_name('Fence').tiles():
            Generic(pos=(x * TILE_SIZE, y * TILE_SIZE), surface=surface, groups=self.all_sprites)
        # water
        for x, y, surface in tmx_data.get_layer_by_name('Water').tiles():
            Water(pos=(x * TILE_SIZE, y * TILE_SIZE), frames=import_folder('graphics/water'), groups=self.all_sprites)
        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, self.all_sprites, obj.name)
        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, self.all_sprites)

        # player
        self.player = Player((640, 360), self.all_sprites)  # move to __init__

        Generic(
            pos=(0, 0),
            surface=pygame.image.load('graphics/world/ground.png').convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground'])

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)
        self.overlay.display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        for layer in LAYERS.values():
            for sprite in self.sprites():
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)