from .list_view import ListView
from .main_screen import MainScreen
from .base_screen import BaseScreen


class Tracklist(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.list_view = ListView((0, 0), (
            self.size[0], self.size[1] - self.base_size), self.base_size, self.fonts['base'])
        self.tracks = []
        self.tracks_strings = []
        self.update_list()

    def update(self, screen, update_all):
        self.list_view.render(screen)

    def tracklist_changed(self):
        self.update_list()

    def update_list(self):
        self.tracks = self.manager.core.tracklist.tl_tracks.get()
        self.tracks_strings = []
        for tl_track in self.tracks:
            self.tracks_strings.append(
                MainScreen.get_track_name(tl_track.track))
        self.list_view.set_list(self.tracks_strings)

    def touch_event(self, touch_event):
        pos = self.list_view.touch_event(touch_event)
        if pos is not None:
            self.manager.core.playback.change_track(self.tracks[pos],
                                                    on_error_step=1)

    def track_started(self, track):
        self.list_view.set_selected(
            [self.manager.core.tracklist.index(track).get()])
