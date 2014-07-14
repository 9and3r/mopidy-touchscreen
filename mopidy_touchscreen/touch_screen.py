import pykka

import logging
from threading import Thread
import pygame
from .main_screen import MainScreen

from mopidy import core


logger = logging.getLogger(__name__)

class TouchScreen(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
	super(TouchScreen, self).__init__()
        self.core = core

    def start_thread(self):
	pygame.init()
	clock = pygame.time.Clock()
	main_screen = MainScreen()
	screen = pygame.display.set_mode((200,200));
	while self.running:
		clock.tick(60)
		main_screen.update(screen)
		pygame.display.flip()
	logger.error("bukatzen")
	pygame.quit()
	logger.error("bukatu dot")
	
	

    def on_start(self):
	self.running=True
	self.thread = Thread(target=self.start_thread)
	self.thread.start()

    def on_stop(self):
	self.running = False
	
	

    def track_playback_started(self, tl_track):
	pass
	#myfont = pygame.font.SysFont("monospace", 15)

				# render text
	#label = myfont.render(tl_track.track.name, 1, (255,255,0))
	#self.screen.blit(label, (100, 100))
    	#pygame.display.flip()
 
