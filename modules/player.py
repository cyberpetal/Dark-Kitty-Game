import pygame
from .frect import FRect
from .entity import Entity
from .engine import *
from .config import *
from .enemy import State
from .particle import BloodParticle
import os
import random

ATTACK_SPRITES = {}
PARTICLES = {}

class Player(Entity):

    def __init__(self, master, grps):

        super().__init__(grps)
        self.master = master
        master.player = self
        self.screen = pygame.display.get_surface()

        self.start_pos = 420, 520
        self.hitbox= FRect(*self.start_pos, 24, 12)
        self.sprite_box = FRect(0, 0, 28, 64)

        self.animations = {}
        self.load_animations()

        self.image = self.animations["walk_right"][0]
        self.rect = self.image.get_rect(midbottom=(self.hitbox.midbottom))

        self.anim_index = 0

        self.direction = pygame.Vector2(1, 0)
        self.input_direc = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 0.4
        self.deceleration = 0.6
        self.max_speed = 2.2
        self.moving = False
        self.attacking = False

        self.attention_level = 80
        self.got_attention = False
        self.kill_count = 0
        self.dead = False

        self.weapon = Weapon(master)

        self.ATTACK_FOR = CustomTimer()

        self.EVENTS = (pygame.KEYDOWN)

    def load_animations(self):
        
        self.animations.update(import_sprite_sheets("graphics/player"))
        ATTACK_SPRITES.update(import_sprite_sheets("graphics/attacks"))

    def get_input_and_events(self):
        
        self.input_direc.update(0, 0)

        if not self.attacking:
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
                elif event.key == pygame.K_F2:
                    index = 0
                    while True:
                        name = f"screenshots/{index:04d}.png"
                        if not os.path.exists(name):
                            pygame.image.save(self.screen, name)
                            break
                        index += 1
                
                elif event.key == pygame.K_SPACE and not self.attacking:
                    self.attacking = True
                    self.can_attack = False
                    self.ATTACK_FOR.start(400)
                    self.anim_index = 0
                    self.weapon.attack('slash', 0.4)
                    self.master.sound.dict["saber swing"].play()
                elif event.key == pygame.K_LSHIFT and not self.attacking:
                    self.attacking = True
                    self.can_attack = False
                    self.ATTACK_FOR.start(800)
                    self.anim_index = 0
                    self.weapon.attack('scratch')
                    self.master.sound.dict[f"slash{random.randint(1, 3)}"].play()

    def process_timers(self):

        if self.ATTACK_FOR.check():
            self.weapon.stop_attack()
            self.attacking = False

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

        state = "attack" if self.attacking else "walk"

        if self.direction.x > 0:
            orientation = "_right"
        elif self.direction.x < 0:
            orientation = "_left"
        elif self.direction.y > 0:
            orientation = "_down"
        elif self.direction.y < 0:
            orientation = "_up"

        if not self.moving and not self.attacking: self.anim_index = 0

        try:
            image = self.animations[state+orientation][int(self.anim_index)]
        except IndexError:
            image = self.animations[state+orientation][0]
            self.anim_index = 0

        if self.moving: self.anim_index += 0.15 * self.master.dt
        if self.attacking:
            if self.anim_index > 1: self.anim_index = 1
            else: self.anim_index += 0.1 * self.master.dt


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
        self.process_timers()
        self.move()
        self.weapon.update()
        self.update_image()
        if not self.got_attention: self.attention_level -= 0.03*self.master.dt
        self.master.debug("pos: ", self.rect.center)
        self.master.debug("velocity: ", self.velocity)
        self.master.debug("attention: ", self.attention_level)
        self.master.debug("got attention: ", self.got_attention)
        self.master.debug("attacking: ", self.attacking)
        self.got_attention = False


class Weapon:

    def __init__(self, master):

        self.master = master
        self.player:Player = master.player
        self.screen = pygame.display.get_surface()
        self.active = False
        self.type = None
        PARTICLES.update(import_sprite_sheets("graphics/particles"))

    def attack(self, type, anim_speed=0.15):

        if self.active: return
        self.active = True
        self.type = type
        self.animation = ATTACK_SPRITES[type]
        self.image = self.animation[0]
        self.anim_index = 0
        self.anim_speed = anim_speed
        self.rect = self.image.get_rect(center = self.player.sprite_box.center)

    def stop_attack(self):
        self.active = False

    def update_image(self):

        try:
            self.image = self.animation[int(self.anim_index)]
        except IndexError:
            self.anim_index = 0
            self.image = self.animation[int(self.anim_index)]

        self.anim_index += self.anim_speed*self.master.dt

        if self.type == 'scratch':
            if self.player.direction.x > 0:
                self.rect.midleft = self.player.rect.midright
            elif self.player.direction.x < 0:
                self.rect.midright = self.player.rect.midleft
                self.image = pygame.transform.flip(self.image, True, False)
            elif self.player.direction.y < 0:
                self.rect.midbottom = self.player.rect.midtop
            elif self.player.direction.y > 0:
                self.rect.midtop = self.player.rect.midbottom
                self.image = pygame.transform.flip(self.image, True, True)
        else:
            if self.player.direction.x > 0:
                pass
            elif self.player.direction.x < 0:
                self.image = pygame.transform.flip(self.image, True, False)
            elif self.player.direction.y > 0:
                self.image = pygame.transform.flip(self.image, True, True)

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)

    def draw(self):

        if not self.active: return
        self.screen.blit(self.image, self.rect.topleft+self.master.offset)

    def update(self):

        if not self.active: return

        self.update_image()
        
        for enemy in self.master.enemy_grp.sprites():
            if not enemy.invincible and self.rect.colliderect(enemy.sprite_box):
                attack_mask = pygame.mask.from_surface(self.image)
                enemy_mask = pygame.mask.Mask(enemy.sprite_box.size, True)
                if attack_mask.overlap(enemy_mask, (enemy.sprite_box.x-self.rect.x, enemy.sprite_box.y-self.rect.y)):

                    if self.type == 'scratch':
                        enemy.health -= 5
                        if enemy.health <= 85:
                            enemy.AWAKE = True
                            enemy.state = State.WANDER
                    else:
                        enemy.health -= 35

                        BloodParticle(self.master, [self.master.game.ysort_grp], enemy.sprite_box,
                            PARTICLES[F'blood{random.randint(1, 3)}'], self.master.player.direction, 0.15)
                    
                    enemy.invincible = True
                    enemy.INVINCIBILITY_TIMER.start(820)
                    self.master.sound.dict[F"robot hit{random.randint(1, 3)}"].play()
class UI:

    def __init__(self, master):

        self.master = master

        self.screen = pygame.display.get_surface()

        self.ui_bar = pygame.image.load("graphics/ui/attention_bar.png").convert_alpha()
        self.ui_bar_rect = self.ui_bar.get_rect(midleft= (0, H//2) )
        self.bar_size = 32, 166
        self.bar_offset = 18, 24

        self.score_midtop = W/2, 10

    def draw(self):

        #bar
        self.screen.blit(self.ui_bar, self.ui_bar_rect)

        bar_filled = (100-self.master.player.attention_level) * self.bar_size[1]/100
        if self.master.player.attention_level < 0.7: bar_filled = self.bar_size[1]+1
        self.screen.fill(0xcfcfcf, (
            self.ui_bar_rect.left + self.bar_offset[0], self.ui_bar_rect.top + self.bar_offset[1],
            self.bar_size[0], bar_filled
        ))

        #score

        score_surf = self.master.fire_font.render(F"{self.master.player.kill_count}", True, (210, 5, 25))
        score_rect = score_surf.get_rect(midtop = self.score_midtop)

        self.screen.blit(score_surf, score_rect)



