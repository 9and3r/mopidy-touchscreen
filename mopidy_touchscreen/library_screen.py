from .list_view import ListView
import logging

logger = logging.getLogger(__name__)

class LibraryScreen():

    def __init__(self, size, base_size, manager):
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.list_view = ListView((0,self.base_size),(self.size[0],self.size[1]-2*self.base_size), self.base_size, manager.fonts)
        self.directory_list = []
        self.library = None
        self.library_strings = None
        self.lookup_uri(None)

    def lookup_uri(self, uri):
        self.library_strings = []
        if uri is not None:
            self.directory_list.append(uri)
            self.library_strings.append("..")
        self.library = self.manager.core.library.browse(uri).get()
        for lib in self.library:
            self.library_strings.append(lib.name)
        self.list_view.set_list(self.library_strings)

    def go_up_directory(self):
        if len(self.directory_list) > 0:
            self.lookup_uri(self.directory_list.pop())
        else:
            self.lookup_uri(None)

    def update(self, screen):
        self.list_view.render(screen)

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event)
        if clicked is not None:
            if len(self.directory_list) > 0:
                if clicked == 0:
                    self.go_up_directory()
                else:
                    self.lookup_uri(self.library[clicked-1].uri)
            else:
                self.lookup_uri(self.library[clicked].uri)
