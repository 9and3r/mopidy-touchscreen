import pygame
import logging
import hashlib
import os
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
                screen.blit(self.image, (0, 0))
            self.touch_text_manager.render(screen)

        return screen

    def track_started(self, track):
        self.track = track
        logger.error("hemen nago")
        self.touch_text_manager.add_text_object(self.track.name,(0,0), self.size, (255.255,255))
        if not self.is_image_in_cache():
            self.downloadImage()
        else:
            self.loadImage()

    def getImageFileName(self):
        name = self.track.album.name
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
        self.imageStatus = 0
        #safe_artist=urllib.quote_plus(self.track.artists)
        safe_artist='clean+bandit'
        safe_album=urllib.quote_plus(self.track.album.name)
        url="http://ws.audioscrobbler.com/2.0/?"
        params="method=album.getinfo&api_key=59a04c6a73fb99d6e8996e01db306829&artist="+safe_artist+"&album="+safe_album+"&format=json"
        response = urllib2.urlopen(url+params)
        data = json.load(response)
        image = data['album']['image'][2]['#text']
        logger.error(image)
        urllib.urlretrieve(image, self.getCoverFolder()+self.getImageFileName())
        self.loadImage()

    def loadImage(self):
        size = self.size[0]/2 - margin
        self.image = pygame.transform.scale(pygame.image.load(self.getCoverFolder()+self.getImageFileName()),(size,size))

