import pygame
from .engine import *
from .config import *

class IntroSceneFiFo:
    "fade-in fade-out cutscene"

    def __init__(self, master) -> None:

        self.master = master
        self.screen = pygame.display.get_surface()

        self.scenes = load_pngs("graphics/cutscene")
        self.current_scene = self.scenes[0]
        self.scene_index = 0
        self.alpha = 0
        self.skip = False

        self.increment = 1
        self.alpha_speed = 8

        self.flash_looping = 0
        self.flash_speed = 0.15

        self.bottom_text = self.master.font.render("Press Space to Continue", False, (255, 255, 255))
        self.bottom_text_rect = self.bottom_text.get_rect(midtop=(W//2, 10))
        self.skip_text = self.master.font_small.render('ESCAPE to skip', False, 'white')
        self.skip_shadow = self.master.font_small.render('ESCAPE to skip', False, 'black')
        self.skip_rect = self.skip_text.get_rect(topleft=(5, 5))

        # self.STAY_TIMER = pygame.event.custom_type()
        # self.EVENTS = (self.STAY_TIMER)
        self.EVENTS = (pygame.KEYDOWN)

    def check_events(self):

        for event in pygame.event.get(self.EVENTS):
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE:
                    self.increment = -1
                
                elif event.key == pygame.K_ESCAPE:
                    self.increment = -1
                    self.skip = True

    def draw(self):
        
        self.screen.fill(0x0)
        self.screen.blit(self.current_scene, (0, 0))
        if self.increment == 0:
            self.screen.blit(self.bottom_text, self.bottom_text_rect)
            self.screen.blit(self.skip_shadow, (self.skip_rect.x-2, self.skip_rect.y+2))
            self.screen.blit(self.skip_text, self.skip_rect)

    def update(self):

        try:
            self.current_scene = self.scenes[int(self.scene_index)]
        except IndexError: return True
        self.current_scene.set_alpha(int(self.alpha))

        self.alpha += self.alpha_speed*self.increment *self.master.dt

        if self.alpha >= 256:
            self.increment = 0
            self.alpha = 255
            # pygame.time.set_timer(self.STAY_TIMER, 500, loops=1)
        elif self.alpha < 0:
            if self.skip: return True
            self.alpha = 0
            self.increment = 1
            self.scene_index += 1

    def run(self):

        self.check_events()
        result = self.update()
        self.draw()
        return result
