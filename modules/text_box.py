import pygame

class TextBox:
    
    def __init__(self, master):

        self.master = master
        master.text_box = self

        global dialogue_font, text_box_edge1, text_box_slice1, text_box_flip_edge1

        dialogue_font = pygame.font.SysFont("Verdana", 10)

        text_box_edge1 = pygame.image.load("graphics/test/text_box_edge.png").convert_alpha()
        text_box_slice1 = pygame.image.load("graphics/test/text_box_slice.png").convert_alpha()
        text_box_flip_edge1 = pygame.transform.flip(text_box_edge1, True, False)

    def get_text_box(self, text:str, color=0x0):

        text_surf = dialogue_font.render(text, False, color)
        slice = pygame.transform.scale(text_box_slice1, (text_surf.get_width(), text_box_slice1.get_height()))

        text_box_surf = pygame.Surface(
            (slice.get_width() + text_box_edge1.get_width()*2, slice.get_height()), pygame.SRCALPHA)

        text_rect = text_surf.get_rect(center = (text_box_surf.get_width()/2, text_box_surf.get_height()/2) )    

        text_box_surf.blit(text_box_edge1, (0, 0))
        text_box_surf.blit(slice, (text_box_edge1.get_width(), 0))
        text_box_surf.blit(text_box_flip_edge1, (text_box_edge1.get_width()+slice.get_width(), 0))
        text_box_surf.blit(text_surf, text_rect)

        return text_box_surf