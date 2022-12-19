import pygame
from modules import *

class Master:
    
    def __init__(self) -> None:

        self.font = pygame.font.SysFont("Ariel", 32)
        self.font_small = pygame.font.SysFont("Ariel", 20)
        self.font_big = pygame.font.SysFont("Ariel", 42)
        self.fire_font = pygame.font.Font("fonts/chp-fire.ttf", 32)

        self.app:App
        self.dt:float
        self.offset:pygame.Vector2

class App:

    MAIN_MENU = 1
    IN_GAME = 2
    GAME_OVER = 3
    CUTSCENE = 4

    def __init__(self) -> None:

        pygame.init()
        
        #window
        self.screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("The Blood Cat")
        pygame.display.set_icon(pygame.image.load("graphics/icon.png").convert_alpha())

        self.state = self.MAIN_MENU
        #init
        self.master = Master()
        self.master.app = self

        SoundSet(self.master)
        self.music = Music(self.master)

        self.game = Game(self.master)
        self.main_menu = MainMenu(self.master)

        self.game_over_menu = GameOverMenu(self.master)

        self.intro = IntroSceneFiFo(self.master)

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

        self.music.run()

        if self.state == self.MAIN_MENU:
            self.main_menu.run()
        elif self.state == self.IN_GAME:
            self.game.run()
        elif self.state == self.GAME_OVER:
            self.game_over_menu.run()
        elif self.state == self.CUTSCENE:
            if self.intro.run():
                self.state = self.IN_GAME


    def run(self):

        while True:
            
            pygame.display.update()
            self.master.dt = self.clock.tick_busy_loop(FPS) / 16.667
            if self.master.dt > 6: self.master.dt = 6
            if not self.master.game.paused: self.master.debug("FPS: ", round(self.clock.get_fps(), 2))
            self.process_events()
            self.run_app()
            pygame.event.pump()


if __name__ == "__main__":

    app = App()
    app.run()