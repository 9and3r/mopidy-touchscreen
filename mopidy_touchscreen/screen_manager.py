from .main_screen import MainScreen
from .touch_manager import TouchManager
import pygame
import logging

logger = logging.getLogger(__name__)


class ScreenManager():

    def __init__(self, size, core):
        self.screen_size = size
        self.screens = [MainScreen(size, self, "/home/ander", core)]
        self.track = None
        self.touch_manager = TouchManager()

    def update(self):
        return self.screens[0].update()

    def track_started(self, track):
        self.track = track
        self.screens[0].track_started(track.track)

    def event(self, event):
        touch_event = self.touch_manager.event(event)
        if touch_event is not None:
            self.screens[0].touch_event(touch_event)



