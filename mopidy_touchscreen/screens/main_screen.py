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

from ..graphic_utils import ImageView, Progressbar, \
    ScreenObjectsManager, TextItem, TouchAndTextItem
from ..graphic_utils.view_pager import ViewPager
from ..input import InputManager


logger = logging.getLogger(__name__)


class MainScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts, cache, core,
                 background):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.core = core
        self.track = None
        self.previous_track = None
        self.next_track = None
        self.cache = cache
        self.image = None
        self.artists = None
        self.update_next_frame = True
        self.background = background
        self.update_keys = []
        self.current_track_pos = 0
        self.track_duration = "00:00"
        self.view_pager = ViewPager(self.size, self)
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
        update = self.view_pager.should_update()
        if update is not BaseScreen.no_update:
            return update
        elif len(self.update_keys) > 0:
            return BaseScreen.update_partial
        else:
            if self.progress_show:
                track_pos_millis = self.core.playback.time_position.get()
                new_track_pos = track_pos_millis / 1000
                if new_track_pos != self.current_track_pos:
                    return BaseScreen.update_partial
                else:
                    return BaseScreen.no_update
            else:
                return BaseScreen.no_update

    def set_update_rects(self, rects):
        progress = self.update_progress()
        if progress is not None:
            self.update_keys = [("time_progress")]
            rects.append(progress.rect_in_pos)
        self.view_pager.set_update_rects(rects)

    def update(self, screen, update_type):
        if update_type == BaseScreen.update_all:
            screen.blit(self.top_bar, (0, 0))
            self.update_progress()
            self.touch_text_manager.render(screen)
            self.view_pager.render(screen, update_type)

        if update_type == BaseScreen.update_partial \
                and self.track is not None:
            for key in self.update_keys:
                object = self.touch_text_manager.get_touch_object(key)
                object.update()
                object.render(screen)
            self.view_pager.render(screen, update_type)

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
                    return progress
        return None

    def create_objects_manager(self):

        touch_text_manager = ScreenObjectsManager()
        x = self.size[1] - self.base_size * 3
        width = self.size[0] - self.base_size / 2 - x

        # Track name
        label = TextItem(self.fonts['base'],
                         "",
                         (x, (self.size[1]-self.base_size*3)/2
                          - self.base_size*0.5),
                         (width, -1))
        touch_text_manager.set_object("track_name", label)

        # Album name
        label = TextItem(self.fonts['base'],
                         "",
                         (x, (self.size[1]-self.base_size*3)/2
                          + self.base_size*0.5),
                         (width, -1))
        touch_text_manager.set_object("album_name", label)

        # Artist
        label = TextItem(self.fonts['base'],
                         "",
                         (x, (self.size[1]-self.base_size*3)/2
                          + self.base_size*1.5),
                         (width, -1))
        touch_text_manager.set_object("artist_name", label)

        # Cover image
        pos = (self.base_size / 2, self.base_size +
                    self.base_size / 2)
        size = self.size[1] - self.base_size * 4
        cover = ImageView(pos, (size, size))
        touch_text_manager.set_object("cover_image", cover)

        return touch_text_manager

    def set_page_values(self, screen_objects_manager, pos):
        if pos == 0:
            track = self.previous_track
        elif pos == 1:
            track = self.track
        elif pos == 2:
            track = self.next_track
        if track is None:
            return False
        else:
            screen_objects_manager.get_object("track_name").set_horizontal_shift(200)
            screen_objects_manager.get_object("track_name").set_text(MainScreen.get_track_name(track), False)
            screen_objects_manager.get_object("album_name").set_text(MainScreen.get_track_album_name(track), False)
            screen_objects_manager.get_object("artist_name").set_text(MainScreen.get_artist_string(track), False)
            return True

    def track_started(self, track):
        self.next_track = track

        self.image = None
        self.view_pager.notify_changed()

        if self.previous_track is not None and track.uri == self.previous_track.uri:
            self.view_pager.change_to_page(-1)
            image_view = self.view_pager.objets_manager[0].get_object("cover_image")
        else:
            self.view_pager.change_to_page(1)
            image_view = self.view_pager.objets_manager[2].get_object("cover_image")
        image_view.set_image(None)

        self.previous_track = self.track
        self.track = track

        # Previous track button
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61c",
                                  (0, self.size[1] - self.base_size * 2), None)
        self.touch_text_manager.set_touch_object("previous", button)
        size_1 = button.get_right_pos()

        size_2 = self.fonts['icon'].size(u"\ue61d")[0]
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61d",
                                  (self.size[0] - size_2,
                                   self.size[1] - self.base_size * 2),
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
                                   (size_1, self.size[1] - self.base_size * 2),
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

        if not self.is_image_in_cache():
            thread = Thread(target=self.download_image, args=[image_view])
            thread.start()
        else:
            thread = Thread(target=self.load_image, args=[image_view])
            thread.start()

    def stream_title_changed(self, title):
        self.touch_text_manager.get_object("track_name").set_text(title, False)

    def get_image_file_name(self):
        name = MainScreen.get_track_album_name(
            self.track) + '-' + self.get_artist_string(self.track)
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

    def download_image(self, image_view):

        image_uris = self.core.library.get_images(
            {self.track.uri}).get()[self.track.uri]
        if len(image_uris) > 0:
            urllib.urlretrieve(image_uris[0].uri,
                               self.get_cover_folder() +
                               self.get_image_file_name())
            self.load_image(image_view)
        else:
            self.download_image_last_fm(0, image_view)

    def download_image_last_fm(self, artist_index, image_view):
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
                self.load_image(image_view)
            except:
                self.download_image_last_fm(artist_index + 1, image_view)
        else:

            logger.info("Cover could not be downloaded")

    def track_playback_ended(self, tl_track, time_position):
        self.background.set_background_image(None)
        self.image = None
        self.track_duration = "00:00"

    def load_image(self, image_view):
        size = self.size[1] - self.base_size * 4
        image_original = pygame.image.load(
            self.get_cover_folder() +
            self.get_image_file_name())
        image = pygame.transform.scale(image_original, (size, size))
        image = image.convert()
        image_view.set_image(image)
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
        if track is None:
            return ""
        elif track.name is None:
            return track.uri
        else:
            return track.name

    @staticmethod
    def get_track_album_name(track):
        if track is None:
            return ""
        if track.album is not None and track.album.name is not None \
                and len(track.album.name) > 0:
            return track.album.name
        else:
            return "Unknow Album"

    @staticmethod
    def get_artist_string(track):
        artists_string = ''
        if track is None:
            return artists_string
        for artist in track.artists:
            artists_string += artist.name + ', '
        if len(artists_string) > 2:
            artists_string = artists_string[:-2]
        elif len(artists_string) == 0:
            artists_string = "Unknow Artist"
        return artists_string
