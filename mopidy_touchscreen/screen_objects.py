import pygame
import logging

logger = logging.getLogger(__name__)

class ScreenObjectsManager():



    def __init__(self,base_size):
        self.base_size = base_size
        self.touch_objects = {}
        self.text_objects = {}

    def add_object(self, key, font, text, pos, pos2, color):
        self.text_objects[key] = TextItem(font, text, pos,pos2,color,self.base_size)

    def get_object(self, key):
        return self.text_objects[key]

    def add_touch_object(self, key, font, text, pos, pos2, color):
        self.touch_objects[key] = TouchAndTextItem(font, text, pos, pos2, color, self.base_size)
        return self.touch_objects[key].get_right_pos()

    def get_touch_object(self,key):
        return self.touch_objects[key]

    def add_progressbar(self, key, font, text, pos, pos2, max,value_text):
        self.touch_objects[key] = Progressbar(font, text,pos,pos2,max,self.base_size,value_text)

    def render(self, surface):
        for key in self.text_objects:
            self.text_objects[key].update()
            self.text_objects[key].render(surface)
        for key in self.touch_objects:
            self.touch_objects[key].render(surface)

    def get_touch_objects_in_pos(self, pos):
        objects = []
        for key in self.touch_objects:
            if self.touch_objects[key].is_pos_inside(pos):
                objects.append(key)
        return objects


class BaseItem():

    def __init__(self,pos,pos2):
        self.pos = pos
        self.pos2 = pos2
        self.size=[0,0]
        self.size[0] = self.pos2[0] - self.pos[0]
        self.size[1] = self.pos2[1] - self.pos[1]
        self.rect = pygame.Rect(0,0,self.size[0],self.size[1])
        self.rect_in_pos = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])

    def get_right_pos(self):
        return self.pos2[0]


class TextItem(BaseItem):

    def __init__(self, font, text, pos, pos2, color, text_size):
        if pos2 is not None:
            BaseItem.__init__(self,pos,pos2)
        self.text_size = text_size
        self.font = font
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
            BaseItem.__init__(self,pos,(pos[0]+self.box.get_rect().width,pos[1]+self.box.get_rect().height))
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

    def render(self,surface):
        if self.fit_horizontal:
            self.box
        else:
            self.box = self.font.render(self.text, True, self.color)
        surface.blit(self.box,self.pos,area=self.rect)

    def set_text(self, text, same_size):
        if same_size:
            TextItem.__init__(self, self.font, text, self.pos, None, self.color, self.text_size)
        else:
            TextItem.__init__(self, self.font, text, self.pos, self.pos2, self.color, self.text_size)

class TouchObject(BaseItem):

    def __init__(self,pos,pos2):
        BaseItem.__init__(self,pos,pos2)
        self.active = False

    def is_pos_inside(self, pos):
        return self.rect_in_pos.collidepoint(pos)

    def set_active(self, active):
        self.active = active

class TouchAndTextItem(TouchObject, TextItem):

    def __init__(self, font, text, pos, pos2, color,text_size):
        TextItem.__init__(self, font, text, pos, pos2, color,text_size)
        TouchObject.__init__(self,pos,self.pos2)

    def update(self):
        TextItem.update()

    def set_active(self, active):
        self.active = active
        if active:
            color = (0,150,255)
        else:
            color = (255,255,255)
        TextItem.__init__(self.font,self.text,self.pos,self.pos2,color,self.text_size)

class Progressbar(TouchObject, TextItem):

    def __init__(self,font,text, pos, pos2, max,size, value_text):
        BaseItem.__init__(self, pos, pos2)
        logger.error(pos2)
        self.value = 0
        self.max = max
        self.back_color = (0,0,0,128)
        self.main_color = (0,150,255)
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.surface.fill(self.back_color)
        self.value_text = value_text
        if value_text:
            self.text = TextItem(font,str(self.max),pos,None,(255,255,255),size)
            self.text.set_text(str(self.value),True)
        else:
            self.text = TextItem(font,text,pos,None,(255,255,255),size)
        self.text.pos = (self.pos[0] + self.size[0] / 2 - self.text.size[0] /2,self.text.pos[1])

    def update(self):
        pass

    def render(self, surface):
        surface.blit(self.surface, self.pos)
        self.text.render(surface)

    def set_value(self, value):
        if value != self.value:
            self.value = value
            if self.value_text:
                self.set_text(str(self.value))
            self.surface.fill(self.back_color)
            pos_pixel = value * self.size[0] / self.max
            rect = pygame.Rect(0,0,pos_pixel,self.size[1])
            self.surface.fill(self.main_color, rect)

    def get_pos_value(self, pos):
        x = pos[0] - self.pos[0]
        return x * self.max / self.size[0]

    def set_text(self, text):
        self.text.set_text(text , True)