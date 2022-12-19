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

ROBOT_DIALOGUE = json.load(open("data/enemy/dialogue.json"))

ENEMY_SPRITES = {}

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

        # self.type = sprite_type
        self.start_pos = start_pos

        self.hitbox = FRect(*self.start_pos, 26, 12)
        self.sprite_box = FRect(0, 0, 28, 64)

        self.image = ENEMY_SPRITES['robot']
        self.rect = self.image.get_rect(midbottom=(self.hitbox.midbottom))

        self.state = State.FOLLOWING
        self.direction = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)
        self.max_speed = 0.8
        self.acceleration = 0.2
        self.moving = True
        self.facing_right = True
        self.dist_sq_to_player = 1_064

        self.max_health = 100
        self.health = self.max_health

        self.AWAKE = False # unattracted enemies
        self.target_robot:Enemy = None

        self.SAVE_TIMER = CustomTimer()
        self.CONSUFED_TIMER = CustomTimer()
        self.THINK_TIMER = CustomTimer()
        self.WANDER_TIMER = CustomTimer()
        self.INVINCIBILITY_TIMER = CustomTimer()

        self.WANDER_TIMER.start(3_000, 0)

        self.saving = False
        self.thinking = False
        self.invincible = False
        self.wander_target = (200, 300)

    def process_events(self):
        
        if self.SAVE_TIMER.check():

            self.target_robot.state = State.CONFUSED
            self.target_robot.CONSUFED_TIMER.start(random.randint(5, 15)*1000)
            self.target_robot = None
            self.saving = False
            self.state = State.WANDER
            self.THINK_TIMER.start(random.randint(5, 10)*1000)
            self.master.sound.dict[F"robot panic{random.randint(1, 3)}"].play()

        if self.CONSUFED_TIMER.check():

            self.state = State.FOLLOWING
            self.thinking = False

        if self.THINK_TIMER.check():

            self.thinking = False
            # self.state = State.WANDER

        if self.WANDER_TIMER.check():

            self.wander_target = random.randint(0, MAP_W), random.randint(0, MAP_H)

        if self.INVINCIBILITY_TIMER.check():
            self.invincible = False
            if self.health <= 0:
                self.kill()
                self.master.player.kill_count += 1

    def update_state(self):

        if not self.AWAKE and not self.thinking:
            if self.dist_sq_to_player < GIVE_ATTENTION_RADIUS**2:
                self.master.player.got_attention = True
                self.master.player.attention_level += 0.01 * self.master.dt
                if self.dist_sq_to_player < GIVE_ATTENTION_PLUS_RADIUS**2:
                    self.master.player.attention_level += 0.025 * self.master.dt
                    self.state = State.IDLE
                else: self.state = State.FOLLOWING
        elif self.target_robot is not None and not self.saving and self.state == State.FOLLOWING:
            if dist_sq(self.sprite_box.center, self.target_robot.sprite_box.center) < GIVE_ATTENTION_PLUS_RADIUS**2:
                self.saving = True
                self.state = State.SAVING
                self.SAVE_TIMER.start(5_000)
                self.thinking = True             
                self.target_robot.state = State.CONFUSED
                self.target_robot.thinking = True
                self.master.sound.dict[F"robot panic{random.randint(1, 3)}"].play()

    def move(self):

        target = self.master.player.sprite_box.center
        if self.AWAKE and not self.thinking:
            if self.target_robot is None:
                robot = random.choice(self.master.enemy_grp.sprites())
                if not(robot.AWAKE or robot.thinking):
                    self.state = State.FOLLOWING
                    self.target_robot = robot
            if self.target_robot is not None:
                target = self.target_robot.sprite_box.center
        if self.state == State.WANDER:
            target = self.wander_target

        if self.state in (State.FOLLOWING, State.WANDER) and not self.invincible:

            self.direction = (target + pygame.Vector2(0, 0) - self.sprite_box.center).normalize()
            self.velocity .move_towards_ip(self.direction * self.max_speed, self.acceleration)
            
            for enemy in self.master.enemy_grp.sprites():
                if enemy == self: continue
                if self.hitbox.colliderect(enemy.hitbox):
                    try:
                        self.velocity += 0.25 * (self.hitbox.center + pygame.Vector2(0, 0) - enemy.hitbox.center).normalize()
                    except ValueError: pass

            self.facing_right = self.velocity.x >= 0

        elif self.state in (State.IDLE, State.CONFUSED, State.SAVING) or self.invincible:
            self.velocity.move_towards_ip((0, 0), 0.08)

        self.hitbox.centerx += self.velocity.x * self.master.dt
        self.check_bounds_collision(0, self.master.game.bounds)
        self.hitbox.bottom += self.velocity.y * self.master.dt
        self.check_bounds_collision(1, self.master.game.bounds)

        self.sprite_box.centerx = self.hitbox.centerx
        self.sprite_box.bottom = self.hitbox.bottom

        self.dist_sq_to_player = dist_sq(self.master.player.sprite_box.center, self.sprite_box.center)
        
    def update_image(self):

        state = "robot"
        if self.AWAKE: state += "_awake"
        elif self.thinking: state += "_confused"

        image = ENEMY_SPRITES[state].copy()

        if self.invincible:
            image.fill((255,255,255), special_flags=pygame.BLEND_RGB_MAX)

        self.image = pygame.transform.flip(image, not self.facing_right, False)
        self.rect.midbottom = self.hitbox.midbottom

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft+self.master.offset)

    def update(self):

        self.process_events()
        self.update_state()
        self.move()
        self.update_image()

        # if self.AWAKE:
        #     self.master.debug("thinking:", self.thinking)
        #     self.master.debug("saving:", self.saving)
        #     self.master.debug("State:", self.state)
        #     self.master.debug("target:", self.target_robot is not None)

class EnemyTextBox(pygame.sprite.Sprite):

    def __init__(self, master, grps, text_box, target, duration):

        super().__init__(grps)

        self.master = master
        self.screen = pygame.display.get_surface()
        
        self.text_box:pygame.Surface = text_box
        self.target = target
        self.rect = self.text_box.get_rect()

        self.DURATION_TIMER = CustomTimer()

        self.DURATION_TIMER.start(duration)

    def draw(self):

        self.screen.blit(self.text_box, self.rect)

    def update(self):

        if self.DURATION_TIMER.check() or not self.target.alive():
            self.kill()
            return
        self.rect.midbottom = self.target.rect.midtop + self.master.offset + (0, 0)
        


class EnemyHandler:

    def __init__(self, master):

        self.master = master
        master.enemy_handler = self

        self.screen = pygame.display.get_surface()

        self.enemy_grp = CustomGroup()
        master.enemy_grp = self.enemy_grp
        self.enemy_text_boxes = CustomGroup()
        self.SPAWN_TEXT_BOXES = CustomTimer()

        self.SPAWN_TIMER = CustomTimer()

        self.SPAWN_TIMER.start(3_000, loops=0)

        ENEMY_SPRITES.update(load_pngs_dict("graphics/enemies"))

        self.SPAWN_TEXT_BOXES.start(2_000)

        self.grps_for_enemies = (self.enemy_grp, master.game.ysort_grp)

        # Enemy(master, self.grps_for_enemies, (50, 250), "robot")
        # Enemy(master, self.grps_for_enemies, (250, 100), "robot")
        # hoard = Enemy(master, self.grps_for_enemies, (200, 120), "awake_robot")
        # hoard.AWAKE = True

    def spawn_text_boxes(self):

        if self.SPAWN_TIMER.check() and len(self.enemy_grp) < 58:

            if self.master.player.kill_count <= 10: count = 3
            elif self.master.player.kill_count <= 15: count = 4
            elif self.master.player.kill_count <= 50: count = 4
            elif self.master.player.kill_count <= 80: count = 5
            elif self.master.player.kill_count <= 100: count = 5
            elif self.master.player.kill_count <= 130: count = 6

            while True:

                pos = random.randint(0, MAP_W), random.randint(0, MAP_H)
                rect = pygame.Rect(-self.master.offset.x, -self.master.offset.y, W, H)
                if rect.collidepoint(pos): continue
                for rect in self.master.game.bounds:
                    if rect.collidepoint(pos):
                        continue
                break

            for _ in range(count):
                Enemy(self.master, self.grps_for_enemies, pos, "robot")
        
        if self.SPAWN_TEXT_BOXES.check():

            self.SPAWN_TEXT_BOXES.start(random.randint(20, 40)*100)
            if self.enemy_grp.sprites():
                enemy = random.choice(self.enemy_grp.sprites())

                if enemy.AWAKE and \
                    enemy.state in (State.SAVING, State.WANDER, State.FOLLOWING):
                        texts = ROBOT_DIALOGUE["AWAKE"][enemy.state.name]
                elif enemy.state in (State.FOLLOWING, State.CONFUSED, State.IDLE):
                        texts = ROBOT_DIALOGUE["ZOMBIE"][enemy.state.name]

                text = random.choice(texts)
                text_box = self.master.text_box.get_text_box(text)
                EnemyTextBox(self.master, [self.enemy_text_boxes], text_box, enemy, 3_000)

    def draw(self):

        self.enemy_text_boxes.draw()

    def update(self):

        self.spawn_text_boxes()
        self.enemy_grp.update()
        self.enemy_text_boxes.update()

