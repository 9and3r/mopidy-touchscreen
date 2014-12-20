import logging
import mopidy.models

from .list_view import ListView
from .input_manager import InputManager
from .base_screen import BaseScreen

logger = logging.getLogger(__name__)


class LibraryScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.list_view = ListView((0, 0), (
            self.size[0], self.size[1] - self.base_size),
                                  self.base_size,
                                  self.fonts['base'])
        self.directory_list = []
        self.current_directory = None
        self.library = None
        self.library_strings = None
        self.lookup_uri(None)

    def get_dirty_area(self):
        return self.list_view.get_dirty_area()

    def go_inside_directory(self, uri):
        self.directory_list.append(self.current_directory)
        self.current_directory = uri
        self.lookup_uri(uri)

    def lookup_uri(self, uri):
        self.library_strings = []
        if uri is not None:
            self.library_strings.append("..")
        self.library = self.manager.core.library.browse(uri).get()
        for lib in self.library:
            self.library_strings.append(lib.name)
        self.list_view.set_list(self.library_strings)

    def go_up_directory(self):
        if len(self.directory_list):
            directory = self.directory_list.pop()
            self.current_directory = directory
            self.lookup_uri(directory)

    def update(self, screen, update_all):
        self.list_view.render(screen)

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event)
        if clicked is not None:
            if touch_event.type == InputManager.long_click:
                if self.current_directory is not None:
                    if clicked == 0:
                        self.go_up_directory()
                    else:
                        self.play_uri(self.library[clicked - 1].uri,
                                      False)
                else:
                    self.play_uri(self.library[clicked].uri, False)
            else:
                if self.current_directory is not None:
                    if clicked == 0:
                        self.go_up_directory()
                    else:
                        if self.library[
                                    clicked - 1].type == mopidy.models.Ref.TRACK:
                            self.play_uri(
                                self.library[clicked - 1].uri, True)
                        else:
                            self.go_inside_directory(
                                self.library[clicked - 1].uri)
                else:
                    if self.library[
                        clicked].type == mopidy.models.Track:
                        self.play_uri(self.library[clicked].uri, True)
                    else:
                        self.go_inside_directory(
                            self.library[clicked].uri)

    def play_uri(self, uri, track):
        self.manager.core.tracklist.clear()
        if track:
            self.manager.core.tracklist.add(uri=uri)
            self.manager.core.playback.play()
        else:
            # TODO: add folder to tracks to play
            pass
