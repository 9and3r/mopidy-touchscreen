import pygame

from .base_screen import BaseScreen
from ..graphic_utils import ScreenObjectsManager, TouchAndTextItem
from ..input import InputManager


class Keyboard(BaseScreen):

    def __init__(self, size, base_size, manager, fonts, listener):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.base_width = size[0]/10
        self.base_height = size[1]/5
        self.listener = listener
        self.manager = manager
        try:
            self.font is None
        except AttributeError:
            self.font = pygame.font.SysFont("arial", size[1]/6)
        self.keyboards = [ScreenObjectsManager(), ScreenObjectsManager()]
        self.other_objects = ScreenObjectsManager()
        self.current_keyboard = 0

        rows = [['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '-'],
                [',', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '_']]

        line = self.base_height
        for row in rows:
            pos = 0
            for key in row:
                button = \
                    TouchAndTextItem(self.font, key,
                                     (pos, line),
                                     (self.base_width, self.base_height),
                                     center=True, background=(150, 150, 150))
                self.keyboards[self.current_keyboard].\
                    set_touch_object(key, button)
                pos += self.base_width
            line += self.base_height

        self.current_keyboard = 1
        rows = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                ['!', '@', '#', '$', '%', '&', '/', '(', ')', '='],
                ['?', '{', '}', '_', '[', ']', '+', '<', '>', '*']]
        line = self.base_height
        for row in rows:
            pos = 0
            for key in row:
                button = \
                    TouchAndTextItem(self.font, key, (pos, line),
                                     (self.base_width, self.base_height),
                                     center=True, background=(150, 150, 150))
                self.keyboards[self.current_keyboard].\
                    set_touch_object(key, button)
                pos += self.base_width
            line += self.base_height
        self.current_keyboard = 0

        # Symbol button
        button = TouchAndTextItem(self.font, "123",
                                  (0, self.base_height*4),
                                  (self.base_width*2, self.base_height),
                                  center=True, background=(150, 150, 150))
        self.other_objects.set_touch_object("symbols", button)

        # remove button
        button = TouchAndTextItem(self.font, "<-",
                                  (self.base_width*2, self.base_height*4),
                                  (self.base_width*2, self.base_height),
                                  center=True, background=(150, 150, 150))
        self.other_objects.set_touch_object("remove", button)

        # Space button
        button = TouchAndTextItem(self.font, " ",
                                  (self.base_width*4, self.base_height*4),
                                  (self.base_width*4, self.base_height),
                                  center=True, background=(150, 150, 150))
        self.other_objects.set_touch_object("space", button)

        # OK button
        button = TouchAndTextItem(self.font, "->",
                                  (self.base_width*8, self.base_height*4),
                                  (self.base_width*2, self.base_height),
                                  center=True, background=(150, 150, 150))
        self.other_objects.set_touch_object("ok", button)

        # EditText button
        button = TouchAndTextItem(self.font, "",
                                  (0, 0),
                                  (self.base_width*10, self.base_height),
                                  center=True)
        self.other_objects.set_object("text", button)

    def update(self, screen):
        screen.fill((0, 0, 0))
        self.keyboards[self.current_keyboard].render(screen)
        self.other_objects.render(screen)

    def touch_event(self, touch_event):
        if touch_event.type == InputManager.click:
            keys = self.keyboards[self.current_keyboard]\
                .get_touch_objects_in_pos(touch_event.current_pos)
            for key in keys:
                self.other_objects.get_object("text").add_text(key, False)
            keys = self.other_objects.get_touch_objects_in_pos(
                touch_event.current_pos)
            for key in keys:
                if key == 'symbols':
                    if self.current_keyboard == 0:
                        self.current_keyboard = 1
                    else:
                        self.current_keyboard = 0
                elif key == "remove":
                    self.other_objects.get_object("text").remove_text(1, False)
                elif key == "space":
                    self.other_objects.get_object("text").add_text(" ", False)
                elif key == "ok":
                    text = self.other_objects.get_object("text").text
                    self.listener.text_input(text)
                    self.manager.close_keyboard()
        elif touch_event.type == InputManager.key:
            if len(touch_event.unicode):
                if touch_event.unicode == u'\x08':
                    self.other_objects.get_object("text").remove_text(1, False)
                else:
                    self.other_objects.get_object("text").add_text(
                        touch_event.unicode, False)
