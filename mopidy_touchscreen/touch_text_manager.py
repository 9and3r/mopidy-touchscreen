import pygame
import logging

logger = logging.getLogger(__name__)


class TouchTextManager():
    def __init__(self, size, base_size):
        self.size = size
        self.base_size = base_size
        self.touch_objects = {}
        self.text_objects = {}

    def add_object(self, key, text, pos, pos2, color):
        self.text_objects[key] = TextItem(text, pos, pos2, color, self.base_size)

    def get_object(self, key):
        return self.text_objects[key]

    def add_touch_object(self, key, text, pos, color):
        self.touch_objects['key'] = TouchAndTextItem(text, pos, color, self.base_size)

    def get_touch_object(self, key):
        return self.touch_objects['key']

    def add_progressbar(self, key, pos, pos2, max):
        self.touch_objects['key'] = Progressbar(pos, pos2, max)

    def render(self, surface):
        for key in self.text_objects:
            self.text_objects[key].update()
            self.text_objects[key].render(surface)
        for key in self.touch_objects:
            self.touch_objects[key].render(surface)


class BaseItem():
    def __init__(self, pos, pos2):
        self.pos = pos
        self.pos2 = pos2
        self.size = [0, 0]
        self.size[0] = self.pos2[0] - self.pos[0]
        self.size[1] = self.pos2[1] - self.pos[1]
        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])


class TextItem(BaseItem):
    def __init__(self, text, pos, pos2, color, text_size):
        if pos2 is not None:
            BaseItem.__init__(self, pos, pos2)
        self.text_size = text_size
        self.font = pygame.font.SysFont("arial", text_size)
        self.text = text
        self.color = color
        self.box = self.font.render(text, True, self.color)
        if pos2 is not None:
            if self.pos[0] + self.box.get_rect().width > pos2[0]:
                self.fit_horizontal = False
                self.text = self.text + "          "
                self.original_text = self.text
                self.step = 0
            else:
                self.fit_horizontal = True
            if self.pos[1] + self.box.get_rect().height > pos2[1]:
                self.fit_vertical = False
            else:
                self.fit_vertical = True
        else:
            BaseItem.__init__(self, pos, (pos[0] + self.box.get_rect().width, pos[1] + self.box.get_rect().height))
            self.fit_horizontal = True
            self.fit_vertical = True


    def update(self):
        if not self.fit_horizontal:
            if self.text == self.original_text:
                if self.step > 90:
                    self.step = 0
                    new_text = self.text[1:]
                    new_text = new_text + self.text[:1]
                    self.text = new_text
                else:
                    self.step = self.step + 1
            elif self.step > 5:
                self.step = 0
                new_text = self.text[1:]
                new_text = new_text + self.text[:1]
                self.text = new_text
            else:
                self.step = self.step + 1

    def render(self, surface):
        if self.fit_horizontal:
            self.box
        else:
            self.box = self.font.render(self.text, True, self.color)
        surface.blit(self.box, self.pos, area=self.rect)

    def set_text(self, text):
        self.__init__(text, self.pos, self.pos2, self.color, self.text_size)


class TouchObject(BaseItem):
    def __init__(self, pos, pos2):
        BaseItem.__init__(self, pos, pos2)
        self.active = False
        self.background_box = pygame.Surface(self.size)
        self.background_box.fill((0, 128, 255))

    def render(self, surface):
        surface.blit(self.background_box, self.pos)


class TouchAndTextItem(TouchObject, TextItem):
    def __init__(self, text, pos, color, text_size):
        TextItem.__init__(self, text, pos, None, color, text_size)
        TouchObject.__init__(self, pos, self.pos2)

    def update(self):
        TextItem.update()

    def render(self, surface):
        TouchObject.render(self, surface)
        TextItem.render(self, surface)


class Progressbar(BaseItem):
    def __init__(self, pos, pos2, max):
        BaseItem.__init__(self, pos, pos2)
        logger.error(pos2)
        self.value = 0
        self.max = max
        self.back_color = (0, 0, 0)
        self.main_color = (255, 255, 255)
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.back_color)

    def update(self):
        pass

    def render(self, surface):
        surface.blit(self.surface, self.pos)

    def set_value(self, value):
        self.value = value
        self.surface.fill(self.back_color)
        pos_pixel = value * self.size[0] / self.max
        rect = pygame.Rect(0, 0, pos_pixel, self.size[1])
        self.surface.fill(self.main_color, rect)

