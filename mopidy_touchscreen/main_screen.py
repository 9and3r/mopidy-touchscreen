import pygame
import logging
from mopidy.audio import PlaybackState
from .dynamic_background import DynamicBackground
import musicbrainzngs as musicb


logger = logging.getLogger(__name__)

class MainScreen():



	def __init__(self,size,manager):
		self.size=size
		self.manager=manager
		self.background=DynamicBackground()
		self.track = None

	def update(self,core):
		screen = pygame.Surface(self.size)
		self.background.drawBackground(screen)
		text = pygame.font.SysFont("arial",20)
		if(self.track!=None):
			text_surface=text.render(self.track.album.musicbrainz_id,False,(255,255,255))
			screen.blit(text_surface,(0,0))
			#logger.error(self.track.album.musicbrainz_id)
		return screen

	def track_started(self,track):
		self.track=track
		self.downloadImage()

	def downloadImage(self):
		logger.error("hemen nago")
		logger.error(musicb.search_releases(artist=self.track.artist.name, limit=1))
		


	
