from base_screen import BaseScreen

from .main_screen import MainScreen
from ..graphic_utils import ListView


class Tracklist(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.list_view = ListView((0, 0), (
            self.size[0], self.size[1] -
            self.base_size), self.base_size, self.fonts['base'])
        self.tracks = []
        self.tracks_strings = []
        self.update_list()
        self.track_started(
            self.manager.core.playback.current_tl_track.get())

    def should_update(self):
        if self.list_view.should_update():
            return BaseScreen.update_partial
        else:
            return BaseScreen.no_update

    def set_update_rects(self, rects):
        self.list_view.set_update_rects(rects)

    def update(self, screen, update_type):
        update_all = (update_type == BaseScreen.update_all)
        self.list_view.render(screen, update_all)

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
            self.manager.core.playback.play(self.tracks[pos])

    def track_started(self, track):
        self.list_view.set_active(
            [self.manager.core.tracklist.index(track).get()])
