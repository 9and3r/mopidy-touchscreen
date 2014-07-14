import pygame
import logging
from mopidy.audio import PlaybackState
from .dynamic_background import DynamicBackground


logger = logging.getLogger(__name__)

class MainScreen():



	def __init__(self,size,manager):
		self.size=size
		self.manager=manager
		self.background=DynamicBackground()

	def update(self,core):
		screen = pygame.Surface(self.size)
		self.background.drawBackground(screen)
		text = pygame.font.SysFont("arial",20)
		if(self.manager.track!=None):
			text_surface=text.render(self.manager.track.track.name,False,(255,255,255))
			screen.blit(text_surface,(0,0))
			images=self.manager.track.track.album.images
			if len(images)>0:
				image = pygame.image.load(next(iter(images)))
				screen.blit(image,(0,0))
		return screen


	
