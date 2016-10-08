import hashlib
import json
import logging
import os
import time
import urllib
import urllib2
from threading import Thread


from base_screen import BaseScreen

import mopidy.core

import pygame

from ..graphic_utils import Progressbar, \
    ScreenObjectsManager, TextItem, TouchAndTextItem
from ..input import InputManager


logger = logging.getLogger(__name__)


class MainScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts, cache, core,
                 background):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.core = core
        self.track = None
        self.cache = cache
        self.image = None
        self.artists = None
        self.update_next_frame = True
        self.background = background
        self.update_keys = []
        self.current_track_pos = 0
        self.track_duration = "00:00"
        self.has_to_update_progress = False
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
        self.progress_show = False



    def should_update(self):
        if len(self.update_keys) > 0:
            if self.update_progress():
                self.has_to_update_progress = True
            return True
        else:
            if self.progress_show:
                if self.update_progress():
                    self.has_to_update_progress = True
                    return True
                else:
                    return False
            else:
                return False

    def find_update_rects(self, rects):
        for key in self.update_keys:
            object = self.touch_text_manager.get_object(key)
            rects.append(object.rect_in_pos)
        if self.progress_show and self.has_to_update_progress :
            object = self.touch_text_manager.get_touch_object("time_progress")
            print object.rect_in_pos
            rects.append(object.rect_in_pos)

    def update(self, screen, update_type, rects):
        if update_type == BaseScreen.update_all:
            screen.blit(self.top_bar, (0, 0))
            self.update_progress()
            self.has_to_update_progress = False
            self.touch_text_manager.render(screen)
            if self.image is not None:
                screen.blit(self.image, (
                    self.base_size / 2, self.base_size +
                    self.base_size / 2))

        if update_type == BaseScreen.update_partial \
                and self.track is not None:

            if self.has_to_update_progress:
                self.touch_text_manager.get_touch_object(
                    "time_progress").render(screen)
                self.has_to_update_progress = False
            for key in self.update_keys:
                object = self.touch_text_manager.get_object(key)
                object.update()
                object.render(screen)

    def update_progress(self):
        if self.progress_show:
                track_pos_millis = self.core.playback.time_position.get()
                new_track_pos = track_pos_millis / 1000

                if new_track_pos != self.current_track_pos:
                    progress = self.touch_text_manager.get_touch_object(
                        "time_progress")
                    progress.set_value(track_pos_millis)
                    self.current_track_pos = new_track_pos
                    progress.set_text(
                        time.strftime('%M:%S', time.gmtime(
                            self.current_track_pos)) +
                        "/" + self.track_duration)
                    return True
        return False

    def track_started(self, track):
        self.update_keys = []
        self.image = None
        x = self.size[1] - self.base_size * 2
        width = self.size[0] - self.base_size / 2 - x

        # Previous track button
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61c",
                                  (0, self.size[1] - self.base_size), None)
        self.touch_text_manager.set_touch_object("previous", button)
        size_1 = button.get_right_pos()

        size_2 = self.fonts['icon'].size(u"\ue61d")[0]
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61d",
                                  (self.size[0] - size_2,
                                   self.size[1] - self.base_size),
                                  None)
        self.touch_text_manager.set_touch_object("next", button)

        if track.length:
            self.track_duration = time.strftime('%M:%S', time.gmtime(
                track.length / 1000))

            # Progress
            progress = Progressbar(self.fonts['base'],
                                   time.strftime('%M:%S', time.gmtime(
                                       0)) + "/" + time.strftime(
                                   '%M:%S', time.gmtime(0)),
                                   (size_1, self.size[1] - self.base_size),
                                   (
                                   self.size[0] - size_1 - size_2,
                                   self.base_size),
                                   track.length, False)
            self.touch_text_manager.set_touch_object("time_progress",
                                                     progress)
            self.progress_show = True
        else:
            self.progress_show = False
            self.touch_text_manager.delete_touch_object("time_progress")

        # Load all artists
        self.artists = []
        for artist in track.artists:
            self.artists.append(artist)

        # Track name
        label = TextItem(self.fonts['base'],
                         MainScreen.get_track_name(track),
                         (x, (self.size[1]-self.base_size*3)/2
                          - self.base_size*0.5),
                         (width, -1))
        if not label.fit_horizontal:
            self.update_keys.append("track_name")
        self.touch_text_manager.set_object("track_name", label)

        # Album name
        label = TextItem(self.fonts['base'],
                         MainScreen.get_track_album_name
                         (track),
                         (x, (self.size[1]-self.base_size*3)/2
                          + self.base_size*0.5),
                         (width, -1))
        if not label.fit_horizontal:
            self.update_keys.append("album_name")
        self.touch_text_manager.set_object("album_name", label)

        # Artist
        label = TextItem(self.fonts['base'],
                         self.get_artist_string(),
                         (x, (self.size[1]-self.base_size*3)/2
                          + self.base_size*1.5),
                         (width, -1))
        if not label.fit_horizontal:
            self.update_keys.append("artist_name")
        self.touch_text_manager.set_object("artist_name", label)

        self.track = track
        if not self.is_image_in_cache():
            thread = Thread(target=self.download_image)
            thread.start()
        else:
            thread = Thread(target=self.load_image)
            thread.start()

    def stream_title_changed(self, title):
        self.touch_text_manager.get_object("track_name").set_text(title, False)

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

    def download_image(self):
        image_uris = self.core.library.get_images(
            {self.track.uri}).get()[self.track.uri]
        if len(image_uris) > 0:
            urllib.urlretrieve(image_uris[0].uri,
                               self.get_cover_folder() +
                               self.get_image_file_name())
            self.load_image()
        else:
            self.download_image_last_fm(0)

    def download_image_last_fm(self, artist_index):
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
                self.download_image_last_fm(artist_index + 1)
        else:

            logger.info("Cover could not be downloaded")

            # There is no cover
            # so it will use all the screen size for the text
            width = self.size[0] - self.base_size

            current = TextItem(self.fonts['base'],
                               MainScreen.get_track_name
                               (self.track),
                               (self.base_size / 2,
                                self.base_size * 2),
                               (width, -1))
            if not current.fit_horizontal:
                self.update_keys.append("track_name")
            self.touch_text_manager.set_object("track_name", current)

            current = TextItem(self.fonts['base'],
                               MainScreen.get_track_album_name
                               (self.track),
                               (self.base_size / 2,
                                self.base_size * 3),
                               (width, -1))
            if not current.fit_horizontal:
                self.update_keys.append("album_name")
            self.touch_text_manager.set_object("album_name", current)

            current = TextItem(self.fonts['base'],
                               self.get_artist_string(),
                               (self.base_size / 2,
                                self.base_size * 4),
                               (width, -1))
            if not current.fit_horizontal:
                self.update_keys.append("artist_name")
            self.touch_text_manager.set_object("artist_name", current)

            self.background.set_background_image(None)

    def track_playback_ended(self, tl_track, time_position):
        self.background.set_background_image(None)
        self.image = None
        self.track_duration = "00:00"

        width = self.size[0] - self.base_size

        current = TextItem(self.fonts['base'], "",
                           (self.base_size / 2,
                            self.base_size * 2),
                           (width, -1))
        self.touch_text_manager.set_object("track_name", current)

        current = TextItem(self.fonts['base'], "",
                           (self.base_size / 2,
                            self.base_size * 3),
                           (width, -1))
        self.touch_text_manager.set_object("album_name", current)

        current = TextItem(self.fonts['base'], "",
                           (self.base_size / 2,
                            self.base_size * 4),
                           (width, -1))
        self.touch_text_manager.set_object("artist_name", current)

    def load_image(self):
        size = self.size[1] - self.base_size * 3
        image_original = pygame.image.load(
            self.get_cover_folder() +
            self.get_image_file_name())
        image = pygame.transform.scale(image_original, (size, size))
        image = image.convert()
        self.image = image
        self.background.set_background_image(image_original)

    def touch_event(self, event):
        if event.type == InputManager.click:
            objects = \
                self.touch_text_manager.get_touch_objects_in_pos(
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
                self.core.mixer.set_volume(volume)
            elif event.direction == InputManager.down:
                volume = self.core.playback.volume.get() - 10
                if volume < 0:
                    volume = 0
                self.core.mixer.set_volume(volume)
        elif event.type == InputManager.key:
            if event.direction == InputManager.enter:
                self.click_on_objects(["pause_play"], None)
            elif event.direction == InputManager.up:
                vol = self.core.mixer.get_volume().get()
                vol += 3
                if vol > 100:
                    vol = 100
                self.core.mixer.set_volume(vol)
            elif event.direction == InputManager.down:
                vol = self.core.mixer.get_volume().get()
                vol -= 3
                if vol < 0:
                    vol = 0
                self.core.mixer.set_volume(vol)
            elif event.longpress:
                if event.direction == InputManager.left:
                    self.click_on_objects(["previous"], None)
                elif event.direction == InputManager.right:
                    self.click_on_objects(["next"], None)

    def click_on_objects(self, objects, event):
        if objects is not None:
            for key in objects:
                if key == "time_progress":
                    value = self.touch_text_manager.get_touch_object(
                        key).get_pos_value(
                        event.current_pos)
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

    def change_volume(self, event):
        manager = self.touch_text_manager
        volume = manager.get_touch_object("volume")
        pos = event.current_pos
        value = volume.get_pos_value(pos)
        self.core.mixer.set_volume(value)

    def playback_state_changed(self, old_state, new_state):
        if new_state == mopidy.core.PlaybackState.PLAYING:
            self.touch_text_manager.get_touch_object(
                "pause_play").set_text(u"\ue616", False)
        else:
            self.touch_text_manager.get_touch_object(
                "pause_play").set_text(u"\ue615", False)

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

    def mute_changed(self, mute):
        self.touch_text_manager.get_touch_object("mute").set_active(
            not mute)
        if mute:
            self.touch_text_manager.get_touch_object("mute").set_text(
                u"\ue623", False)
        else:
            self.volume_changed(self.core.playback.volume.get())

    @staticmethod
    def get_track_name(track):
        if track.name is None:
            return track.uri
        else:
            return track.name

    @staticmethod
    def get_track_album_name(track):
        if track.album is not None and track.album.name is not None \
                and len(track.album.name) > 0:
            return track.album.name
        else:
            return "Unknow Album"
