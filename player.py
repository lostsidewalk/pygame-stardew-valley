import pygame
from settings import *
from support import *
from timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction_sprites, soil_layer):
        super().__init__(group)
        # import assets
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        # general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']
        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200
        # collision
        self.hitbox = self.rect.copy().inflate((-126, -70))  # shrink x by 126, shrink y by 70
        self.collision_sprites = collision_sprites
        # timers
        self.timers = {
            'tool-use': Timer(350, self.use_tool),  # call use_tool after 350 ms
            'tool-switch': Timer(200),
            'seed-use': Timer(350, self.use_seed),  # call use_seed after 350 ms
            'seed-switch': Timer(200),
        }
        # tool attributes
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        # seed attributes
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
        # inventory
        self.item_inventory = {
            'wood': 0,
            'apple': 0,
            'corn': 0,
            'tomato': 0
        }
        # interaction attributes
        self.tree_sprites = tree_sprites
        self.interaction_sprites = interaction_sprites
        self.sleep = False
        self.soil_layer = soil_layer

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSETS[self.status.split('_')[0]]

    def use_seed(self):
        self.soil_layer.plant_seed(self.target_pos, self.selected_seed)

    def import_assets(self):
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
            'up_hoe': [], 'down_hoe': [], 'left_hoe': [], 'right_hoe': [],
            'up_axe': [], 'down_axe': [], 'left_axe': [], 'right_axe': [],
            'up_water': [], 'down_water': [], 'left_water': [], 'right_water': [],
        }

        for animation in self.animations.keys():
            full_path = 'graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['tool-use'].active and not self.sleep:  # disable input when tool in use or player sleeping
            # directions
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0  # no vertical movement

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0  # no horizontal movement

            # tool use (space)
            if keys[pygame.K_SPACE]:
                self.timers.get('tool-use').activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # change tool ('q')
            if keys[pygame.K_q] and not self.timers['tool-switch'].active:
                self.timers['tool-switch'].activate()
                self.tool_index += 1
                if self.tool_index >= len(self.tools):
                    self.tool_index = 0
                self.selected_tool = self.tools[self.tool_index]

            # seed use (left ctrl)
            if keys[pygame.K_LCTRL]:
                self.timers.get('seed-use').activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # change seed ('e')
            if keys[pygame.K_e] and not self.timers['seed-switch'].active:
                self.timers['seed-switch'].activate()
                self.seed_index += 1
                if self.seed_index >= len(self.seeds):
                    self.seed_index = 0
                self.selected_seed = self.seeds[self.seed_index]

        if keys[pygame.K_RETURN]:
            collided_interaction_sprite = pygame.sprite.spritecollide(sprite=self, group=self.interaction_sprites,
                                                                      dokill=False)
            if collided_interaction_sprite:
                if collided_interaction_sprite[0].name == 'Trader':
                    pass
                elif collided_interaction_sprite[0].name == 'Bed':
                    self.status = 'left_idle'
                    self.sleep = True
                else:
                    pass

    def get_status(self):
        d = None
        # add '_idle' to status if no movement
        if self.direction.magnitude() == 0:
            d = self.status.split('_')[0]
            self.status = d + '_idle'

        if self.timers['tool-use'].active and d is not None:
            self.status = d + '_' + self.selected_tool

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:  # player is moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:  # player is moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction == 'vertical':
                        if self.direction.y > 0:  # player is moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:  # player is moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        # normalize
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        # horizontal
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        # vertical
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(dt)
        self.animate(dt)
