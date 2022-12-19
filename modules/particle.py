import pygame

class BloodParticle(pygame.sprite.Sprite):

    def __init__(self, master, grps, enemy_rect, animation, direction, anim_speed):

        super().__init__(grps)
        self.master = master
        self.screen = pygame.display.get_surface()

        self.enemy_rect = enemy_rect
        self.direction = direction
        self.anim_speed = anim_speed
        self.animation = animation
        self.anim_index = 0

        self.image = self.animation[0]
        self.rect = self.image.get_rect()
        self.hitbox = self.rect

        if direction.x > 0:
            self.rect.midleft = enemy_rect.midright
        elif direction.x < 0:
            self.rect.midright = enemy_rect.midleft
        elif direction.y < 0:
            self.rect.midbottom = enemy_rect.midtop
        elif direction.y > 0:
            self.rect.midtop = enemy_rect.midbottom

    def draw(self):


        try:
            image = self.animation[int(self.anim_index)]
        except IndexError:
            self.kill()
            return
            self.anim_index = 0
            image = self.animation[int(self.anim_index)]

        self.anim_index += self.anim_speed*self.master.dt

        if self.direction.x > 0:
            self.image = image
        elif self.direction.x < 0:
            self.image = pygame.transform.flip(image, True, False)
        elif self.direction.y < 0:
            self.image = pygame.transform.rotate(image, 90)
        elif self.direction.y > 0:
            self.image = pygame.transform.rotate(image, -90)

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)

