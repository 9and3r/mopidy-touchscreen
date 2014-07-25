from .list_view import ListView


class Tracklist():

    def __init__(self, size, base_size, manager):
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.list_view = ListView((0,self.base_size),(self.size[0],self.size[1]-2*self.base_size), self.base_size, manager.fonts)
        self.tracks = []
        self.update_list()

    def update(self, screen):
        self.list_view.render(screen)

    def tracklist_changed(self):
        self.update_list()

    def update_list(self):
        self.tracks = self.manager.core.tracklist.tl_tracks.get()
        self.tracks_strings = []
        for tl_track in self.tracks:
            self.tracks_strings.append(tl_track.track.name)
        self.list_view.set_list(self.tracks_strings)

    def touch_event(self, touch_event):
        self.list_view.touch_event(touch_event)