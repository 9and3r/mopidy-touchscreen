from .list_view import ListView
import logging

logger = logging.getLogger(__name__)

mode_track_name = 0
mode_album_name = 1
mode_artist_name = 2


class SearchScreen():
    def __init__(self, size, base_size, manager):
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.list_view = ListView((0, 0), (
            self.size[0], self.size[1] - self.base_size),
                                  self.base_size,
                                  manager.fonts['base'])
        self.results_strings = []
        self.results = []

    def update(self, screen, update_all):
        self.list_view.render(screen)

    def search(self, query, mode):
        if mode == mode_track_name:
            search_query = {'any': [query]}
        elif mode == mode_album_name:
            search_query = {'album': [query]}
        else:
            search_query = {'artist': [query]}
        current_results = self.manager.core.library.search(search_query).get()
        self.results = []
        self.results_strings = []
        for backend in current_results:
            if mode == mode_track_name:
                iterable = backend.tracks
            elif mode == mode_album_name:
                iterable = backend.albums
            else:
                iterable = backend.artists

            for result in iterable:
                self.results.append(result)
                self.results_strings.append(result.name)
        self.list_view.set_list(self.results_strings)

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event)
        if clicked is not None:
            self.manager.core.tracklist.clear()
            self.manager.core.tracklist.add(
                uri=self.results[clicked].uri)
            self.manager.core.playback.play()
