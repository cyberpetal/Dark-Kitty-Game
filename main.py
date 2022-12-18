import pygame
from modules import *

class Master:
    
    def __init__(self) -> None:

        self.font = pygame.font.SysFont("Ariel", 22)
        self.font_big = pygame.font.SysFont("Ariel", 32)

        self.app:App
        self.dt:float
        self.offset:pygame.Vector2

class App:

    MAIN_MENU = 1
    IN_GAME = 2

    def __init__(self) -> None:

        pygame.init()
        
        #window
        self.screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        # pygame.display.set_caption("DarkKittyGame")
        # pygame.display.set_icon(pygame.image.load("graphics/abc/icon.png").convert_alpha())

        self.state = self.MAIN_MENU
        #init
        self.master = Master()
        self.master.app = self

        SoundSet(self.master)
        # self.music = Music(self.master)

        self.game = Game(self.master)
        self.main_menu = MainMenu(self.master)

        self.EVENT_CLEAR_TIMER = pygame.event.custom_type()
        pygame.time.set_timer(self.EVENT_CLEAR_TIMER, 30_000)


    def process_events(self):

        for event in pygame.event.get((pygame.QUIT, self.EVENT_CLEAR_TIMER)):
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == self.EVENT_CLEAR_TIMER:
                pygame.event.clear()
                break

    def run_app(self):

        # self.music.run()

        if self.state == self.MAIN_MENU:
            self.main_menu.run()
        if self.state == self.IN_GAME:
            self.game.run()


    def run(self):

        while True:
            
            pygame.display.update()
            self.master.dt = self.clock.tick(FPS) / 16.667
            if self.master.dt > 12: self.master.dt = 12
            if not self.master.game.paused: self.master.debug("FPS: ", round(self.clock.get_fps(), 2))
            self.process_events()
            self.run_app()
            pygame.event.pump()


if __name__ == "__main__":

    app = App()
    app.run()