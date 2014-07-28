from .main_screen import MainScreen
from .touch_manager import TouchManager
from .screen_objects import *
from .tracklist import Tracklist
from .dynamic_background import DynamicBackground
import pygame
import logging
import mopidy
import traceback

logger = logging.getLogger(__name__)


class ScreenManager():
    def __init__(self, size, core, backend):
        self.size = size
        self.core = core
        self.backend = backend
        self.fonts = {}
        self.background = DynamicBackground()
        self.current_screen = 0
        self.base_size = self.size[1] / 8
        self.fonts['dejavuserif'] = pygame.font.SysFont("dejavuserif", self.base_size)
        self.fonts['dejavusans'] = pygame.font.SysFont("dejavusans", self.base_size)
        try:
            self.screens = [MainScreen(size, self, "/home/ander", core, self.fonts),
                            Tracklist(size, self.base_size, self)]
        except:
            traceback.print_exc()
        self.track = None
        self.touch_manager = TouchManager(size)
        self.screen_objects_manager = ScreenObjectsManager()

        # Top bar
        self.top_bar = pygame.Surface((self.size[0], self.base_size), pygame.SRCALPHA)
        self.top_bar.fill((0, 0, 0, 128))

        #Play/pause
        button = TouchAndTextItem(self.fonts['dejavusans'], " ll", (0, 0), None)
        self.screen_objects_manager.set_touch_object("pause_play", button)
        x = button.get_right_pos()

        #Random
        button = TouchAndTextItem(self.fonts['dejavuserif'], u"\u2928", (x, 0), None)
        self.screen_objects_manager.set_touch_object("random", button)
        x = button.get_right_pos()

        #Repeat
        button = TouchAndTextItem(self.fonts['dejavuserif'], u"\u27F21", (x, 0), None)
        self.screen_objects_manager.set_touch_object("repeat", button)
        x = button.get_right_pos()

        #Mute
        button = TouchAndTextItem(self.fonts['dejavusans'], "Mute", (x, 0), None)
        self.screen_objects_manager.set_touch_object("mute", button)
        x = button.get_right_pos()

        #Volume
        progress = Progressbar(self.fonts['dejavusans'], "100", (x, 0), (self.size[0] - x, self.base_size), 100, True)
        self.screen_objects_manager.set_touch_object("volume", progress)
        progress.set_value(self.core.playback.volume.get())

        #Menu buttons

        #Main button
        button = TouchAndTextItem(self.fonts['dejavusans'], "Main", (0, self.base_size * 7), None)
        self.screen_objects_manager.set_touch_object("menu_main", button)
        x = button.get_right_pos()

        #Tracklist button
        button = TouchAndTextItem(self.fonts['dejavusans'], "Tracklist", (x, self.base_size * 7), None)
        self.screen_objects_manager.set_touch_object("menu_tracklist", button)

        #Down bar
        self.down_bar = pygame.Surface((self.size[0], self.base_size), pygame.SRCALPHA)
        self.down_bar.fill((0, 0, 0, 128))

        self.options_changed()
        self.playback_state_changed(self.core.playback.state.get(), self.core.playback.state.get())

    def update(self):
        surface = pygame.Surface(self.size)
        self.background.draw_background(surface)
        self.screens[self.current_screen].update(surface)
        surface.blit(self.top_bar, (0, 0))
        surface.blit(self.top_bar, (0, self.base_size * 7))
        self.screen_objects_manager.render(surface)
        return surface

    def track_started(self, track):
        self.track = track
        self.screens[0].track_started(track.track)

    def event(self, event):
        touch_event = self.touch_manager.event(event)
        if touch_event is not None:
            if touch_event.type == TouchManager.click:
                objects = self.screen_objects_manager.get_touch_objects_in_pos(touch_event.current_pos)
                if objects is not None:
                    for key in objects:
                        if key == "volume":
                            value = self.screen_objects_manager.get_touch_object(key).get_pos_value(
                                touch_event.current_pos)
                            self.backend.tell({'action': 'volume', 'value': value})
                            self.screen_objects_manager.get_touch_object(key).set_value(value)
                        elif key == "pause_play":
                            if self.core.playback.state.get() == mopidy.core.PlaybackState.PLAYING:
                                self.core.playback.pause()
                                logger.error("pausatzen")
                            else:
                                self.core.playback.play()
                                logger.error("erreproduzitzen")
                        elif key == "mute":
                            mute = not self.core.playback.mute.get()
                            self.core.playback.set_mute(mute)
                            self.mute_changed(mute)
                        elif key == "random":
                            random = not self.core.tracklist.random.get()
                            self.core.tracklist.set_random(random)
                            self.options_changed()
                        elif key == "repeat":
                            self.change_repeat_single()
                        elif key == "menu_main":
                            self.current_screen = 0
                        elif key == "menu_tracklist":
                            self.current_screen = 1
            self.screens[self.current_screen].touch_event(touch_event)

    def volume_changed(self, volume):
        self.screen_objects_manager.get_touch_object("volume").set_value(volume)

    def playback_state_changed(self, old_state, new_state):
        if new_state == mopidy.core.PlaybackState.PLAYING:
            self.screen_objects_manager.get_touch_object("pause_play").set_text(" ll", True)
        else:
            self.screen_objects_manager.get_touch_object("pause_play").set_text(u" \u25B8", True)

    def mute_changed(self, mute):
        self.screen_objects_manager.get_touch_object("mute").set_active(mute)

    def tracklist_changed(self):
        self.screens[1].tracklist_changed()

    def options_changed(self):
        self.screen_objects_manager.get_touch_object("random").set_active(self.core.tracklist.random.get())
        repeat = self.core.tracklist.repeat.get()
        single = self.core.tracklist.single.get()
        repeat_button = self.screen_objects_manager.get_touch_object("repeat")
        repeat_button.set_active(repeat)
        if single:
            repeat_button.set_text(u"\u27F21", True)
        else:
            repeat_button.set_text(u"\u27F2", True)

    def change_repeat_single(self):
        repeat = self.core.tracklist.repeat.get()
        single = self.core.tracklist.single.get()
        if single:
            if repeat:
                repeat = False
                single = False
            else:
                repeat = True
                single = False
        else:
            if repeat:
                # repeat = True
                single = True
            else:
                # repeat = False
                single = True
        self.core.tracklist.set_repeat(repeat)
        self.core.tracklist.set_single(single)
        self.options_changed()
