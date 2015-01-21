import logging
import math

import pygame

from .input_manager import InputManager


logger = logging.getLogger(__name__)


class ScreenObjectsManager():
    def __init__(self):
        self.touch_objects = {}
        self.text_objects = {}
        self.selected = None
        self.selected_key = None

    def clear(self):
        self.touch_objects = {}
        self.text_objects = {}

    def set_object(self, key, add_object):
        self.text_objects[key] = add_object

    def get_object(self, key):
        return self.text_objects[key]

    def set_touch_object(self, key, add_object):
        self.touch_objects[key] = add_object

    def get_touch_object(self, key):
        return self.touch_objects[key]

    def render(self, surface):
        for key in self.text_objects:
            self.text_objects[key].update()
            self.text_objects[key].render(surface)
        for key in self.touch_objects:
            self.touch_objects[key].update()
            self.touch_objects[key].render(surface)

    def get_touch_objects_in_pos(self, pos):
        touched_objects = []
        for key in self.touch_objects:
            if self.touch_objects[key].is_pos_inside(pos):
                touched_objects.append(key)
        return touched_objects

    def clear_touch(self, not_remove):
        if not_remove is not None:
            new_touch = {}
            for key in not_remove:
                new_touch[key] = self.get_touch_object(key)
            self.touch_objects = new_touch
        else:
            self.touch_objects = {}

    def set_selected(self, key):
        if self.selected is not None:
            self.selected.set_selected(False)
        if key is not None:
            self.selected = self.touch_objects[key]
            self.selected.set_selected(True)
            self.selected_key = key
        else:
            self.selected = None
            self.selected_key = None


class BaseItem():
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        self.rect_in_pos = pygame.Rect(self.pos[0], self.pos[1],
                                       self.size[0],
                                       self.size[1])

    def get_right_pos(self):
        return self.pos[0] + self.size[0]

    def update(self):
        pass


class TextItem(BaseItem):

    scroll_speed = 5

    def __init__(self, font, text, pos, size, center=False):
        self.font = font
        self.text = text
        self.color = (255, 255, 255)
        self.box = self.font.render(text, True, self.color)
        if size is not None:
            if size[1] == -1:
                height = self.font.size(text)[1]
                BaseItem.__init__(self, pos, (size[0], height))
            else:
                BaseItem.__init__(self, pos, size)
        else:
            BaseItem.__init__(self, pos, self.font.size(text))
        if size is not None:
            if self.pos[0] + self.box.get_rect().width > pos[0] + \
                    size[0]:
                self.fit_horizontal = False
                self.step = 0
                self.step_2 = None
                self.scroll_white_gap = self.font.get_height() * 4
            else:
                self.fit_horizontal = True
            if self.pos[1] + self.box.get_rect().height > pos[1] + \
                    size[1]:
                self.fit_vertical = False
            else:
                self.fit_vertical = True
        else:
            self.fit_horizontal = True
            self.fit_vertical = True
        self.margin = 0
        self.center = center
        if self.center:
            if self.fit_horizontal:
                self.margin = (self.size[0] -
                               self.box.get_rect().width)/2

    def update(self):
        if not self.fit_horizontal:
            self.step += TextItem.scroll_speed
            if self.step_2 is None:
                if (self.box.get_rect().width - self.step +
                        self.scroll_white_gap) < self.size[0]:
                    self.step_2 = \
                        self.box.get_rect().width - \
                        self.step + self.scroll_white_gap
            else:
                self.step_2 -= TextItem.scroll_speed
                if self.step_2 < 0:
                    self.step = 0 - self.step_2
                    self.step_2 = None
            return True
        else:
            return BaseItem.update(self)

    def render(self, surface):
        if self.fit_horizontal:
            surface.blit(
                self.box, ((self.pos[0] + self.margin), self.pos[1]), area=self.rect)
        else:
            surface.blit(self.box, self.pos,
                         area=pygame.Rect(self.step, 0, self.size[0],
                                          self.size[1]))
            if self.step_2 is not None:
                surface.blit(self.box, (self.pos[0]+self.step_2,
                                        self.pos[1]),
                             area=pygame.Rect(0, 0,
                                              self.size[0] -
                                              self.step_2,
                                              self.size[1]))

    def set_text(self, text, change_size):
        if text != self.text:
            if change_size:
                TextItem.__init__(self, self.font, text, self.pos,
                                  None, self.center)
            else:
                TextItem.__init__(self, self.font, text, self.pos,
                                  self.size, self.center)


class TouchObject(BaseItem):
    def __init__(self, pos, size):
        BaseItem.__init__(self, pos, size)
        self.active = False
        self.selected = False
        self.selected_box = pygame.Surface(size, pygame.SRCALPHA)
        self.selected_box.fill((0, 0, 0, 128))
        self.selected_box_rectangle = pygame.Surface(size,
                                                     pygame.SRCALPHA)
        pygame.draw.rect(self.selected_box_rectangle, (255, 255, 255),
                         self.selected_box_rectangle.get_rect(),
                         size[1]/10+1)

    def is_pos_inside(self, pos):
        return self.rect_in_pos.collidepoint(pos)

    def set_active(self, active):
        self.active = active

    def set_selected(self, selected):
        self.selected = selected

    def render(self, surface):
        if self.selected:
            surface.blit(self.selected_box, self.pos)
            surface.blit(self.selected_box_rectangle, self.pos)

    def pre_render(self, surface):
        if self.selected:
            surface.blit(self.selected_box, self.pos)

    def post_render(self, surface):
        if self.selected:
            surface.blit(self.selected_box_rectangle, self.pos)


class TouchAndTextItem(TouchObject, TextItem):
    def __init__(self, font, text, pos, size, center=False):
        TextItem.__init__(self, font, text, pos, size, center=center)
        TouchObject.__init__(self, pos, self.size)
        self.active_color = (0, 150, 255)
        self.normal_box = self.box
        self.active_box = self.font.render(text, True,
                                           self.active_color)

    def update(self):
        TextItem.update(self)

    def set_text(self, text, change_size):
        TextItem.set_text(self, text, change_size)
        self.normal_box = self.box
        self.active_box = self.font.render(text, True,
                                           self.active_color)

    def set_active(self, active):
        TouchObject.set_active(self, active)
        if self.active:
            self.box = self.active_box
        else:
            self.box = self.normal_box

    def render(self, surface):
        TouchObject.pre_render(self, surface)
        TextItem.render(self, surface)
        TouchObject.post_render(self, surface)


class Progressbar(TouchObject):
    def __init__(self, font, text, pos, size, max_value, value_text):
        BaseItem.__init__(self, pos, size)
        self.value = 0
        self.max = max_value
        self.back_color = (0, 0, 0, 128)
        self.main_color = (0, 150, 255)
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.surface.fill(self.back_color)
        self.value_text = value_text
        if value_text:
            self.text = TextItem(font, str(max_value), pos, None)
            self.text.pos = (self.pos[0]
                             + self.size[0] / 2 -
                             self.text.size[0] /
                             2, self.text.pos[1])
            self.text.set_text(str(self.value), True)
        else:
            self.text = TextItem(font, text, pos, None)
            self.text.pos = (
                self.pos[0] + self.size[0] / 2 - self.text.size[0] /
                2, self.text.pos[1])

    def render(self, surface):
        surface.blit(self.surface, self.pos)
        self.text.render(surface)

    def set_value(self, value):
        if value != self.value:
            self.value = value
            if self.value_text:
                self.set_text(str(self.value))
                self.text.pos = (self.pos[0]
                                 + self.size[0] / 2 -
                                 self.text.size[0]
                                 / 2, self.text.pos[1])
            self.surface.fill(self.back_color)
            pos_pixel = value * self.size[0] / self.max
            rect = pygame.Rect(0, 0, pos_pixel, self.size[1])
            self.surface.fill(self.main_color, rect)

    def get_pos_value(self, pos):
        x = pos[0] - self.pos[0]
        return x * self.max / self.size[0]

    def set_text(self, text):
        self.text.set_text(text, True)


class ScrollBar(TouchObject):
    def __init__(self, pos, size, max_value, items_on_screen):
        BaseItem.__init__(self, pos,
                          (pos[0] + size[0], pos[1] + size[1]))
        self.pos = pos
        self.size = size
        self.max = max_value
        self.items_on_screen = items_on_screen
        self.current_item = 0
        self.back_bar = pygame.Surface(self.size, pygame.SRCALPHA)
        self.back_bar.fill((255, 255, 255, 128))
        self.bar_pos = 0
        if self.max < 1:
            self.bar_size = self.size[1]
        else:
            self.bar_size = math.ceil(
                float(self.items_on_screen) / float(self.max) * float(
                    self.size[1]))
        self.bar = pygame.Surface((self.size[0], self.bar_size))
        self.bar.fill((255, 255, 255))

    def render(self, surface):
        surface.blit(self.back_bar, self.pos)
        surface.blit(self.bar,
                     (self.pos[0], self.pos[1] + self.bar_pos))

    def touch(self, pos):
        if pos[1] < self.pos[1] + self.bar_pos:
            return -1
        elif pos[1] > self.pos[1] + self.bar_pos + self.bar_size:
            return 1
        else:
            return 0

    def set_item(self, current_item):
        self.current_item = current_item
        self.bar_pos = float(self.current_item) / float(
            self.max) * float(
            self.size[1])
