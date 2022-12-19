import pygame


class Music:
    def __init__(self, master):
        self.master = master
        master.music = self
        self.tracks = {
            'in_game': "music/game_music.ogg"
        }
        track_type = "in_game"
        if self.master.app.state == self.master.app.IN_GAME: track_type = 'in_game'
        pygame.mixer.music.load(self.tracks[track_type])
        self.is_playing = False
        self.can_play = True
        self.started_playing = False

        self.change_track_to = None

        self.START_NEW_TRACK_TIMER = pygame.event.custom_type()
        self.EVENTS = (self.START_NEW_TRACK_TIMER)
    
    def change_track(self, track_type):
        pygame.mixer.music.fadeout(2_000)
        pygame.time.set_timer(self.START_NEW_TRACK_TIMER, 2_100, loops=1)
        self.change_track_to = track_type

    def process_events(self):

        for event in pygame.event.get(self.EVENTS):
            if event.type == self.START_NEW_TRACK_TIMER:
                pygame.mixer.music.load(self.tracks[self.change_track_to])
                pygame.mixer.music.play(loops=-1, fade_ms=2_000)
                if self.change_track_to == 'in_game':
                    pygame.mixer.music.set_volume(0.3)
                self.change_track_to = None
    
    def run(self):

        self.can_play = not self.master.game.paused

        self.process_events()

        if self.can_play and not self.is_playing:
            if not self.started_playing:
                pygame.mixer.music.play(loops=-1, fade_ms= 2_000)
                self.started_playing = True
            else:
                pygame.mixer.music.unpause()

            self.is_playing = True

        elif not self.can_play and self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False