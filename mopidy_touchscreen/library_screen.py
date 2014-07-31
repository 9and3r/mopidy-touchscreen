from .list_view import ListView
import logging
import mopidy.models

logger = logging.getLogger(__name__)


class LibraryScreen():

    def __init__(self, size, base_size, manager):
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.list_view = ListView((0,self.base_size),(self.size[0],self.size[1]-2*self.base_size), self.base_size, manager.fonts)
        self.directory_list = []
        self.current_directory = None
        self.library = None
        self.library_strings = None
        self.lookup_uri(None)

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

    def update(self, screen):
        self.list_view.render(screen)

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event)
        if clicked is not None:
            if self.current_directory is not None:
                if clicked == 0:
                    self.go_up_directory()
                else:
                    if self.library[clicked-1].type == mopidy.models.Ref.TRACK:
                        self.play_uri(self.library[clicked-1].uri)
                    else:
                        self.go_inside_directory(self.library[clicked-1].uri)
            else:
                if self.library[clicked].type == mopidy.models.Track:
                    self.play_uri(self.library[clicked].uri)
                else:
                    self.go_inside_directory(self.library[clicked].uri)

    def play_uri(self, uri):
        self.manager.core.tracklist.clear()
        self.manager.core.tracklist.add(uri=uri)
        self.manager.core.playback.play()
