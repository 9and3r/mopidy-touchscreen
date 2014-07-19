import pygame
import  logging

logger = logging.getLogger(__name__)


class TouchManager():

    click = 1

    def __init__(self):
        self.down_pos = (0, 0)
        self.up_pos = (0, 0)

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            return self.mouse_up(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return None

    def mouse_down(self, event):
        self.down_pos = event.pos

    def mouse_up(self,event):
        self.up_pos = event.pos
        return TouchEvent(TouchManager.click, self.down_pos, self.up_pos)

class TouchEvent():

    def __init__(self, event_type, down_pos, current_pos):
        self.type = event_type
        self.down_pos = down_pos
        self.current_pos = current_pos