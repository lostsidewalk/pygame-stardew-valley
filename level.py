import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction
from pytmx.util_pygame import load_pygame
from support import import_folder


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()  # screen

        self.all_sprites = CameraGroup()  # sprite groups

        self.collision_sprites = pygame.sprite.Group()  # contains all 'collidable' sprites

        self.interaction_sprites = pygame.sprite.Group()

        self.tree_sprites = pygame.sprite.Group()  # contains all trees

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
            Generic(pos=(x * TILE_SIZE, y * TILE_SIZE), surface=surface, groups=[self.all_sprites, self.collision_sprites])
        # water
        for x, y, surface in tmx_data.get_layer_by_name('Water').tiles():
            Water(pos=(x * TILE_SIZE, y * TILE_SIZE), frames=import_folder('graphics/water'), groups=self.all_sprites)
        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites, self.tree_sprites], obj.name, self.player_add)
        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
        # collision tiles
        for x, y, surface in tmx_data.get_layer_by_name('Collision').tiles():
            Generic(pos=(x * TILE_SIZE, y * TILE_SIZE), surface=pygame.Surface((TILE_SIZE, TILE_SIZE)), groups=self.collision_sprites)
        # player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.tree_sprites, self.interaction_sprites)
            elif obj.name == 'Bed':
                Interaction(
                    pos=(obj.x, obj.y),
                    size=(obj.width, obj.height),
                    groups=self.interaction_sprites,
                    name=obj.name
                )

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

    def player_add(self, item):
        self.player.item_inventory[item] += 1


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)

                    # if sprite == player:
                    #     pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSETS[player.status.split('_')[0]]
                    #     pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)
