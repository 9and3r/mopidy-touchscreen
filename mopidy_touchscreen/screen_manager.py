from .main_screen import MainScreen
from .touch_manager import TouchManager
from .screen_objects import ScreenObjectsManager
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
        self.current_screen = 1
        self.base_size = self.size[1] / 8
        self.fonts['dejavuserif'] = pygame.font.SysFont("dejavuserif", self.base_size)
        self.fonts['dejavusans'] = pygame.font.SysFont("dejavusans", self.base_size)
        try:
            self.screens = [MainScreen(size, self, "/home/ander", core,self.fonts),Tracklist(size,self.base_size,self)]
        except:
            traceback.print_exc()
        self.track = None
        self.touch_manager = TouchManager(size)
        self.screen_objects_manager = ScreenObjectsManager(self.base_size)
        x = self.screen_objects_manager.add_touch_object("pause_play",self.fonts['dejavusans']," ll",(0,0), None, (255,255,255))
        x = x + self.base_size / 2
        x = self.screen_objects_manager.add_touch_object("random",self.fonts['dejavuserif'],u"\u2928",(x,0),None,(255,255,255))
        x = x + self.base_size / 2
        x = self.screen_objects_manager.add_touch_object("repeat",self.fonts['dejavuserif'],u"\u27F21",(x,0),None,(255,255,255))
        x = x + self.base_size / 2
        x = self.screen_objects_manager.add_touch_object("mute",self.fonts['dejavusans'],"Mute",(x,0),None,(255,255,255))
        x = x + self.base_size / 2
        self.screen_objects_manager.add_progressbar("volume",self.fonts['dejavusans'],"100", (x,0), (self.size[0],self.base_size),100, True)
        self.screen_objects_manager.get_touch_object("volume").set_value(self.core.playback.volume.get())
        self.top_bar = pygame.Surface((self.size[0],self.base_size),pygame.SRCALPHA)
        self.top_bar.fill((0,0,0,128))
        self.playback_state_changed(mopidy.core.PlaybackState.STOPPED, self.core.playback.state.get())
        self.down_bar = pygame.Surface((self.size[0], self.base_size),pygame.SRCALPHA)
        self.down_bar.fill((0,0,0,128))
        x = self.screen_objects_manager.add_touch_object("menu_main",self.fonts['dejavusans'],"Main",(0,self.base_size*7),None,(255,255,255))

    def update(self):
        surface = pygame.Surface(self.size)
        self.background.drawBackground(surface)
        self.screens[self.current_screen].update(surface)
        surface.blit(self.top_bar,(0,0))
        surface.blit(self.top_bar,(0,self.base_size*7))
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
                            value = self.screen_objects_manager.get_touch_object(key).get_pos_value(touch_event.current_pos)
                            self.backend.tell({'action':'volume','value':value})
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
                            self.backend.tell({'action':'mute','value':mute})
                        elif key == "random":
                            logger.error(self.core.tracklist.random)
                            self.core.tracklist.random = not self.core.tracklist.random
                            #self.backend.tell({'action':'random','value':random})
            self.screens[self.current_screen].touch_event(touch_event)

    def volume_changed(self, volume):
        self.screen_objects_manager.get_touch_object("volume").set_value(volume)

    def playback_state_changed(self, old_state, new_state):
        if new_state == mopidy.core.PlaybackState.PLAYING:
            self.screen_objects_manager.get_touch_object("pause_play").set_text(" ll",False)
        else:
            self.screen_objects_manager.get_touch_object("pause_play").set_text(u" \u25B8",True)

    def mute_changed(self, mute):
        self.touch_text_manager.get_touch_object("mute").set_active(mute)

    def tracklist_changed(self):
        self.screens[1].tracklist_changed()