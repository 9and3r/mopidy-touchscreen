import logging

from .screen_objects import ScreenObjectsManager, ScrollBar, \
    TouchAndTextItem
from .input_manager import InputManager

logger = logging.getLogger(__name__)


class ListView():
    def __init__(self, pos, size, base_size, font):
        self.size = size
        self.pos = pos
        self.base_size = base_size
        self.screen_objects = ScreenObjectsManager()
        self.max_rows = self.size[1] / self.base_size
        self.current_item = 0
        self.font = font
        self.list_size = 0
        self.list = []
        self.scrollbar = False
        self.set_list([])
        self.selected = []

    # Sets the list for the lisview. It should be an iterable of strings
    def set_list(self, item_list):
        self.screen_objects.clear()
        self.list = item_list
        self.list_size = len(item_list)
        if self.max_rows < self.list_size:
            self.scrollbar = True
            scroll_bar = ScrollBar(
                (self.pos[0] + self.size[0] - self.base_size,
                 self.pos[1]),
                (self.base_size, self.size[1]), self.list_size,
                self.max_rows)
            self.screen_objects.set_touch_object("scrollbar",
                                                 scroll_bar)
        else:
            self.scrollbar = False
        self.load_new_item_position(0)

    # Will load items currently displaying in item_pos
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
            item = TouchAndTextItem(self.font, self.list[i], (
                self.pos[0], self.pos[1] + self.base_size * z),
                                    (width, -1))
            self.screen_objects.set_touch_object(str(i), item)
            i += 1
            z += 1


    def render(self, surface):
        self.screen_objects.render(surface)

    def touch_event(self, touch_event):
        if touch_event.type == InputManager.click \
                or touch_event.type == InputManager.long_click:
            objects = self.screen_objects.get_touch_objects_in_pos(
                touch_event.current_pos)
            if objects is not None:
                for key in objects:
                    if key == "scrollbar":
                        direction = self.screen_objects.get_touch_object(
                            key).touch(touch_event.current_pos)
                        if direction != 0:
                            self.move_to(direction)
                    else:
                        return int(key)
        elif touch_event.type == InputManager.swipe:
            if touch_event.direction == InputManager.up:
                self.move_to(-1)
            elif touch_event.direction == InputManager.down:
                self.move_to(1)

    # Scroll to direction
    # direction == 1 will scroll down
    # direction == -1 will scroll up
    def move_to(self, direction):
        if self.scrollbar:
            if direction == 1:
                self.current_item += self.max_rows
                if self.current_item + self.max_rows > self.list_size:
                    self.current_item = self.list_size - self.max_rows
                self.load_new_item_position(self.current_item)
                self.screen_objects.get_touch_object(
                    "scrollbar").set_item(
                    self.current_item)
            elif direction == -1:
                self.current_item -= self.max_rows
                if self.current_item < 0:
                    self.current_item = 0
                self.load_new_item_position(self.current_item)
                self.screen_objects.get_touch_object(
                    "scrollbar").set_item(
                    self.current_item)
            self.set_selected(self.selected)

    # Set selected items
    def set_selected(self, selected):
        for number in self.selected:
            try:
                self.screen_objects.get_touch_object(
                    str(number)).set_active(
                    False)
            except KeyError:
                pass
        for number in selected:
            try:
                self.screen_objects.get_touch_object(
                    str(number)).set_active(
                    True)
            except KeyError:
                pass
        self.selected = selected
