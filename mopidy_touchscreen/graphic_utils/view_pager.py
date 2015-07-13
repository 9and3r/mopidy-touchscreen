__author__ = 'ander'

from ..screens.base_screen import BaseScreen
import traceback


class ViewPager:

    def __init__(self, size, manager):
        self.size = size
        self.objets_manager = [manager.create_objects_manager(), manager.create_objects_manager(), manager.create_objects_manager()]
        self.pos = 0
        self.manager = manager
        self.next = False
        self.direction = 0
        self.previous = False
        self.speed = self.size[0] / 15
        self.update = False
        self.update_rects = []

    def notify_changed(self):
        try:
            for i in range(0, 3, 1):
                self.manager.set_page_values(self.objets_manager[i], i)
            self.update = True
        except:
            traceback.print_exc()

    def change_to_page(self, page):
        self.direction = page
        self.update = True

    def should_update(self):
        if self.update:
            return BaseScreen.update_all
        else:
            if len(self.update_rects)>0:
                return BaseScreen.update_partial
            else:
                return BaseScreen.no_update

    def shift(self):
        if self.direction == 1:
            if -self.pos > self.size[0]:
                self.pos = 0
                self.direction = 0
                aux = self.objets_manager[0]
                self.objets_manager[0] = self.objets_manager[1]
                self.objets_manager[1] = self.objets_manager[2]
                self.objets_manager[2] = aux
                self.notify_changed()
            else:
                self.pos -= self.speed
            self.objets_manager[2].set_horizontal_shift(self.size[0] + self.pos)
            self.objets_manager[1].set_horizontal_shift(self.pos)
        elif self.direction == -1:
            if self.pos > self.size[0]:
                self.pos = 0
                self.direction = 0
                aux = self.objets_manager[2]
                self.objets_manager[2] = self.objets_manager[1]
                self.objets_manager[1] = self.objets_manager[0]
                self.objets_manager[0] = aux
                self.notify_changed()
            else:
                self.pos += self.speed
            self.objets_manager[0].set_horizontal_shift(-self.size[0] + self.pos)
            self.objets_manager[1].set_horizontal_shift(self.pos)

    def render(self, screen, update_type):
        if self.direction != 0:
            self.shift()
        if self.pos != 0:
            if self.direction == 1:
                self.objets_manager[2].render(screen)
            elif self.direction == -1:
                self.objets_manager[0].render(screen)
        else:
            self.update = False
            self.update_rects = self.objets_manager[1].get_update_rects()
            #if update_type == BaseScreen.update_partial:
                #rects += self.update_rects

        self.objets_manager[1].render(screen)