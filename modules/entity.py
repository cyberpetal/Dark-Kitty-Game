import pygame

class Entity(pygame.sprite.Sprite):

    def __init__(self, grps):
        super().__init__(grps)

    def check_bounds_collision(self, axis, bounds):

        if axis == 0: #x
            
             for rect in bounds:
                if self.hitbox.colliderect(rect):

                    if self.velocity.x > 0:
                        self.hitbox.right = rect.left
                        return 1
                    elif self.velocity.x < 0:
                        self.hitbox.left = rect.right
                        return -1

        if axis == 1: #y

            for rect in bounds:
                if self.hitbox.colliderect(rect):

                    if self.velocity.y > 0:
                        self.hitbox.bottom = rect.top
                        return 1
                    elif self.velocity.y < 0:
                        self.hitbox.top = rect.bottom
                        return -1        


