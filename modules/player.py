import pygame
from .frect import FRect
from .entity import Entity

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
        self.deceleration = 0.8
        self.max_speed = 2.2
        self.moving = False

        self.EVENTS = (pygame.KEYDOWN)

    def update_image(self):

        flip = self.direction.x < 0
        self.image = pygame.transform.flip(self.original_image, flip, False)

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

    def move(self):

        if self.moving:
            self.velocity += self.direction * self.acceleration  * self.master.dt
        elif self.velocity.magnitude_squared() >= self.deceleration**2:
            self.velocity -= self.velocity.normalize() * self.deceleration  * self.master.dt
        else: self.velocity.update(0, 0)

        if (mag:=self.velocity.magnitude_squared()):
            if mag > self.max_speed**2:
                self.velocity.scale_to_length(self.max_speed)
        

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
        self.master.debug("pos: ", self.rect.center)
        self.master.debug("velocity: ", self.velocity)