import pygame, os
# from PIL import Image, ImageFilter

class CustomGroup(pygame.sprite.Group):

    def draw(self):

        for sprite in self.sprites():
            sprite.draw()

    def draw_y_sort(self, key):

        for sprite in sorted(self.sprites(), key=key):
            sprite.draw()


def import_spritesheet(folder_path, sheet_name):
    "imports a given spritesheet and places it in a list"
    sprite_list = []
    name, size = sheet_name[:-4].split('-')
    w, h = [int(x) for x in size.split('x')]
    sheet = pygame.image.load(F"{folder_path}/{sheet_name}").convert_alpha()
    for i in range(sheet.get_width()//w):
        # sprite = pygame.Surface((w, h), pygame.SRCALPHA)
        # sprite.blit(sheet, (-w*i, 0))
        sprite = sheet.subsurface((w*i, 0, w, h))
        sprite_list.append(sprite)
    return sprite_list


def import_sprite_sheets(folder_path):
    "imports all sprite sheets in a folder"
    animations = {}

    for file in os.listdir(folder_path):
        if file.endswith(".png"):
            animations[file.split('-')[0]] = import_spritesheet(folder_path, file)

    return animations

def load_pngs(folder_path):
    "loads all png from folder"

    return [pygame.image.load(F"{folder_path}/{file}").convert() for file in sorted(os.listdir(folder_path))]

def dist_sq(p1, p2):

    return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2

class CustomTimer:

    def __init__(self):

        self.running = False

        self.duration = None
        self.start_time = None
        self.loops = 0

    def start(self, duration, loops=1):

        self.running = True
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.loops = loops

    def stop(self):
        
        if self.running:
            self.running = False
            return True

    def check(self):

        if not self.running: return False
        
        if pygame.time.get_ticks() - self.duration >= self.start_time:
            self.loops -= 1
            if self.loops == 0:
                self.running = False
            else: self.start_time += self.duration
            return True

# def blur_image(image, radius=6):
#     raw_str = pygame.image.tostring(image, 'RGBA')
#     pil_blured = Image.frombytes("RGBA", image.get_size(), raw_str).filter(ImageFilter.GaussianBlur(radius=radius))
#     return pygame.image.fromstring(pil_blured.tobytes("raw", 'RGBA'), image.get_size(), 'RGBA')