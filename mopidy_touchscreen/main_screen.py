import pygame
import logging
import hashlib
import time
import os
from threading import Thread
import urllib
import urllib2
import json
from mopidy.audio import PlaybackState
from .touch_manager import TouchManager
from .screen_objects import *


logger = logging.getLogger(__name__)


class MainScreen():

    def __init__(self, size, manager, cache, core, fonts):
        self.core = core
        self.size = size
        self.base_size = self.size[1]/8
        self.fonts = fonts
        self.manager = manager
        self.track = None
        self.cache = cache
        self.image = None
        self.touch_text_manager = ScreenObjectsManager()


    def update(self, screen):
        if self.track is not None:
            if self.image is not None:
                screen.blit(self.image, (self.base_size/2, self.base_size + self.base_size/2))
            self.touch_text_manager.get_touch_object("time_progress").set_value(self.core.playback.time_position.get()/1000)
            self.touch_text_manager.get_touch_object("time_progress").set_text(time.strftime('%M:%S', time.gmtime(self.core.playback.time_position.get()/1000))+"/"+time.strftime('%M:%S', time.gmtime(self.track.length/1000)))
        self.touch_text_manager.render(screen)
        return screen

    def track_started(self, track):
        self.image = None
        x = self.base_size * 5
        width = self.size[0]-self.base_size / 2-x

        #Track name
        label = TextItem(self.fonts['base'],track.name,(x,self.base_size*2), (width,self.size[1]))
        self.touch_text_manager.set_object("track_name", label)

        #Album name
        label = TextItem(self.fonts['base'],track.album.name,(x,self.base_size*3), (width,self.size[1]))
        self.touch_text_manager.set_object("album_name",label)

        #Artist
        label = TextItem(self.fonts['base'],self.getFirstArtist(track),(x,self.base_size*4), (width,self.size[1]))
        self.touch_text_manager.set_object("artist_name",label)

        #Previous track button
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61c", (0, self.base_size * 6), None)
        self.touch_text_manager.set_touch_object("previous", button)
        size_1 = button.get_right_pos()

        size_2 = self.fonts['icon'].size(u"\ue61d")[0]
        button = TouchAndTextItem(self.fonts['icon'], u"\ue61d", (self.size[0] - size_2, self.base_size * 6), None)
        self.touch_text_manager.set_touch_object("next", button)

        #Progress
        progress = Progressbar(self.fonts['base'],time.strftime('%M:%S', time.gmtime(0))+"/"+time.strftime('%M:%S', time.gmtime(0)),(size_1, self.base_size*6), (self.size[0] - size_1- size_2,self.base_size),track.length/1000, False)
        self.touch_text_manager.set_touch_object("time_progress", progress)

        self.track = track
        if not self.is_image_in_cache():
            thread = Thread(target=self.downloadImage())
            thread.start()
        else:
            self.loadImage()


    def getFirstArtist(self,track):
        if track is None:
            artist = next(iter(self.track.artists)).name
        else:
            artist = next(iter(track.artists)).name
        return artist


    def getImageFileName(self):
        name = self.track.album.name + '-' + self.getFirstArtist(None)
        md5name = hashlib.md5(name).hexdigest()
        return md5name

    def getCoverFolder(self):
        if(not os.path.isdir(self.cache+"/covers")):
            os.makedirs(self.cache+"/covers")
        return self.cache+"/covers/"

    def is_image_in_cache(self):
        self.getCoverFolder()
        return os.path.isfile(self.getCoverFolder()+self.getImageFileName())

    def downloadImage(self):
        try:
            safe_artist=urllib.quote_plus(self.getFirstArtist(self.track))
            safe_album=urllib.quote_plus(self.track.album.name)
            url="http://ws.audioscrobbler.com/2.0/?"
            params="method=album.getinfo&api_key=59a04c6a73fb99d6e8996e01db306829&artist="+safe_artist+"&album="+safe_album+"&format=json"
            response = urllib2.urlopen(url+params)
            data = json.load(response)
            image = data['album']['image'][-1]['#text']
            urllib.urlretrieve(image, self.getCoverFolder()+self.getImageFileName())
            self.loadImage()
        except:
            logger.warning("Cover could not be downloaded")
            logger.error(self.track.name)
            width = self.size[0] -self.base_size

            current = TextItem(self.fonts['base'],self.track.name,(self.base_size/2,self.base_size*2),(width, self.base_size))
            self.touch_text_manager.set_object("track_name", current)

            current = TextItem(self.fonts['base'],self.track.album.name,(self.base_size/2,self.base_size*3),(width, self.base_size))
            self.touch_text_manager.set_object("album_name", current)

            current = TextItem(self.fonts['base'],self.getFirstArtist(self.track),(self.base_size/2,self.base_size*4),(width, self.base_size))
            self.touch_text_manager.set_object("artist_name", current)

    def loadImage(self):
        size = self.base_size * 4
        self.image = pygame.transform.scale(pygame.image.load(self.getCoverFolder()+self.getImageFileName()).convert(),(size,size))

    def touch_event(self, event):
        if event.type == TouchManager.click:
            objects = self.touch_text_manager.get_touch_objects_in_pos(event.current_pos)
            if objects is not None:
                for key in objects:
                    if key == "time_progress":
                        value = self.touch_text_manager.get_touch_object(key).get_pos_value(event.current_pos) * 1000
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
                self.manager.backend.tell({'action':'volume','value':volume})
                self.manager.volume_changed(volume)
            elif event.direction == TouchManager.down:
                volume = self.core.playback.volume.get() - 10
                if volume < 0:
                    volume = 0
                self.manager.backend.tell({'action':'volume','value':volume})
                self.manager.volume_changed(volume)


