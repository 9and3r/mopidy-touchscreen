from base_screen import BaseScreen

from ..graphic_utils import ListView

import mopidy.models


class LibraryScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.list_view = ListView((0, 0), (
            self.size[0], self.size[1] -
            self.base_size), self.base_size, self.fonts['base'])
        self.directory_list = []
        self.current_directory = None
        self.library = None
        self.library_strings = None
        self.browse_uri(None)

    def go_inside_directory(self, uri):
        self.directory_list.append(self.current_directory)
        self.current_directory = uri
        self.browse_uri(uri)

    def browse_uri(self, uri):
        self.library_strings = []
        if uri is not None:
            self.library_strings.append("../")
        self.library = self.manager.core.library.browse(uri).get()
        for lib in self.library:
            self.library_strings.append(lib.name)
        self.list_view.set_list(self.library_strings)

    def go_up_directory(self):
        if len(self.directory_list):
            directory = self.directory_list.pop()
            self.current_directory = directory
            self.browse_uri(directory)

    def update(self, screen):
        self.list_view.render(screen)

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event)
        if clicked is not None:
            if self.current_directory is not None:
                if clicked == 0:
                    self.go_up_directory()
                else:
                    if self.library[clicked - 1].type\
                            == mopidy.models.Ref.TRACK:
                        self.play_uri(clicked-1)
                    else:
                        self.go_inside_directory(
                            self.library[clicked - 1].uri)
            else:
                self.go_inside_directory(self.library[clicked].uri)

    def play_uri(self, track_pos):
        self.manager.core.tracklist.clear()
        tracks = []
        for item in self.library:
            if item.type == mopidy.models.Ref.TRACK:
                tracks.append(self.manager.core.library.lookup(
                    item.uri).get()[0])
            else:
                track_pos -= 1
        self.manager.core.tracklist.add(tracks)
        self.manager.core.playback.play(
            tl_track=self.manager.core.tracklist.tl_tracks.get()
            [track_pos])
