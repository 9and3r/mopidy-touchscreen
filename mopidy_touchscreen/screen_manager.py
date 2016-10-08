import logging
import random
import traceback

from graphic_utils import DynamicBackground, \
    ScreenObjectsManager, TouchAndTextItem
from input import InputManager

import mopidy

from pkg_resources import Requirement, resource_filename

import pygame

from screens import BaseScreen, Keyboard, LibraryScreen, MainScreen, MenuScreen,\
    PlaylistScreen, SearchScreen, Tracklist


logger = logging.getLogger(__name__)

search_index = 0
main_screen_index = 1
tracklist_index = 2
library_index = 3
playlist_index = 4
menu_index = 5


class ScreenManager():

    def __init__(self, size, core, cache, resolution_factor):
        self.core = core
        self.cache = cache
        self.fonts = {}
        self.background = None
        self.current_screen = library_index

        # Init variables in init
        self.base_size = None
        self.size = None
        self.screens = None
        self.track = None
        self.input_manager = InputManager(size)
        self.down_bar_objects = ScreenObjectsManager()
        self.down_bar = None
        self.keyboard = None
        self.update_type = BaseScreen.update_all

        self.resolution_factor = resolution_factor

        self.init_manager(size)

        self.last_surface = pygame.Surface(size)

    def init_manager(self, size):
        self.size = size
        self.base_size = self.size[1] / self.resolution_factor

        self.background = DynamicBackground(self.size)
        font_icon = resource_filename(
            Requirement.parse("mopidy-touchscreen"),
            "mopidy_touchscreen/icomoon.ttf")

        font_base = resource_filename(
            Requirement.parse("mopidy-touchscreen"),
            "mopidy_touchscreen/NotoSans-Regular.ttf")
        self.fonts['base'] = pygame.font.Font(font_base, int(self.base_size*0.9))
        self.fonts['icon'] = pygame.font.Font(font_icon, int(self.base_size*0.9))

        self.track = None

        # Menu buttons

        button_size = (self.size[0] / 6, self.base_size)

        menu_icons = [u" \ue986", u" \ue600", u"\ue60d", u" \ue604", u" \ue605", u" \ue60a"]

        x = 0
        i = 0
        while(i<6):

            button = TouchAndTextItem(self.fonts['icon'], menu_icons[i],
                                    (x, self.size[1] - self.base_size),
                                    button_size, center=True)
            self.down_bar_objects.set_touch_object("menu_" + str(i), button)
            x = button.get_right_pos()
            i += 1
            button.pos = (button.pos[0], self.size[1] - button.rect_in_pos.size[1])

        # Down bar
        self.down_bar = pygame.Surface(
            (self.size[0], button.rect_in_pos.size[1]),
            pygame.SRCALPHA)
        self.down_bar.fill((0, 0, 0, 200))

        screen_size = (size[0], self.size[1] - button.rect.size[1])

        try:
            self.screens = [
                SearchScreen(screen_size, self.base_size, self, self.fonts),
                MainScreen(screen_size, self.base_size, self, self.fonts,
                           self.cache, self.core, self.background),
                Tracklist(screen_size, self.base_size, self, self.fonts),
                LibraryScreen(screen_size, self.base_size, self, self.fonts),
                PlaylistScreen(screen_size,
                               self.base_size, self, self.fonts),
                MenuScreen(screen_size, self.base_size, self, self.fonts, self.core)]
        except:
            traceback.print_exc()

        self.options_changed()
        self.mute_changed(self.core.playback.mute.get())
        playback_state = self.core.playback.state.get()
        self.playback_state_changed(playback_state,
                                    playback_state)
        self.screens[menu_index].check_connection()

        self.change_screen(self.current_screen)

        self.update_type = BaseScreen.update_all

    def get_update_type(self):
        if self.update_type == BaseScreen.update_all:
            self.update_type = BaseScreen.no_update
            return BaseScreen.update_all
        else:
            if self.keyboard:
                return BaseScreen.no_update
            else:
                if self.background.should_update():
                    return BaseScreen.update_all
                else:
                    if self.screens[self.current_screen].should_update():
                        return BaseScreen.update_partial
                    else:
                        return BaseScreen.no_update

    def update(self, screen):
        update_type = self.get_update_type()
        if update_type != BaseScreen.no_update:
            rects = []
            if update_type == BaseScreen.update_partial:
                surface = self.last_surface
                self.screens[self.current_screen].find_update_rects(rects)
                self.background.draw_background_in_rects(surface, rects)
            else:
                surface = self.background.draw_background()

            if self.keyboard:
                self.keyboard.update(surface)
            else:
                self.screens[self.current_screen].\
                    update(surface, update_type, rects)
                surface.blit(self.down_bar, (0, self.size[1] - self.down_bar.get_size()[1]))
                self.down_bar_objects.render(surface)

            if update_type == BaseScreen.update_all:
                screen.blit(surface, (0, 0))
                pygame.display.flip()
            else:
                for rect in rects:
                    screen.blit(surface, rect, area=rect)
                    pygame.display.update(rects)
            self.last_surface = surface

    def track_started(self, track):
        self.track = track
        self.screens[main_screen_index].track_started(track.track)
        self.screens[tracklist_index].track_started(track)

    def track_playback_ended(self, tl_track, time_position):
        self.screens[main_screen_index].track_playback_ended(
            tl_track, time_position)

    def event(self, event):
        event = self.input_manager.event(event)
        if event is not None:
            if self.keyboard is not None:
                self.keyboard.touch_event(event)
            elif not self.manage_event(event):
                self.screens[self.current_screen].touch_event(event)
            self.update_type = BaseScreen.update_all

    def manage_event(self, event):
        if event.type == InputManager.click:
            objects = \
                self.down_bar_objects.get_touch_objects_in_pos(
                    event.current_pos)
            return self.click_on_objects(objects, event)
        else:
            if event.type == InputManager.key and not event.longpress:
                dir = event.direction
                if dir == InputManager.right or dir == InputManager.left:
                    if not self.screens[self.current_screen]\
                            .change_screen(dir):
                        if dir == InputManager.right:
                            self.change_screen(self.current_screen+1)
                        else:
                            self.change_screen(self.current_screen-1)
                    return True
                elif event.unicode is not None:
                    if event.unicode == "n":
                        self.core.playback.next()
                    elif event.unicode == "p":
                        self.core.playback.previous()
                    elif event.unicode == "+":
                        volume = self.core.playback.volume.get() + 10
                        if volume > 100:
                            volume = 100
                        self.core.mixer.set_volume(volume)
                    elif event.unicode == "-":
                        volume = self.core.playback.volume.get() - 10
                        if volume < 0:
                            volume = 0
                        self.core.mixer.set_volume(volume)
                    elif event.unicode == " ":
                        if self.core.playback.get_state().get() == \
                                mopidy.core.PlaybackState.PLAYING:
                            self.core.playback.pause()
                        else:
                            self.core.playback.play()
            return False

    def volume_changed(self, volume):
        self.screens[main_screen_index].volume_changed(volume)
        self.update_type = BaseScreen.update_all

    def playback_state_changed(self, old_state, new_state):
        self.screens[main_screen_index].playback_state_changed(
            old_state, new_state)
        self.update_type = BaseScreen.update_all

    def mute_changed(self, mute):
        self.screens[main_screen_index].mute_changed(mute)
        self.update_type = BaseScreen.update_all

    def tracklist_changed(self):
        self.screens[tracklist_index].tracklist_changed()
        self.update_type = BaseScreen.update_all

    def options_changed(self):
        self.screens[menu_index].options_changed()
        self.update_type = BaseScreen.update_all

    def change_screen(self, new_screen):
        if new_screen > -1 and new_screen < len(self.screens):
            self.down_bar_objects.get_touch_object(
                "menu_" + str(self.current_screen)).set_active(False)
            self.current_screen = new_screen
            self.down_bar_objects.get_touch_object(
                "menu_" + str(new_screen)).set_active(True)
        self.update_type = BaseScreen.update_all

    def click_on_objects(self, objects, event):
        if objects is not None:
            for key in objects:
                if key[:-1] == "menu_":
                    self.change_screen(int(key[-1:]))
                    return True
        return False

    def playlists_loaded(self):
        self.screens[playlist_index].playlists_loaded()
        self.update_type = BaseScreen.update_all

    def search(self, query, mode):
        self.screens[search_index].search(query, mode)
        self.update_type = BaseScreen.update_all

    def resize(self, event):
        self.init_manager(event.size)
        self.update_type = BaseScreen.update_all

    def stream_title_changed(self, title):
        self.screens[main_screen_index].stream_title_changed(title)
        self.update_type = BaseScreen.update_all

    def open_keyboard(self, input_listener):
        self.keyboard = Keyboard(self.size, self.base_size, self,
                                 self.fonts, input_listener)
        self.update_type = BaseScreen.update_all

    def close_keyboard(self):
        self.keyboard = None
        self.update_type = BaseScreen.update_all
