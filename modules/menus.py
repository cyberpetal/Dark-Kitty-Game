from .config import *
import pygame


class Button():
    def __init__(self, master, pos, action, button_list, text_color='white'):

        self.pos = pos
        self.action = action
        self.master = master
        self.screen = pygame.display.get_surface()
        self.text_color = text_color
        self.mouse_hover = False
        self.hover_sound_played = False


        self.image = self.master.font.render(action.upper(), False, self.text_color)
        self.rect = self.image.get_rect(center=pos)
        self.detection_rect = self.rect.inflate(10,10)

        self.underline = pygame.Surface((self.image.get_width(), 2))
        self.underline.fill(self.text_color)
        self.underline_rect = self.underline.get_rect(midtop=(self.rect.midbottom))

        self.shadow = self.master.font.render(action.upper(), False, (136, 8, 8))
        self.shadow.set_alpha(200)
        

        button_list.append(self)

    def interact(self, mouse_pos, click=False):

        if click and self.mouse_hover:
            # if self.action != "start":self.master.sound.dict["button_click"].play()
            return self.action
        self.mouse_hover = self.detection_rect.collidepoint(mouse_pos)
        if self.mouse_hover:
            if not self.hover_sound_played:
                self.hover_sound_played = True
                # self.master.sound.dict["button_hover"].play()
        else:self.hover_sound_played = False

    def draw(self):
        
        if not self.mouse_hover:
            self.screen.blit(self.shadow, (self.rect.left-3, self.rect.top+3))
        else:
            self.screen.blit(self.underline, self.underline_rect)

        self.screen.blit(self.image, self.rect)


class MainMenu():

    def __init__(self, master):
        self.master = master
        self.master.main_menu = self
        self.screen = pygame.display.get_surface()
        # self.mainmenu_bg = pygame.image.load("graphics/extra/cover.png").convert()
        # self.title_surf = self.master.font_big.render('Winter Wreck', False, 'white')
        # self.title_rect = self.title_surf.get_rect(midtop=(W/2, 40))
        # self.title_shadow = self.master.font_big.render('Winter Wreck', False, (136, 8, 8))
        # self.title_shadow.set_alpha(200)
        self.buttons:list[Button] = []
        self.create_buttons()
        
    def create_buttons(self):

        Button(self.master, (W//2, H*0.5), 'start', self.buttons)
        Button(self.master, (W//2, H*0.6), 'fullscreen', self.buttons)
        Button(self.master, (W//2, H*0.7), 'quit', self.buttons)

    def update(self):
        
        for event in pygame.event.get((pygame.MOUSEBUTTONDOWN)):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                for button in self.buttons:
                    action = button.interact(event.pos, click=True)
                    if action == 'start':
                        # self.master.music.change_track("in_game")
                        # self.master.sound.dict["start_button"].play()
                        self.master.app.state = self.master.app.IN_GAME
                    elif action == 'fullscreen':
                        pygame.display.toggle_fullscreen()
                    elif action == 'quit':
                        pygame.quit()
                        raise SystemExit
                    if action is not None:
                        return
    def draw(self):

        self.screen.fill((0, 0, 0))

        # self.screen.blit(self.mainmenu_bg, (0, 0))
        # self.screen.blit(self.title_shadow, (self.title_rect.x-3, self.title_rect.y+3))
        # self.screen.blit(self.title_surf, self.title_rect)

        for button in self.buttons:
            button.draw()
            button.interact(pygame.mouse.get_pos())

    def run(self):
        self.update()
        self.draw()


class PauseMenu():

    def __init__(self, master):
        self.master = master
        self.master.pause_menu = self

        self.screen = pygame.display.get_surface()
        self.bg = self.screen.copy()
        self.bg_overlay = pygame.Surface(self.screen.get_size())
        self.bg_overlay.fill((0,0,0))
        self.bg_overlay.set_alpha(192)

        self.buttons:list[Button] = []
        self.create_buttons()
        
    def create_buttons(self):

        Button(self.master, (W//2, H*0.4), 'resume', self.buttons)
        Button(self.master, (W//2, H*0.5), 'fullscreen', self.buttons)
        Button(self.master, (W//2, H*0.6), 'quit', self.buttons)

    def open(self):
        self.bg = self.screen.copy()
        # self.master.sound.dict["button_click"].play()

    def update(self):
        
        for event in pygame.event.get((pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.master.game.paused = False
                # self.master.sound.dict["button_click"].play()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                for button in self.buttons:
                    action = button.interact(event.pos, click=True)
                    if action == 'resume':
                        self.master.game.paused = False
                    elif action == 'fullscreen':
                        pygame.display.toggle_fullscreen()
                    elif action == 'quit':
                        pygame.quit()
                        raise SystemExit
                    if action is not None:
                        return
    def draw(self):

        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.bg_overlay, (0, 0))

        for button in self.buttons:
            button.draw()
            button.interact(pygame.mouse.get_pos())


class GameOverMenu():

    def __init__(self, master):
        self.master = master
        self.master.game_over_menu = self

        self.screen = pygame.display.get_surface()

        self.buttons:list[Button] = []
        self.create_buttons()
        
    def create_buttons(self):

        Button(self.master, (W//2, H*0.5), 'Main Menu', self.buttons)

    def open(self, death_msg):

        self.master.app.state = self.master.app.GAME_OVER

        self.title_surf = self.master.font_big.render(death_msg, False, 'white')
        self.title_rect = self.title_surf.get_rect(midtop=(W/2, 40))
        self.title_shadow = self.master.font_big.render(death_msg, False, (136, 8, 8))
        self.title_shadow.set_alpha(200)
        # self.master.sound.dict["button_click"].play()

    def update(self):
        
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                for button in self.buttons:
                    action = button.interact(event.pos, click=True)
                    if action == 'Main Menu':
                        self.master.app.state = self.master.app.MAIN_MENU
                        self.master.game.reset_game()
    def draw(self):

        self.screen.fill((0, 0, 0)) 

        self.screen.blit(self.title_shadow, (self.title_rect.x-3, self.title_rect.y+3))
        self.screen.blit(self.title_surf, self.title_rect)

        for button in self.buttons:
            button.draw()
            button.interact(pygame.mouse.get_pos())

    def run(self):
        self.update()
        self.draw()