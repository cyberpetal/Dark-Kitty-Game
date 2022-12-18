import pygame
from .config import *
from .engine import *
from .entity import Entity
from .frect import FRect
import random
import json
from enum import Enum

GIVE_ATTENTION_RADIUS = 96
GIVE_ATTENTION_PLUS_RADIUS = 32

class State(Enum):

    IDLE = 0
    FOLLOWING = 1
    WANDER = 2
    CONFUSED = 3
    SAVING = 4

class Enemy(Entity):

    def __init__(self, master, grps, start_pos, sprite_type):

        super().__init__(grps)
        self.master = master
        self.screen = pygame.display.get_surface()

        self.type = sprite_type
        self.start_pos = start_pos

        self.hitbox = FRect(*self.start_pos, 12, 9)
        self.sprite_box = FRect(0, 0, 8, 30)

        self.original_image = pygame.image.load(F"graphics/test/{sprite_type}.png").convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(midbottom=(self.hitbox.midbottom))

        self.state = State.FOLLOWING
        self.direction = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)
        self.max_speed = 0.8
        self.acceleration = 0.2
        self.moving = True
        self.facing_right = True
        self.dist_sq_to_player = 600

        self.max_health = 100
        self.health = self.max_health

        self.AWAKE = False # unattracted enemies
        self.target_robot:Enemy = None

        self.SAVE_TIMER = CustomTimer()
        self.CONSUFED_TIMER = CustomTimer()
        self.THINK_TIMER = CustomTimer()
        self.WANDER_TIMER = CustomTimer()

        self.WANDER_TIMER.start(3_000, 0)

        self.saving = False
        self.thinking = False
        self.wander_target = (200, 300)

    def process_events(self):
        
        if self.SAVE_TIMER.check():

            self.target_robot.state = State.CONFUSED
            self.target_robot.CONSUFED_TIMER.start(random.randint(5, 15)*1000)
            self.target_robot = None
            self.saving = False
            self.state = State.WANDER
            self.THINK_TIMER.start(random.randint(5, 10)*1000)

        if self.CONSUFED_TIMER.check():

            self.state = State.FOLLOWING
            self.thinking = False

        if self.THINK_TIMER.check():

            self.thinking = False
            # self.state = State.WANDER

        if self.WANDER_TIMER.check():

            self.wander_target = random.randint(0, MAP_W), random.randint(0, MAP_H)

    def update_image(self):

        # if self.hurting:
        #     self.image.fill((255,255,255), special_flags=pygame.BLEND_RGB_MAX)
        flip = self.velocity.x < 0
        self.image = pygame.transform.flip(self.original_image, flip, False)
        self.rect.midbottom = self.hitbox.midbottom

    def update_state(self):

        if not self.AWAKE and not self.thinking:
            if self.dist_sq_to_player < GIVE_ATTENTION_RADIUS**2:
                self.master.player.attention_level += 0.01 * self.master.dt
                if self.dist_sq_to_player < GIVE_ATTENTION_PLUS_RADIUS**2:
                    self.master.player.attention_level += 0.1 * self.master.dt
                    self.state = State.IDLE
                else: self.state = State.FOLLOWING
        elif self.target_robot is not None and not self.saving and self.state == State.FOLLOWING:
            if dist_sq(self.sprite_box.center, self.target_robot.sprite_box.center) < GIVE_ATTENTION_PLUS_RADIUS**2:
                self.saving = True
                self.state = State.IDLE
                self.SAVE_TIMER.start(5_000)
                self.thinking = True             
                self.target_robot.state = State.IDLE
                self.target_robot.thinking = True

    def move(self):

        target = self.master.player.sprite_box.center
        if self.AWAKE and not self.thinking:
            if self.target_robot is None:
                for _ in range(5):
                    self.target_robot = random.choice(self.master.enemy_grp.sprites())
                    if self.target_robot.AWAKE or self.target_robot.thinking: continue
                    self.state = State.FOLLOWING
                    break
                
            target = self.target_robot.sprite_box.center
        if self.state == State.WANDER:
            target = self.wander_target

        if self.state in (State.FOLLOWING, State.WANDER):
                self.direction = (target + pygame.Vector2(0, 0) - self.sprite_box.center).normalize()
                self.velocity .move_towards_ip(self.direction * self.max_speed, self.acceleration)

        elif self.state in (State.IDLE, State.CONFUSED, State.SAVING):
            self.velocity.move_towards_ip((0, 0), 0.05*self.master.dt)

        for enemy in self.master.enemy_grp.sprites():
            if enemy == self: continue
            if self.sprite_box.colliderect(enemy.sprite_box):
                try:
                    self.velocity += 0.6 * (self.sprite_box.center + pygame.Vector2(0, 0) - enemy.sprite_box.center).normalize()
                except ValueError: pass

        self.hitbox.centerx += self.velocity.x * self.master.dt
        self.check_bounds_collision(0, self.master.game.bounds)
        self.hitbox.bottom += self.velocity.y * self.master.dt
        self.check_bounds_collision(1, self.master.game.bounds)

        self.sprite_box.centerx = self.hitbox.centerx
        self.sprite_box.bottom = self.hitbox.bottom

        self.dist_sq_to_player = dist_sq(self.master.player.sprite_box.center, self.sprite_box.center)
        
    def draw(self):

        self.screen.blit(self.image, self.rect.topleft+self.master.offset)

    def update(self):

        self.process_events()
        self.update_state()
        self.move()
        self.update_image()

        if self.AWAKE:
            self.master.debug("State:", self.state)
            self.master.debug("saving:", self.saving)
            self.master.debug("thinking:", self.thinking)
            self.master.debug("target:", self.target_robot is not None)


class EnemyHandler:

    def __init__(self, master):

        self.master = master
        master.enemy_handler = self

        self.screen = pygame.display.get_surface()

        self.enemy_grp = CustomGroup()
        master.enemy_grp = self.enemy_grp

        self.grps_for_enemies = (self.enemy_grp, master.game.ysort_grp)

        Enemy(master, self.grps_for_enemies, (50, 250), "robot")
        Enemy(master, self.grps_for_enemies, (250, 100), "robot")
        hoard = Enemy(master, self.grps_for_enemies, (200, 120), "awake_robot")
        hoard.AWAKE = True

    def update(self):

        self.enemy_grp.update()

