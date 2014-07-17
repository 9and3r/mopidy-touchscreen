import pykka

import traceback
import logging
from threading import Thread
import pygame
from .screen_manager import ScreenManager

from mopidy import core


logger = logging.getLogger(__name__)

class TouchScreen(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(TouchScreen, self).__init__()
        self.core = core
        self.screen_size=(320, 240)
        self.screen_manager = ScreenManager(self.screen_size)


    def start_thread(self):
        pygame.init()
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(self.screen_size)
        while self.running:
            clock.tick(30)
            screen.blit(self.screen_manager.update(self.core),(0,0))
            pygame.display.flip()

    pygame.quit()

    def on_start(self):
        self.running=True
        thread = Thread(target=self.start_thread)
        thread.start()

    def on_stop(self):
        self.running = False

    def track_playback_started(self, tl_track):
        try:
            self.screen_manager.track_started(tl_track)
        except:
            traceback.print_exc()

 
