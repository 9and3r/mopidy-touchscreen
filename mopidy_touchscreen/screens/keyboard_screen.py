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
        self.selected_row = 0
        self.selected_col = 0
        self.selected_others = -1
        self.font = pygame.font.SysFont("arial", size[1]/6)
        self.keyboards = [ScreenObjectsManager(), ScreenObjectsManager()]
        self.other_objects = ScreenObjectsManager()
        self.current_keyboard = 0

        self.keys = [[['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                      ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '-'],
                      [',', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '_']],

                     [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                      ['!', '@', '#', '$', '%', '&', '/', '(', ')', '='],
                      ['?', '{', '}', '_', '[', ']', '+', '<', '>', '*']]]

        line = self.base_height
        for row in self.keys[self.current_keyboard]:
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
        line = self.base_height
        for row in self.keys[self.current_keyboard]:
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
        self.change_selected(0, 0)

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
                    self.change_keyboard()
                elif key == "remove":
                    self.other_objects.get_object("text").remove_text(1, False)
                elif key == "space":
                    self.other_objects.get_object("text").add_text(" ", False)
                elif key == "ok":
                    text = self.other_objects.get_object("text").text
                    self.listener.text_input(text)
                    self.manager.close_keyboard()
        elif touch_event.type == InputManager.key:
            if isinstance(touch_event.unicode, unicode):
                if touch_event.unicode == u'\x08':
                    self.other_objects.get_object("text").remove_text(1, False)
                else:
                    self.other_objects.get_object("text").add_text(
                        touch_event.unicode, False)
            elif touch_event.direction is not None:
                x = 0
                y = 0
                if touch_event.direction == InputManager.left:
                    x = -1
                elif touch_event.direction == InputManager.right:
                    x = 1
                elif touch_event.direction == InputManager.up:
                    y = -1
                elif touch_event.direction == InputManager.down:
                    y = 1
                self.change_selected(x, y)

    def change_keyboard(self):
        if self.current_keyboard == 0:
            self.current_keyboard = 1
        else:
            self.current_keyboard = 0
        if self.selected_others < 0:
            self.change_selected(0, 0)

    def change_selected(self, x, y):
        if self.selected_others < 0:
            self.selected_row += x
            if self.selected_row < 0:
                self.selected_row = 0
            elif self.selected_row > 9:
                self.selected_row = 9
            self.selected_col += y
            if self.selected_col < 0:
                self.selected_col = 0
            elif self.selected_col > 2:
                if self.selected_col < 2:
                    self.selected_others = 0
                elif self.selected_col < 8:
                    self.selected_others = 1
                else:
                    self.selected_others = 2
                self.set_selected_other()
            if self.selected_others < 0:
                key = self.keys[self.current_keyboard]
                [self.selected_col][self.selected_row]
                self.keyboards[self.current_keyboard].set_selected(key)
            else:
                self.keyboards[0].set_selected(None)
                self.keyboards[0].set_selected(None)
        else:
            if y < 0:
                self.selected_others = -1
                self.set_selected_other()
                self.selected_col = 2
                self.selected_row = 0
                key = self.keys[self.current_keyboard]
                [self.selected_col][self.selected_row]
                self.keyboards[self.current_keyboard].set_selected(key)
            else:
                self.selected_others += x
                if self.selected_others < 0:
                    self.selected_others = 0
                elif self.selected_others > 3:
                    self.selected_others = 3
                self.set_selected_other()

    def set_selected_other(self):
        key = None
        if self.selected_others == 0:
            key = "symbols"
        elif self.selected_others == 1:
            key = "remove"
        elif self.selected_others == 2:
            key = "space"
        elif self.selected_others == 3:
            key = "ok"
        self.other_objects.set_selected(key)
