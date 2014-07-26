from .screen_objects import ScreenObjectsManager
import logging
import pygame
from .touch_manager import TouchManager
from .touch_manager import TouchEvent
from .screen_objects import *

logger = logging.getLogger(__name__)


class ListView():

    def __init__(self, pos, size, base_size, fonts):
        self.size = size
        self.pos = pos
        self.base_size = base_size
        self.screen_objects = ScreenObjectsManager()
        self.max_rows = self.size[1] / self.base_size
        self.current_item = 0
        self.fonts = fonts
        self.list_size = 0
        self.list = []
        self.scrollbar = False
        self.set_list([])

    def set_list(self, item_list):
        self.list = item_list
        self.list_size = len(item_list)
        if self.max_rows < self.list_size:
            self.scrollbar = True
            scroll_bar = ScrollBar((self.pos[0]+self.size[0]-self.base_size,self.pos[1]), (self.base_size, self.size[1]),self.list_size,self.max_rows)
            self.screen_objects.set_touch_object("scrollbar", scroll_bar)
            logger.error("hemen nao")
        else:
            self.scrollbar = False
        self.load_new_item_position(0)

    def load_new_item_position(self, item_pos):
        self.current_item = item_pos
        if self.scrollbar:
            self.screen_objects.clear_touch(["scrollbar"])
        else:
            self.screen_objects.clear_touch(None)
        i = self.current_item
        z = 0
        if self.scrollbar:
            width = self.size[0] - self.base_size
        else:
            width = self.size[0]
        while i < self.list_size and z < self.max_rows:
            item = TouchAndTextItem(self.fonts['dejavusans'], self.list[i], (self.pos[0], self.pos[1]+self.base_size*z), (width, self.base_size))
            self.screen_objects.set_touch_object(str(i), item)
            i += 1
            z += 1

    def render(self, surface):
        self.screen_objects.render(surface)

    def touch_event(self, touch_event):
        if touch_event.type == TouchManager.click:
            objects = self.screen_objects.get_touch_objects_in_pos(touch_event.current_pos)
            if objects is not None:
                for key in objects:
                    if key == "scrollbar":
                        direction = self.screen_objects.get_touch_object(key).touch(touch_event.current_pos)
                        if direction != 0:
                            self.move_to(direction)

    def move_to(self, direction):
        if direction == 1:
            self.current_item += self.max_rows
            if self.current_item + self.max_rows > self.list_size:
                self.current_item = self.list_size - self.max_rows
            self.load_new_item_position(self.current_item)
            self.screen_objects.get_touch_object("scrollbar").set_item(self.current_item)
        elif direction == -1:
            self.current_item -= self.max_rows
            if self.current_item < 0:
                self.current_item = 0
            self.load_new_item_position(self.current_item)
            self.screen_objects.get_touch_object("scrollbar").set_item(self.current_item)