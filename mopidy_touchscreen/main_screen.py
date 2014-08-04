import time
import os
from threading import Thread
import urllib
import urllib2
import json
import hashlib
import logging

import pygame

from .touch_manager import TouchManager
from .screen_objects import ScreenObjectsManager, Progressbar, \
    TouchAndTextItem, TextItem


logger = logging.getLogger(__name__)


class MainScreen():
    def __init__(self, size, manager, cache, core, fonts):
        self.core = core
        self.size = size
        self.base_size = self.size[1] / 8
        self.fonts = fonts
        self.manager = manager
        self.track = None
        self.cache = cache
        self.image = None
        self.artists = None
        self.touch_text_manager = ScreenObjectsManager()
        current_track = self.core.playback.current_track.get()
        if current_track is None:
            self.track_playback_ended(None, None)
        else:
            self.track_started(current_track)

    def update(self, screen):
        if self.track is not None:
            if self.image is not None:
                screen.blit(self.image, (
                    self.base_size / 2, self.base_size + self.base_size / 2))
            self.touch_text_manager.get_touch_object(
                "time_progress").set_value(
                self.core.playback.time_position.get() / 1000)
            self.touch_text_manager.get_touch_object("time_progress").set_text(
                time.strftime('%M:%S', time.gmtime(
                    self.core.playback.time_position.get() / 1000)) + "/" +
                time.strftime('%M:%S', time.gmtime(
                    self.track.length / 1000)))
        self.touch_text_manager.render(screen)
        return screen

    def track_started(self, track):
        self.image = None
        x = self.base_size * 5
        width = self.size[0] - self.base_size / 2 - x

        # Load all artists
        self.artists = []
        for artist in track.artists:
            self.artists.append(artist)

        # Track name
        label = TextItem(self.fonts['base'], MainScreen.get_track_name(track),
                         (x, self.base_size * 2),
                         (width, self.size[1]))
        self.touch_text_manager.set_object("track_name", label)

        # Album name
        label = TextItem(self.fonts['base'],
                         MainScreen.get_track_album_name(track),
                         (x, self.base_size * 3),
                         (width, self.size[1]))
        self.touch_text_manager.set_object("album_name", label)

        # Artist
        label = TextItem(self.fonts['base'], self.get_artist_string(),
                         (x, self.base_size * 4), (width, self.size[1]))
        self.touch_text_manager.set_object("artist_name", label)

        # Previous track button
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61c",
                                  (0, self.base_size * 6), None)
        self.touch_text_manager.set_touch_object("previous", button)
        size_1 = button.get_right_pos()

        size_2 = self.fonts['icon'].size(u"\ue61d")[0]
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61d",
                                  (self.size[0] - size_2, self.base_size * 6),
                                  None)
        self.touch_text_manager.set_touch_object("next", button)

        # Progress
        progress = Progressbar(self.fonts['base'],
                               time.strftime('%M:%S', time.gmtime(
                                   0)) + "/" + time.strftime('%M:%S',
                                                             time.gmtime(0)),
                               (size_1, self.base_size * 6),
                               (
                               self.size[0] - size_1 - size_2, self.base_size),
                               track.length / 1000, False)
        self.touch_text_manager.set_touch_object("time_progress", progress)

        self.track = track
        if not self.is_image_in_cache():
            thread = Thread(target=self.download_image(0))
            thread.start()
        else:
            self.load_image()

    def get_artist_string(self):
        artists_string = ''
        for artist in self.artists:
            artists_string += artist.name + ', '
        if len(artists_string) > 2:
            artists_string = artists_string[:-2]
        elif len(artists_string) == 0:
            artists_string = "Unknow Artist"
        return artists_string

    def get_image_file_name(self):
        name = MainScreen.get_track_album_name(
            self.track) + '-' + self.get_artist_string()
        md5name = hashlib.md5(name.encode('utf-8')).hexdigest()
        return md5name

    def get_cover_folder(self):
        if not os.path.isdir(self.cache + "/covers"):
            os.makedirs(self.cache + "/covers")
        return self.cache + "/covers/"

    def is_image_in_cache(self):
        self.get_cover_folder()
        return os.path.isfile(
            self.get_cover_folder() + self.get_image_file_name())

    def download_image(self, artist_index):
        if artist_index < len(self.artists):
            try:
                safe_artist = urllib.quote_plus(
                    self.artists[artist_index].name)
                safe_album = urllib.quote_plus(
                    MainScreen.get_track_album_name(self.track))
                url = "http://ws.audioscrobbler.com/2.0/?"
                params = "method=album.getinfo&" + \
                         "api_key=59a04c6a73fb99d6e8996e01db306829&" \
                         + "artist=" \
                         + safe_artist + "&album=" + safe_album + \
                         "&format=json"
                response = urllib2.urlopen(url + params)
                data = json.load(response)
                image = data['album']['image'][-1]['#text']
                urllib.urlretrieve(image,
                                   self.get_cover_folder() +
                                   self.get_image_file_name())
                self.load_image()
            except:
                self.download_image(artist_index + 1)
        else:

            logger.info("Cover could not be downloaded")

            # There is no cover so it will use all the screen size for the text
            width = self.size[0] - self.base_size

            current = TextItem(self.fonts['base'],
                               MainScreen.get_track_name(self.track),
                               (self.base_size / 2, self.base_size * 2),
                               (width, -1))
            self.touch_text_manager.set_object("track_name", current)

            current = TextItem(self.fonts['base'],
                               MainScreen.get_track_album_name(self.track),
                               (self.base_size / 2, self.base_size * 3),
                               (width, -1))
            self.touch_text_manager.set_object("album_name", current)

            current = TextItem(self.fonts['base'], self.get_artist_string(),
                               (self.base_size / 2, self.base_size * 4),
                               (width, -1))
            self.touch_text_manager.set_object("artist_name", current)

    def track_playback_ended(self, tl_track, time_position):

        self.image = None

        # There is no cover so it will use all the screen size for the text
        width = self.size[0] - self.base_size

        current = TextItem(self.fonts['base'], "Stopped",
                           (self.base_size / 2, self.base_size * 2),
                           (width, -1))
        self.touch_text_manager.set_object("track_name", current)

        current = TextItem(self.fonts['base'], "",
                           (self.base_size / 2, self.base_size * 3),
                           (width, -1))
        self.touch_text_manager.set_object("album_name", current)

        current = TextItem(self.fonts['base'], "",
                           (self.base_size / 2, self.base_size * 4),
                           (width, -1))
        self.touch_text_manager.set_object("artist_name", current)

    def load_image(self):
        size = self.base_size * 4
        self.image = pygame.transform.scale(
            pygame.image.load(
                self.get_cover_folder() +
                self.get_image_file_name()).convert(),
            (size, size))

    def touch_event(self, event):
        if event.type == TouchManager.click:
            objects = self.touch_text_manager.get_touch_objects_in_pos(
                event.current_pos)
            if objects is not None:
                for key in objects:
                    if key == "time_progress":
                        value = self.touch_text_manager.get_touch_object(
                            key).get_pos_value(event.current_pos) * 1000
                        self.core.playback.seek(value)
                    elif key == "previous":
                        self.core.playback.previous()
                    elif key == "next":
                        self.core.playback.next()
        elif event.type == TouchManager.swipe:
            if event.direction == TouchManager.left:
                self.core.playback.next()
            elif event.direction == TouchManager.right:
                self.core.playback.previous()
            elif event.direction == TouchManager.up:
                volume = self.core.playback.volume.get() + 10
                if volume > 100:
                    volume = 100
                self.manager.backend.tell(
                    {'action': 'volume', 'value': volume})
                self.manager.volume_changed(volume)
            elif event.direction == TouchManager.down:
                volume = self.core.playback.volume.get() - 10
                if volume < 0:
                    volume = 0
                self.manager.backend.tell(
                    {'action': 'volume', 'value': volume})
                self.manager.volume_changed(volume)

    @staticmethod
    def get_track_name(track):
        if track.name is None:
            return track.uri
        else:
            return track.name

    @staticmethod
    def get_track_album_name(track):
        if track.album is not None and track.album.name is not None and len(
                track.album.name) > 0:
            return track.album.name
        else:
            return "Unknow Album"
