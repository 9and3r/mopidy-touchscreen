import logging
import os
import traceback
from threading import Thread

from mopidy import core, exceptions

import pygame

import pykka

from .screen_manager import ScreenManager


logger = logging.getLogger(__name__)


class TouchScreen(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(TouchScreen, self).__init__()
        self.core = core
        self.running = False
        self.cursor = config['touchscreen']['cursor']
        self.cache_dir = config['touchscreen']['cache_dir']
        self.fullscreen = config['touchscreen']['fullscreen']
        self.screen_size = (config['touchscreen']['screen_width'],
                            config['touchscreen']['screen_height'])
        self.resolution_factor = (config['touchscreen']['resolution_factor'])
        if config['touchscreen']['sdl_fbdev'].lower() != "none":
            os.environ["SDL_FBDEV"] = config['touchscreen']['sdl_fbdev']
        if config['touchscreen']['sdl_mousdrv'].lower() != "none":
            os.environ["SDL_MOUSEDRV"] = (
                config['touchscreen']['sdl_mousdrv'])

        if config['touchscreen']['sdl_mousedev'].lower() != "none":
            os.environ["SDL_MOUSEDEV"] = config['touchscreen']['sdl_mousedev']

        if config['touchscreen']['sdl_audiodriver'].lower() != "none":
            os.environ["SDL_AUDIODRIVER"] = (
                config['touchscreen']['sdl_audiodriver'])

        os.environ["SDL_PATH_DSP"] = config['touchscreen']['sdl_path_dsp']
        pygame.init()
        pygame.display.set_caption("Mopidy-Touchscreen")
        self.get_display_surface(self.screen_size)
        pygame.mouse.set_visible(self.cursor)
        self.screen_manager = ScreenManager(self.screen_size,
                                            self.core,
                                            self.cache_dir,
                                            self.resolution_factor)

        # Raspberry pi GPIO
        self.gpio = config['touchscreen']['gpio']
        if self.gpio:

            from .input import GPIOManager

            pins = {}
            pins['left'] = config['touchscreen']['gpio_left']
            pins['right'] = config['touchscreen']['gpio_right']
            pins['up'] = config['touchscreen']['gpio_up']
            pins['down'] = config['touchscreen']['gpio_down']
            pins['enter'] = config['touchscreen']['gpio_enter']
            self.gpio_manager = GPIOManager(pins)

    def get_display_surface(self, size):
        try:
            if self.fullscreen:
                self.screen = pygame.display.set_mode(
                    size, pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        except Exception:
            raise exceptions.FrontendError("Error on display init:\n"
                                           + traceback.format_exc())

    def start_thread(self):
        clock = pygame.time.Clock()
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        while self.running:
            clock.tick(12)
            self.screen_manager.update(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    os.system("pkill mopidy")
                elif event.type == pygame.VIDEORESIZE:
                    self.get_display_surface(event.size)
                    self.screen_manager.resize(event)
                else:
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

    def playback_state_changed(self, old_state, new_state):
        self.screen_manager.playback_state_changed(old_state,
                                                   new_state)

    def tracklist_changed(self):
        try:
            self.screen_manager.tracklist_changed()
        except:
            traceback.print_exc()

    def track_playback_ended(self, tl_track, time_position):
        self.screen_manager.track_playback_ended(tl_track,
                                                 time_position)

    def options_changed(self):
        try:
            self.screen_manager.options_changed()
        except:
            traceback.print_exc()

    def playlists_loaded(self):
        self.screen_manager.playlists_loaded()
