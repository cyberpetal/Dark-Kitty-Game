import pygame
from .frect import FRect
from .entity import Entity
import os

class Player(Entity):

    def __init__(self, master, grps):

        super().__init__(grps)
        self.master = master
        master.player = self
        self.screen = pygame.display.get_surface()

        self.start_pos = 300, 150
        self.hitbox= FRect(*self.start_pos, 12, 9)
        self.sprite_box = FRect(0, 0, 8, 30)

        self.original_image = pygame.image.load("graphics/test/player.png").convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(midbottom=(self.hitbox.midbottom))

        self.direction = pygame.Vector2(1, 0)
        self.input_direc = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 0.4
        self.deceleration = 0.3
        self.max_speed = 2.2
        self.moving = False
        self.facing_right = True

        self.attention_level = 500

        self.EVENTS = (pygame.KEYDOWN)

    def update_image(self):

        self.image = pygame.transform.flip(self.original_image, not self.facing_right, False)

        self.rect.midbottom = self.hitbox.midbottom

    def get_input_and_events(self):
        
        self.input_direc.update(0, 0)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.input_direc.y += 1
        if keys[pygame.K_w]:
            self.input_direc.y -= 1
        if keys[pygame.K_d]:
            self.input_direc.x += 1
            self.facing_right = True
        if keys[pygame.K_a]:
            self.input_direc.x -= 1
            self.facing_right = False
        
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
            self.velocity.move_towards_ip(self.direction * self.max_speed , self.acceleration  * self.master.dt)
        else: self.velocity.move_towards_ip((0, 0), self.deceleration*self.master.dt)

        # try: self.velocity.clamp_magnitude_ip(0, self.max_speed)
        # except ValueError: pass

        self.hitbox.centerx += self.velocity.x * self.master.dt
        self.check_bounds_collision(0, self.master.game.bounds)
        self.hitbox.bottom += self.velocity.y * self.master.dt
        self.check_bounds_collision(1, self.master.game.bounds)

        self.sprite_box.midbottom = self.hitbox.midbottom

    def draw(self):
        
        self.screen.blit(self.image, self.rect.topleft+self.master.offset)

    def update(self):

        self.get_input_and_events()
        self.move()
        self.update_image()
        self.attention_level -= 0.06*self.master.dt
        self.master.debug("pos: ", self.rect.center)
        self.master.debug("velocity: ", self.velocity)
        self.master.debug("attention: ", self.attention_level)