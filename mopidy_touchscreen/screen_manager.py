import logging
import traceback

import pygame
from pkg_resources import resource_filename, Requirement
import mopidy
import mopidy.core

from .dynamic_background import DynamicBackground
from .library_screen import LibraryScreen
from .main_screen import MainScreen
from .menu_screen import MenuScreen
from .playlist_screen import PlaylistScreen
from .screen_objects import Progressbar, ScreenObjectsManager, TouchAndTextItem
from .touch_manager import TouchManager
from .tracklist import Tracklist


logger = logging.getLogger(__name__)


class ScreenManager():
    def __init__(self, size, core, backend, cache):
        self.size = size
        self.core = core
        self.backend = backend
        self.fonts = {}
        self.background = DynamicBackground()
        self.current_screen = 0
        self.base_size = self.size[1] / 8
        font = resource_filename(Requirement.parse("mopidy-touchscreen"),
                                 "mopidy_touchscreen/icomoon.ttf")
        self.fonts['base'] = pygame.font.SysFont("verdana", self.base_size)
        self.fonts['icon'] = pygame.font.Font(font, self.base_size)
        try:
            self.screens = [MainScreen(size, self, cache, core, self.fonts),
                            Tracklist(size, self.base_size, self),
                            LibraryScreen(size, self.base_size, self),
                            PlaylistScreen(size, self.base_size, self),
                            MenuScreen(size, self.base_size, self)]
        except:
            traceback.print_exc()
        self.track = None
        self.touch_manager = TouchManager(size)
        self.screen_objects_manager = ScreenObjectsManager()

        # Top bar
        self.top_bar = pygame.Surface((self.size[0], self.base_size),
                                      pygame.SRCALPHA)
        self.top_bar.fill((0, 0, 0, 128))

        # Play/pause
        button = TouchAndTextItem(self.fonts['icon'], u"\ue615 ", (0, 0), None)
        self.screen_objects_manager.set_touch_object("pause_play", button)
        x = button.get_right_pos()

        # Random
        button = TouchAndTextItem(self.fonts['icon'], u"\ue629 ", (x, 0), None)
        self.screen_objects_manager.set_touch_object("random", button)
        x = button.get_right_pos()

        # Repeat
        button = TouchAndTextItem(self.fonts['icon'], u"\ue626", (x, 0), None)
        self.screen_objects_manager.set_touch_object("repeat", button)
        x = button.get_right_pos()

        # Single
        button = TouchAndTextItem(self.fonts['base'], " 1 ", (x, 0), None)
        self.screen_objects_manager.set_touch_object("single", button)
        x = button.get_right_pos()

        # Internet
        button = TouchAndTextItem(self.fonts['icon'], u"\ue602 ", (x, 0), None)
        self.screen_objects_manager.set_touch_object("internet", button)
        x = button.get_right_pos()

        # Mute
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61f ", (x, 0), None)
        self.screen_objects_manager.set_touch_object("mute", button)
        x = button.get_right_pos()

        # Volume
        progress = Progressbar(self.fonts['base'], "100", (x, 0),
                               (self.size[0] - x, self.base_size), 100, True)
        self.screen_objects_manager.set_touch_object("volume", progress)
        progress.set_value(self.core.playback.volume.get())

        # Menu buttons

        button_size = (self.size[0] / 5, self.base_size)

        # Main button
        button = TouchAndTextItem(self.fonts['icon'], u" \ue600",
                                  (0, self.base_size * 7), button_size)
        self.screen_objects_manager.set_touch_object("menu_0", button)
        x = button.get_right_pos()

        # Tracklist button
        button = TouchAndTextItem(self.fonts['icon'], u" \ue60d",
                                  (x, self.base_size * 7), button_size)
        self.screen_objects_manager.set_touch_object("menu_1", button)
        x = button.get_right_pos()

        # Library button
        button = TouchAndTextItem(self.fonts['icon'], u" \ue604",
                                  (x, self.base_size * 7), button_size)
        self.screen_objects_manager.set_touch_object("menu_2", button)
        x = button.get_right_pos()

        # Playlist button
        button = TouchAndTextItem(self.fonts['icon'], u" \ue605",
                                  (x, self.base_size * 7), button_size)
        self.screen_objects_manager.set_touch_object("menu_3", button)
        x = button.get_right_pos()

        # Menu button
        button = TouchAndTextItem(self.fonts['icon'], u" \ue60a",
                                  (x, self.base_size * 7), None)
        self.screen_objects_manager.set_touch_object("menu_4", button)

        # Down bar
        self.down_bar = pygame.Surface(
            (self.size[0], self.size[1] - self.base_size * 7), pygame.SRCALPHA)
        self.down_bar.fill((0, 0, 0, 128))

        self.options_changed()
        self.mute_changed(self.core.playback.mute.get())
        self.playback_state_changed(self.core.playback.state.get(),
                                    self.core.playback.state.get())
        self.screens[4].check_connection()
        self.change_screen(self.current_screen)

    def update(self):
        surface = pygame.Surface(self.size)
        self.background.draw_background(surface)
        self.screens[self.current_screen].update(surface)
        surface.blit(self.top_bar, (0, 0))
        surface.blit(self.down_bar, (0, self.base_size * 7))
        self.screen_objects_manager.render(surface)
        return surface

    def track_started(self, track):
        self.track = track
        self.screens[0].track_started(track.track)
        self.screens[1].track_started(track)

    def track_playback_ended(self, tl_track, time_position):
        self.screens[0].track_playback_ended(tl_track, time_position)

    def event(self, event):
        touch_event = self.touch_manager.event(event)
        if touch_event is not None:
            if touch_event.type == TouchManager.click:
                objects = self.screen_objects_manager.get_touch_objects_in_pos(
                    touch_event.current_pos)
                if objects is not None:
                    for key in objects:
                        if key == "volume":
                            manager = self.screen_objects_manager
                            volume = manager.get_touch_object(key)
                            pos = touch_event.current_pos
                            value = volume.get_pos_value(pos)
                            self.backend.tell(
                                {'action': 'volume', 'value': value})
                            self.volume_changed(value)
                        elif key == "pause_play":
                            if self.core.playback.state.get() == \
                                    mopidy.core.PlaybackState.PLAYING:
                                self.core.playback.pause()
                            else:
                                self.core.playback.play()
                        elif key == "mute":
                            mute = not self.core.playback.mute.get()
                            self.core.playback.set_mute(mute)
                            self.mute_changed(mute)
                        elif key == "random":
                            random = not self.core.tracklist.random.get()
                            self.core.tracklist.set_random(random)
                            self.options_changed()
                        elif key == "repeat":
                            self.core.tracklist.set_repeat(
                                not self.core.tracklist.repeat.get())
                        elif key == "single":
                            self.core.tracklist.set_single(
                                not self.core.tracklist.single.get())
                        elif key == "internet":
                            self.screens[4].check_connection()
                        elif key[:-1] == "menu_":
                            self.change_screen(int(key[-1:]))
            self.screens[self.current_screen].touch_event(touch_event)

    def volume_changed(self, volume):
        if not self.core.playback.mute.get():
            if volume > 80:
                self.screen_objects_manager.get_touch_object("mute").set_text(
                    u"\ue61f", False)
            elif volume > 50:
                self.screen_objects_manager.get_touch_object("mute").set_text(
                    u"\ue620", False)
            elif volume > 20:
                self.screen_objects_manager.get_touch_object("mute").set_text(
                    u"\ue621", False)
            else:
                self.screen_objects_manager.get_touch_object("mute").set_text(
                    u"\ue622", False)
        self.screen_objects_manager.get_touch_object("volume").set_value(
            volume)

    def playback_state_changed(self, old_state, new_state):
        if new_state == mopidy.core.PlaybackState.PLAYING:
            self.screen_objects_manager.get_touch_object(
                "pause_play").set_text(u"\ue616", False)
        else:
            self.screen_objects_manager.get_touch_object(
                "pause_play").set_text(u"\ue615", False)

    def mute_changed(self, mute):
        self.screen_objects_manager.get_touch_object("mute").set_active(
            not mute)
        if mute:
            self.screen_objects_manager.get_touch_object("mute").set_text(
                u"\ue623", False)
        else:
            self.volume_changed(self.core.playback.volume.get())

    def tracklist_changed(self):
        self.screens[1].tracklist_changed()

    def options_changed(self):
        self.screen_objects_manager.get_touch_object("random").set_active(
            self.core.tracklist.random.get())
        self.screen_objects_manager.get_touch_object("repeat").set_active(
            self.core.tracklist.repeat.get())
        self.screen_objects_manager.get_touch_object("single").set_active(
            self.core.tracklist.single.get())

    def change_screen(self, new_screen):
        self.screen_objects_manager.get_touch_object(
            "menu_" + str(self.current_screen)).set_active(False)
        self.current_screen = new_screen
        self.screen_objects_manager.get_touch_object(
            "menu_" + str(new_screen)).set_active(True)

    def playlists_loaded(self):
        self.screens[3].playlists_loaded()

    def set_connection(self, connection, loading):
        internet = self.screen_objects_manager.get_touch_object("internet")
        if loading:
            internet.set_text(u"\ue627", None)
            internet.set_active(False)
        else:
            internet.set_text(u"\ue602", None)
            internet.set_active(connection)
