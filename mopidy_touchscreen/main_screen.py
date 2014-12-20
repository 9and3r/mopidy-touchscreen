import hashlib
import json
import logging
import os
import time
import mopidy.core
import urllib
import urllib2
from threading import Thread
import pygame
from .base_screen import BaseScreen

from .screen_objects import (Progressbar, ScreenObjectsManager,
                             TextItem,
                             TouchAndTextItem)
from .input_manager import InputManager


logger = logging.getLogger(__name__)


class MainScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts, cache, core):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.core = core
        self.track = None
        self.cache = cache
        self.image = None
        self.artists = None
        self.track_duration = "00:00"
        self.touch_text_manager = ScreenObjectsManager()
        current_track = self.core.playback.current_track.get()
        if current_track is None:
            self.track_playback_ended(None, None)
        else:
            self.track_started(current_track)
            
            
        # Top bar
        self.top_bar = pygame.Surface((self.size[0], self.base_size),
                                      pygame.SRCALPHA)
        self.top_bar.fill((0, 0, 0, 128))

        # Play/pause
        button = TouchAndTextItem(self.fonts['icon'], u"\ue615 ",
                                  (0, 0), None)
        self.touch_text_manager.set_touch_object("pause_play", button)
        x = button.get_right_pos()

        # Random
        button = TouchAndTextItem(self.fonts['icon'], u"\ue629 ",
                                  (x, 0), None)
        self.touch_text_manager.set_touch_object("random", button)
        x = button.get_right_pos()

        # Repeat
        button = TouchAndTextItem(self.fonts['icon'], u"\ue626",
                                  (x, 0), None)
        self.touch_text_manager.set_touch_object("repeat", button)
        x = button.get_right_pos()

        # Single
        button = TouchAndTextItem(self.fonts['base'], " 1 ", (x, 0),
                                  None)
        self.touch_text_manager.set_touch_object("single", button)
        x = button.get_right_pos()

        # Internet
        button = TouchAndTextItem(self.fonts['icon'], u"\ue602 ",
                                  (x, 0), None)
        self.touch_text_manager.set_touch_object("internet", button)
        x = button.get_right_pos()

        # Mute
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61f ",
                                  (x, 0), None)
        self.touch_text_manager.set_touch_object("mute", button)
        x = button.get_right_pos()

        # Volume
        progress = Progressbar(self.fonts['base'], "100", (x, 0),
                               (self.size[0] - x, self.base_size),
                               100, True)
        self.touch_text_manager.set_touch_object("volume", progress)
        progress.set_value(self.core.playback.volume.get())

    def update(self, screen, update_all):
        screen.blit(self.top_bar, (0, 0))
        if self.track is not None:
            self.touch_text_manager.get_touch_object(
                "time_progress").set_value(
                self.core.playback.time_position.get() / 1000)
            self.touch_text_manager.get_touch_object(
                "time_progress").set_text(
                time.strftime('%M:%S', time.gmtime(
                    self.core.playback.time_position.get() / 1000)) + "/" + self.track_duration)
            if self.image is not None:
                screen.blit(self.image, (
                    self.base_size / 2, self.base_size + self.base_size / 2))
        self.touch_text_manager.render(screen)
        return screen

    def track_started(self, track):
        self.image = None
        x = self.base_size * 5
        width = self.size[0] - self.base_size / 2 - x

        self.track_duration = time.strftime('%M:%S', time.gmtime(
            track.length / 1000))

        # Load all artists
        self.artists = []
        for artist in track.artists:
            self.artists.append(artist)

        # Track name
        label = TouchAndTextItem(self.fonts['base'],
                         MainScreen.get_track_name(track),
                         (x, self.base_size * 2),
                         (width, -1))
        self.touch_text_manager.set_touch_object("track_name", label)

        # Album name
        label = TouchAndTextItem(self.fonts['base'],
                         MainScreen.get_track_album_name(track),
                         (x, self.base_size * 3),
                         (width, -1))
        self.touch_text_manager.set_touch_object("album_name", label)

        # Artist
        label = TouchAndTextItem(self.fonts['base'], self.get_artist_string(),
                         (x, self.base_size * 4),
                         (width, -1))
        self.touch_text_manager.set_touch_object("artist_name", label)

        # Previous track button
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61c",
                                  (0, self.base_size * 6), None)
        self.touch_text_manager.set_touch_object("previous", button)
        size_1 = button.get_right_pos()

        size_2 = self.fonts['icon'].size(u"\ue61d")[0]
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61d",
                                  (self.size[0] - size_2,
                                   self.base_size * 6),
                                  None)
        self.touch_text_manager.set_touch_object("next", button)

        # Progress
        progress = Progressbar(self.fonts['base'],
                               time.strftime('%M:%S', time.gmtime(
                                   0)) + "/" + time.strftime('%M:%S',
                                                             time.gmtime(
                                                                 0)),
                               (size_1, self.base_size * 6),
                               (
                                   self.size[0] - size_1 - size_2,
                                   self.base_size),
                               track.length / 1000, False)
        self.touch_text_manager.set_touch_object("time_progress",
                                                 progress)

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

            current = TouchAndTextItem(self.fonts['base'],
                               MainScreen.get_track_name(self.track),
                               (self.base_size / 2,
                                self.base_size * 2),
                               (width, -1))
            self.touch_text_manager.set_touch_object("track_name", current)

            current = TouchAndTextItem(self.fonts['base'],
                               MainScreen.get_track_album_name(
                                   self.track),
                               (self.base_size / 2,
                                self.base_size * 3),
                               (width, -1))
            self.touch_text_manager.set_touch_object("album_name", current)

            current = TouchAndTextItem(self.fonts['base'],
                               self.get_artist_string(),
                               (self.base_size / 2,
                                self.base_size * 4),
                               (width, -1))
            self.touch_text_manager.set_touch_object("artist_name", current)

    def track_playback_ended(self, tl_track, time_position):
        if self.image is not None:
            self.dirty_area.append(pygame.Rect(self.base_size / 2,
                                               self.base_size + self.base_size / 2,
                                               self.image.get_rect().width,
                                               self.image.get_rect().height))
            self.image = None

        self.track_duration = "00:00"

        width = self.size[0] - self.base_size

        current = TouchAndTextItem(self.fonts['base'], "",
                           (self.base_size / 2, self.base_size * 2),
                           (width, -1))
        self.touch_text_manager.set_touch_object("track_name", current)

        current = TouchAndTextItem(self.fonts['base'], "",
                           (self.base_size / 2, self.base_size * 3),
                           (width, -1))
        self.touch_text_manager.set_touch_object("album_name", current)

        current = TouchAndTextItem(self.fonts['base'], "",
                           (self.base_size / 2, self.base_size * 4),
                           (width, -1))
        self.touch_text_manager.set_touch_object("artist_name", current)

    def load_image(self):
        size = self.base_size * 4
        self.image = pygame.transform.scale(
            pygame.image.load(
                self.get_cover_folder() +
                self.get_image_file_name()).convert(),
            (size, size))

    def touch_event(self, event):
        if event.type == InputManager.click:
            objects = self.touch_text_manager.get_touch_objects_in_pos(
                event.current_pos)
            if objects is not None:
                self.click_on_objects(objects, event)

        elif event.type == InputManager.swipe:
            if event.direction == InputManager.left:
                self.core.playback.next()
            elif event.direction == InputManager.right:
                self.core.playback.previous()
            elif event.direction == InputManager.up:
                volume = self.core.playback.volume.get() + 10
                if volume > 100:
                    volume = 100
                self.core.playback.volume = volume
                self.manager.volume_changed(volume)
            elif event.direction == InputManager.down:
                volume = self.core.playback.volume.get() - 10
                if volume < 0:
                    volume = 0
                self.core.playback.volume = volume
                self.manager.volume_changed(volume)
                
    def click_on_objects(self, objects, event):
        if objects is not None:
            for key in objects:
                if key == "time_progress":
                    value = self.touch_text_manager.get_touch_object(
                     key).get_pos_value(
                        event.current_pos) * 1000
                    self.core.playback.seek(value)

                elif key == "previous":
                    self.core.playback.previous()
                elif key == "next":
                    self.core.playback.next()
                elif key == "volume":
                    self.change_volume(event)
                elif key == "pause_play":
                    if self.core.playback.state.get() == \
                            mopidy.core.PlaybackState.PLAYING:
                        self.core.playback.pause()
                    else:
                        self.core.playback.play()
                elif key == "mute":
                    mute = not self.core.playback.mute.get()
                    self.core.playback.set_mute(mute)
                    self.mute_changed(mute)
                elif key == "random":
                    random = not self.core.tracklist.random.get()
                    self.core.tracklist.set_random(random)
                    self.options_changed()
                elif key == "repeat":
                    self.core.tracklist.set_repeat(
                        not self.core.tracklist.repeat.get())
                elif key == "single":
                    self.core.tracklist.set_single(
                        not self.core.tracklist.single.get())
                elif key == "internet":
                    self.manager.check_connection()
                elif key == "track_name":
                    self.manager.search(self.track.name, 0)
                elif key == "album_name":
                    self.manager.search(self.track.album.name, 1)
                elif key == "artist_name":
                    self.manager.search(self.get_artist_string(), 2)

    def change_volume(self, event):
        manager = self.touch_text_manager
        volume = manager.get_touch_object("volume")
        pos = event.current_pos
        value = volume.get_pos_value(pos)
        self.core.playback.volume = value
        self.volume_changed(value)
        
    def volume_changed(self, volume):
        if not self.core.playback.mute.get():
            if volume > 80:
                self.touch_text_manager.get_touch_object(
                    "mute").set_text(
                    u"\ue61f", False)
            elif volume > 50:
                self.touch_text_manager.get_touch_object(
                    "mute").set_text(
                    u"\ue620", False)
            elif volume > 20:
                self.touch_text_manager.get_touch_object(
                    "mute").set_text(
                    u"\ue621", False)
            else:
                self.touch_text_manager.get_touch_object(
                    "mute").set_text(
                    u"\ue622", False)
        self.touch_text_manager.get_touch_object("volume").set_value(
            volume)
        
    def options_changed(self):
        self.touch_text_manager.get_touch_object("random").set_active(
            self.core.tracklist.random.get())
        self.touch_text_manager.get_touch_object("repeat").set_active(
            self.core.tracklist.repeat.get())
        self.touch_text_manager.get_touch_object("single").set_active(
            self.core.tracklist.single.get())

    def mute_changed(self, mute):
        self.touch_text_manager.get_touch_object("mute").set_active(
            not mute)
        if mute:
            self.touch_text_manager.get_touch_object("mute").set_text(
                u"\ue623", False)
        else:
            self.volume_changed(self.core.playback.volume.get())
            
    def playback_state_changed(self, old_state, new_state):
        if new_state == mopidy.core.PlaybackState.PLAYING:
            self.touch_text_manager.get_touch_object(
                "pause_play").set_text(u"\ue616", False)
        else:
            self.touch_text_manager.get_touch_object(
                "pause_play").set_text(u"\ue615", False)
                                
    def set_connection(self, connection, loading):
        internet = self.touch_text_manager.get_touch_object("internet")
        if loading:
            internet.set_text(u"\ue627", None)
            internet.set_active(False)
        else:
            internet.set_text(u"\ue602", None)
            internet.set_active(connection)


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
