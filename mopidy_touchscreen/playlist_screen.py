from .list_view import ListView
from .base_screen import BaseScreen


class PlaylistScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.list_view = ListView((0, 0), (
            self.size[0], self.size[1] - self.base_size),
                                  self.base_size,
                                  self.fonts['base'])
        self.playlists_strings = []
        self.playlists = []
        self.playlists_loaded()

    def update(self, screen, update_all):
        self.list_view.render(screen)

    def playlists_loaded(self):
        self.playlists_strings = []
        self.playlists = []
        for playlist in self.manager.core.playlists.playlists.get():
            self.playlists.append(playlist)
            self.playlists_strings.append(playlist.name)
        self.list_view.set_list(self.playlists_strings)

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event)
        if clicked is not None:
            self.manager.core.tracklist.clear()
            self.manager.core.tracklist.add(
                uri=self.playlists[clicked].uri)
            self.manager.core.playback.play()
