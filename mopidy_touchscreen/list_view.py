from .screen_objects import ScreenObjectsManager
import logging
import pygame

logger = logging.getLogger(__name__)

class ListView():

    def __init__(self, pos, size, base_size,fonts):
        self.size = size
        self.pos = pos
        self.base_size = base_size
        self.screen_objects = ScreenObjectsManager(self.base_size)
        self.max_rows = self.size[1] / self.base_size
        self.current_item = 0
        self.fonts = fonts
        self.list_size = 0
        self.list = []
        self.set_list([])



    def set_list(self, item_list):
        self.list = item_list
        self.list_size = len(item_list)
        self.load_new_item_position(0)
        logger.error(self.list_size)
        self.screen_objects.add_scroll_bar("scroll", (self.pos[0]+self.size[0]-self.base_size,self.pos[1]), (self.base_size, self.size[1]),self.list_size,self.max_rows)

    def load_new_item_position(self, item_pos):
        self.current_item = item_pos
        i = self.current_item
        logger.error(self.max_rows)
        while i < self.list_size and i - self.current_item < self.max_rows:
            self.screen_objects.add_touch_object(str(i),self.fonts['dejavusans'], str(self.list[i]), (self.pos[0],self.pos[1]+self.base_size*i),None, (255, 255, 255))
            i += 1

    def render(self, surface):
        self.screen_objects.render(surface)



