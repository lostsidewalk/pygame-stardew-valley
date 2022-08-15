import pygame
from settings import *


class Overlay:
    def __init__(self, player):
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        # imports
        overlay_path = 'graphics/overlay/'
        self.tool_surfaces = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha()
                              for tool in player.tools}
        print('tool surfaces')
        print(self.tool_surfaces)
        self.seed_surfaces = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha()
                              for seed in player.seeds}
        print('seed surfaces')
        print(self.seed_surfaces)

    def display(self):
        # tool
        tool_surface = self.tool_surfaces[self.player.selected_tool]
        tool_rect = tool_surface.get_rect(midbottom=OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surface, tool_rect)

        # seed
        seed_surface = self.seed_surfaces[self.player.selected_seed]
        seed_rect = seed_surface.get_rect(midbottom=OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surface, seed_rect)
