import os
import pygame

class SoundSet:

    def __init__(self, master):

        self.master = master
        self.master.sound = self
        self.dict = {}

        for sound_file in os.listdir("sounds"):
            self.dict[sound_file[:-4]] = pygame.mixer.Sound(F"sounds/{sound_file}")
        