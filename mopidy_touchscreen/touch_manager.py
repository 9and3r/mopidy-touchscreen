import pygame
import  logging

logger = logging.getLogger(__name__)


class TouchManager():

    click = 1
    swipe = 2

    up = 0
    down = 1
    left = 2
    right = 3

    def __init__(self,size):
        self.down_pos = (0, 0)
        self.up_pos = (0, 0)
        self.screen_size = size
        self.max_move_margin = self.screen_size[1] / 6
        self.min_swipe_move = self.screen_size[1] / 3

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            return self.mouse_up(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down(event)
            return None

    def mouse_down(self, event):
        self.down_pos = event.pos

    def mouse_up(self,event):
        self.up_pos = event.pos
        if abs(self.down_pos[0] - self.up_pos[0]) < self.max_move_margin:
            if abs(self.down_pos[1] - self.up_pos[1]) < self.max_move_margin:
                return TouchEvent(TouchManager.click, self.down_pos, self.up_pos, None)
            elif abs(self.down_pos[1] - self.up_pos[1]) > self.min_swipe_move:
                return TouchEvent(TouchManager.swipe, self.down_pos, self.up_pos, True)
        elif self.down_pos[1] - self.up_pos[1] < self.max_move_margin:
            logger.error("hemen nago")
            logger.error( abs(self.down_pos[1] - self.up_pos[1]))
            if abs(self.down_pos[0] - self.up_pos[0]) > self.min_swipe_move:
                logger.error("kaixo")
                return TouchEvent(TouchManager.swipe, self.down_pos, self.up_pos, False)


class TouchEvent():

    def __init__(self, event_type, down_pos, current_pos, vertical):
        self.type = event_type
        self.down_pos = down_pos
        self.current_pos = current_pos
        if event_type is TouchManager.swipe:
            if vertical:
                if self.down_pos[1] < self.current_pos[1]:
                    self.direction = TouchManager.down
                else:
                    self.direction = TouchManager.up
            else:
                if self.down_pos[0] < self.current_pos[0]:
                    self.direction = TouchManager.right
                else:
                    self.direction = TouchManager.left