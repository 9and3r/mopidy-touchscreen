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
from .screen_objects import ScreenObjectsManager
from .dynamic_background import DynamicBackground

logger = logging.getLogger(__name__)


class MainScreen():

    def __init__(self, size, manager, cache, core, fonts):
        self.core = core
        self.size = size
        self.base_size = self.size[1]/8
        self.fonts = fonts
        self.manager = manager
        self.background = DynamicBackground()
        self.track = None
        self.cache = cache
        self.image = None
        self.touch_text_manager = ScreenObjectsManager(size,self.base_size)


    def update(self, screen):
        self.background.drawBackground(screen)

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
        self.touch_text_manager.add_object("track_name",self.fonts['dejavusans'],track.name,(x,self.base_size*2), (self.size[0]-self.base_size,self.size[1]), (255, 255, 255))
        self.touch_text_manager.add_object("album_name",self.fonts['dejavusans'],track.album.name,(x,self.base_size*3), (self.size[0]-self.base_size,self.size[1]), (255, 255, 255))
        self.touch_text_manager.add_object("artist_name",self.fonts['dejavusans'],self.getFirstArtist(track),(x,self.base_size*4), (self.size[0]-self.base_size,self.size[1]), (255, 255, 255))
        self.touch_text_manager.add_progressbar("time_progress", self.fonts['dejavusans'],time.strftime('%M:%S', time.gmtime(0))+"/"+time.strftime('%M:%S', time.gmtime(0)),(0,self.base_size*6), (self.size[0],self.base_size*7),track.length/1000, False)
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
            self.touch_text_manager.add_object("track_name",self.fonts['dejavusans'],self.track.name,(self.base_size,self.base_size*2), (self.size[0]-self.base_size,self.size[1]), (255, 255, 255))
            self.touch_text_manager.add_object("album_name",self.fonts['dejavusans'],self.track.album.name,(self.base_size,self.base_size*3), (self.size[0]-self.base_size,self.size[1]), (255, 255, 255))
            self.touch_text_manager.add_object("artist_name",self.fonts['dejavusans'],self.getFirstArtist(self.track),(self.base_size,self.base_size*4), (self.size[0]-self.base_size,self.size[1]), (255, 255, 255))

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


