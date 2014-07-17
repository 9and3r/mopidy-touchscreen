import pygame
import logging
import hashlib
import os
from threading import Thread
import urllib
import urllib2
import json
from mopidy.audio import PlaybackState
from .touch_text_manager import TouchTextManager
from .dynamic_background import DynamicBackground

logger = logging.getLogger(__name__)
margin = 10


class MainScreen():

    def __init__(self,size,manager,cache):
        self.size = size
        self.manager = manager
        self.background = DynamicBackground()
        self.track = None
        self.cache = cache
        self.image = None
        self.touch_text_manager = TouchTextManager(size)

    def update(self,core):
        screen = pygame.Surface(self.size)
        self.background.drawBackground(screen)
        if self.track!=None:
            if self.image is not None:
                screen.blit(self.image, ((self.size[0]-self.image.get_rect().width)/2, 0))
            self.touch_text_manager.render(screen)
        return screen

    def track_started(self, track):
        self.track = track
        self.image = None
        self.touch_text_manager.add_text_object("track_name",self.track.name,(0,0), self.size, (255, 255, 255))
        self.touch_text_manager.add_text_object("album_name",self.track.album.name,(0,20), self.size, (255, 255, 255))
        self.touch_text_manager.add_text_object("artist_name",self.getFirstArtist(),(0,40), self.size, (255, 255, 255))
        if not self.is_image_in_cache():
            thread = Thread(target=self.downloadImage())
            thread.start()
        else:
            self.loadImage()

    def getFirstArtist(self):
        artist = next(iter(self.track.artists)).name
        if "," in artist:
            artist = artist.split(',')[0]
        return artist


    def getImageFileName(self):
        name = self.track.album.name + '-' + self.getFirstArtist()
        md5name = hashlib.md5(name).hexdigest()+".png"
        return md5name

    def getCoverFolder(self):
        if(not os.path.isdir(self.cache+"/covers")):
            os.makedirs(self.cache+"/covers")
        return self.cache+"/covers/"

    def is_image_in_cache(self):
        self.getCoverFolder()
        return os.path.isfile(self.cache+self.getCoverFolder()+self.getImageFileName())

    def downloadImage(self):
        safe_artist=urllib.quote_plus(self.getFirstArtist())
        safe_album=urllib.quote_plus(self.track.album.name)
        url="http://ws.audioscrobbler.com/2.0/?"
        params="method=album.getinfo&api_key=59a04c6a73fb99d6e8996e01db306829&artist="+safe_artist+"&album="+safe_album+"&format=json"
        response = urllib2.urlopen(url+params)
        data = json.load(response)
        image = data['album']['image'][-1]['#text']
        urllib.urlretrieve(image, self.getCoverFolder()+self.getImageFileName())
        self.loadImage()

    def loadImage(self):
        size = self.size[1]
        self.image = pygame.transform.scale(pygame.image.load(self.getCoverFolder()+self.getImageFileName()),(size,size))

