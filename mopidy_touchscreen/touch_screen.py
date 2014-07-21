import pykka
import traceback
import logging
from threading import Thread
import pygame
from .screen_manager import ScreenManager
from pygame.locals import *

from mopidy import core


logger = logging.getLogger(__name__)


class TouchScreen(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(TouchScreen, self).__init__()
        self.backend = pykka.ActorRegistry.get_by_class_name("TouchScreenBackend")[0]
        logger.error(self.backend)
        self.core = core
        self.running = False
        self.screen_size=(320, 240)
        #self.screen_size=(800, 600)
        pygame.init()
        self.screen_manager = ScreenManager(self.screen_size,self.core, self.backend)

    def start_thread(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(self.screen_size)
        while self.running:
            clock.tick(15)
            screen.blit(self.screen_manager.update(),(0,0))
            pygame.display.flip()
            for event in pygame.event.get():
                self.screen_manager.event(event)
        pygame.quit()

    def on_start(self):
        try:
            self.running = True
            thread = Thread(target=self.start_thread)
            thread.start()
        except:
            traceback.print_exc()

    def on_stop(self):
        self.running = False

    def track_playback_started(self, tl_track):
        try:
            self.screen_manager.track_started(tl_track)
        except:
            traceback.print_exc()

    def volume_changed(self, volume):
        self.screen_manager.volume_changed(volume)

    def playback_state_changed(self,old_state, new_state):
        self.screen_manager.playback_state_changed(old_state, new_state)
