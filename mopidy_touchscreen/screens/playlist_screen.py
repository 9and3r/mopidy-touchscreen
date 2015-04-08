from base_screen import BaseScreen

from ..graphic_utils import ListView


class PlaylistScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.list_view = ListView((0, 0), (
            self.size[0], self.size[1] -
            self.base_size), self.base_size,
            self.fonts['base'])
        self.playlists_strings = []
        self.playlists = []
        self.playlists_loaded()
        self.selected_playlist = None
        self.playlist_tracks = []
        self.playlist_tracks_strings = []

    def update(self, screen):
        self.list_view.render(screen)

    def playlists_loaded(self):
        self.selected_playlist = None
        self.playlists_strings = []
        self.playlists = []
        for playlist in self.manager.core.playlists.playlists.get():
            self.playlists.append(playlist)
            self.playlists_strings.append(playlist.name)
        self.list_view.set_list(self.playlists_strings)

    def playlist_selected(self, playlist):
        self.selected_playlist = playlist
        self.playlist_tracks = playlist.tracks
        self.playlist_tracks_strings = ["../"]
        for track in self.playlist_tracks:
            self.playlist_tracks_strings.append(track.name)
        self.list_view.set_list(self.playlist_tracks_strings)

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event)
        if clicked is not None:
            if self.selected_playlist is None:
                self.playlist_selected(self.playlists[clicked])
            else:
                if clicked == 0:
                    self.selected_playlist = None
                    self.list_view.set_list(self.playlists_strings)
                else:
                    self.manager.core.tracklist.clear()
                    self.manager.core.tracklist.add(
                        self.playlist_tracks)
                    self.manager.core.playback.play(
                        tl_track=self.manager.core.
                        tracklist.tl_tracks.get()
                        [clicked-1])
