import logging
import traceback
from threading import Thread
import os
import pygame
import pykka
import mopidy
from mopidy import core

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
        os.environ["SDL_FBDEV"] = config['touchscreen']['sdl_fbdev']
        os.environ["SDL_MOUSEDRV"] = config['touchscreen'][
            'sdl_mousdrv']
        os.environ["SDL_MOUSEDEV"] = config['touchscreen'][
            'sdl_mousedev']
        os.environ["SDL_AUDIODRIVER"] = config['touchscreen']['sdl_audiodriver']
        os.environ["SDL_PATH_DSP"] = config['touchscreen']['sdl_path_dsp']
        pygame.init()
        pygame.display.set_caption("Mopidy-Touchscreen")
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.screen_size,
                                             pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.screen_size)
        pygame.mouse.set_visible(self.cursor)
        self.screen_manager = ScreenManager(self.screen_size,
                                            self.core,
                                            self.cache_dir)
        

        # Raspberry pi GPIO
        self.gpio = config['touchscreen']['gpio']
        if self.gpio:
            from .gpio_inpput_manager import GPIOManager

            pins = {}
            pins['left'] = config['touchscreen']['gpio_left']
            pins['right'] = config['touchscreen']['gpio_right']
            pins['up'] = config['touchscreen']['gpio_up']
            pins['down'] = config['touchscreen']['gpio_down']
            pins['enter'] = config['touchscreen']['gpio_enter']
            self.gpio_manager = GPIOManager(pins)

    def start_thread(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(15)
            self.screen.blit(self.screen_manager.update(), (0, 0))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYUP and event.key == pygame.K_q:
                    self.running = False
                else:
                    self.screen_manager.event(event)
        pygame.quit()
        mopidy.utils.process.exit_process()

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
