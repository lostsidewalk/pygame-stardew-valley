import pygame
from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)

        self.image = pygame.Surface((32, 64))
        self.image.fill('green')
        self.rect = self.image.get_rect(center=pos)

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            print('up')
        elif keys[pygame.K_DOWN]:
            print('down')
        elif keys[pygame.K_RIGHT]:
            print('right')
        elif keys[pygame.K_LEFT]:
            print('left')

    def update(self, dt):
        self.input()
