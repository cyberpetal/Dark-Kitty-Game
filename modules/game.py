import pygame
from .menus import PauseMenu
from .config import *
from .engine import *
from .debug import Debug
from .player import Player


class Game:

    def __init__(self, master) -> None:
        
        self.master = master
        master.game = self

        self.screen = pygame.display.get_surface()

        self.master.offset = pygame.Vector2(0, 0)

        self.pause_menu = PauseMenu(master)
        self.debug = Debug()
        master.debug = self.debug

        self.ysort_grp = CustomGroup()

        self.player = Player(self.master, self.ysort_grp)

        self.bounds = []
        self.paused = False

    def update_offset(self):

        # self.offset =  (self.master.player.hitbox.center - pygame.Vector2(W/2, H/2)) * -1
        camera_rigidness = 0.18 if self.master.player.moving else 0.05
        # if self.master.player.dashing: camera_rigidness = 0.22
        self.master.offset -= (self.master.offset + (self.master.player.hitbox.center - pygame.Vector2(W/2, H/2))) * camera_rigidness * self.master.dt


    def pause_game(self):

        if not self.paused:
            self.paused = True
            self.pause_menu.open()

    def draw(self):

        self.screen.fill(0xd0d0d0)

        self.ysort_grp.draw_y_sort(key=lambda sprite: sprite.hitbox.bottom)

        self.debug.draw()

    def process_events(self):
        pass

    def run_pause_menu(self):
        self.pause_menu.update()
        self.pause_menu.draw()

    def update(self):
        
        self.player.update()
        # self.update_offset()

    def run(self):

        if self.paused:
            self.run_pause_menu()
        else:
            self.process_events()
            self.update()
            self.draw()
