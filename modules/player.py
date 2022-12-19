import pygame
from .frect import FRect
from .entity import Entity
from .engine import *
import os

class Player(Entity):

    def __init__(self, master, grps):

        super().__init__(grps)
        self.master = master
        master.player = self
        self.screen = pygame.display.get_surface()

        self.start_pos = 300, 150
        self.hitbox= FRect(*self.start_pos, 24, 12)
        self.sprite_box = FRect(0, 0, 28, 64)

        self.animations = {}
        self.load_animations()

        self.image = self.animations["walk_right"][0]
        self.rect = self.image.get_rect(midbottom=(self.hitbox.midbottom))

        self.anim_index = 0
        self.anim_speed = 0.15

        self.direction = pygame.Vector2(1, 0)
        self.input_direc = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 0.2
        self.deceleration = 0.3
        self.max_speed = 2.2
        self.moving = False

        self.attention_level = 50
        self.dead = False
        self.got_attention = False

        self.EVENTS = (pygame.KEYDOWN)

    def load_animations(self):
        
        self.animations.update(import_sprite_sheets("graphics/player"))

    def get_input_and_events(self):
        
        self.input_direc.update(0, 0)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.input_direc.y += 1
        if keys[pygame.K_w]:
            self.input_direc.y -= 1
        if keys[pygame.K_d]:
            self.input_direc.x += 1
        if keys[pygame.K_a]:
            self.input_direc.x -= 1
        
        if self.input_direc.x and self.input_direc.y:
            self.input_direc.normalize_ip()
        if self.input_direc.x or self.input_direc.y:
            self.moving = True
            self.direction.update(self.input_direc)
        else: self.moving = False

        for event in pygame.event.get(self.EVENTS):

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.master.game.pause_game()
                if event.key == pygame.K_F2:
                    index = 0
                    while True:
                        name = f"screenshots/{index:04d}.png"
                        if not os.path.exists(name):
                            pygame.image.save(self.screen, name)
                            break
                        index += 1

    def move(self):

        if self.moving:
            self.velocity.move_towards_ip(self.direction * self.max_speed , self.acceleration)
        else: self.velocity.move_towards_ip((0, 0), self.deceleration)

        # try: self.velocity.clamp_magnitude_ip(0, self.max_speed)
        # except ValueError: pass

        self.hitbox.centerx += self.velocity.x * self.master.dt
        self.check_bounds_collision(0, self.master.game.bounds)
        self.hitbox.bottom += self.velocity.y * self.master.dt
        self.check_bounds_collision(1, self.master.game.bounds)

        self.sprite_box.midbottom = self.hitbox.midbottom

    def update_image(self):

        state = "walk"

        if self.direction.x > 0:
            orientation = "_right"
        elif self.direction.x < 0:
            orientation = "_left"
        elif self.direction.y > 0:
            orientation = "_down"
        elif self.direction.y < 0:
            orientation = "_up"

        if not self.moving: self.anim_index = 0

        try:
            image = self.animations[state+orientation][int(self.anim_index)]
        except IndexError:
            image = self.animations[state+orientation][0]
            self.anim_index = 0

        if self.moving: self.anim_index += self.anim_speed * self.master.dt

        self.image = image

        self.rect.midbottom = self.hitbox.midbottom

    def check_death(self):

        if self.dead: return

        if self.attention_level <= 0:
            self.dead = True
            self.master.game_over_menu.open("You Couldn't Survive Without Attention")
        elif self.attention_level >= 100:
            self.dead = True
            self.master.game_over_menu.open("You Got Overwhelmed with Attention")

    def draw(self):
        
        self.screen.blit(self.image, self.rect.topleft+self.master.offset)

    def update(self):

        self.check_death()
        self.get_input_and_events()
        self.move()
        self.update_image()
        if not self.got_attention: self.attention_level -= 0.03*self.master.dt
        self.master.debug("pos: ", self.rect.center)
        self.master.debug("velocity: ", self.velocity)
        self.master.debug("attention: ", self.attention_level)
        self.master.debug("got attention: ", self.got_attention)
        self.got_attention = False