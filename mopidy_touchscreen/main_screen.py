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
from .screen_objects import ScreenObjectsManager
from .dynamic_background import DynamicBackground

logger = logging.getLogger(__name__)


class MainScreen():

    def __init__(self,size,manager,cache,core):
        self.core = core
        self.size = size
        self.base_size = self.size[1]/12
        self.manager = manager
        self.background = DynamicBackground()
        self.track = None
        self.cache = cache
        self.image = None
        self.touch_text_manager = ScreenObjectsManager(size,self.base_size)
        self.touch_text_manager.add_touch_object("pause_play","Play",(0,0),(255,255,255))


    def update(self):
        screen = pygame.Surface(self.size)
        self.background.drawBackground(screen)
        if self.track is not None:
            if self.image is not None:
                screen.blit(self.image, (self.base_size, self.base_size*3))
            self.touch_text_manager.get_touch_object("time_progress").set_value(self.core.playback.time_position.get()/1000)
            self.touch_text_manager.get_object("track_time").set_text(time.strftime('%M:%S', time.gmtime(self.core.playback.time_position.get()/1000))+"/"+time.strftime('%M:%S', time.gmtime(self.track.length/1000)))
        self.touch_text_manager.render(screen)
        return screen

    def track_started(self, track):

        self.image = None
        self.touch_text_manager.add_object("track_name",track.name,(self.size[0]/2,self.base_size*3), (self.size[0]-self.base_size,self.size[1]), (255, 255, 255))
        self.touch_text_manager.add_object("album_name",track.album.name,(self.size[0]/2,self.base_size*4), (self.size[0]-self.base_size,self.size[1]), (255, 255, 255))
        self.touch_text_manager.add_object("artist_name",self.getFirstArtist(track),(self.size[0]/2,self.base_size*5), (self.size[0]-self.base_size,self.size[1]), (255, 255, 255))
        self.touch_text_manager.add_object("track_time",time.strftime('%M:%S', time.gmtime(0))+"/"+time.strftime('%M:%S', time.gmtime(0)),(self.size[0]/2,self.base_size*6), (self.size[0]-self.base_size,self.base_size * 7), (255, 255, 255))
        self.touch_text_manager.add_progressbar("time_progress", (self.size[0]/2,self.base_size*7), (self.size[0]-self.base_size,self.base_size*8),track.length/1000)
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
        safe_artist=urllib.quote_plus(self.getFirstArtist(None))
        safe_album=urllib.quote_plus(self.track.album.name)
        url="http://ws.audioscrobbler.com/2.0/?"
        params="method=album.getinfo&api_key=59a04c6a73fb99d6e8996e01db306829&artist="+safe_artist+"&album="+safe_album+"&format=json"
        response = urllib2.urlopen(url+params)
        data = json.load(response)
        image = data['album']['image'][-1]['#text']
        urllib.urlretrieve(image, self.getCoverFolder()+self.getImageFileName())
        self.loadImage()

    def loadImage(self):
        size = self.base_size*6
        self.image = pygame.transform.scale(pygame.image.load(self.getCoverFolder()+self.getImageFileName()).convert(),(size,size))

    def touch_event(self, event):
        objects = self.touch_text_manager.get_touch_objects_in_pos(event.current_pos)
        logger.error(objects)
        if objects is not None:
            for key in objects:
                if key == "time_progress":
                    value = self.touch_text_manager.get_touch_object(key).get_pos_value(event.current_pos) * 1000
                    self.core.playback.seek(value)