import logging
import time

import pygame

logger = logging.getLogger(__name__)


class InputManager():
    click = 1
    swipe = 2
    long_click = 3
    key = 4

    long_click_min_time = 0.3

    up = 0
    down = 1
    left = 2
    right = 3
    enter = 4

    def __init__(self, size):
        self.down_pos = (0, 0)
        self.up_pos = (0, 0)
        self.screen_size = size
        self.max_move_margin = self.screen_size[1] / 6
        self.min_swipe_move = self.screen_size[1] / 3
        self.down_button = -1
        self.down_time = -1
        self.last_key = -1

    def event(self, event):

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 4:
                touch_event = InputEvent(InputManager.swipe,
                                         self.down_pos,
                                         self.up_pos, True,
                                         InputManager.up)
                return touch_event
            elif event.button == 5:
                touch_event = InputEvent(InputManager.swipe,
                                         self.down_pos,
                                         self.up_pos, True,
                                         InputManager.down)
                return touch_event
            elif event.button == 1 and self.down_button == 1:
                touch_event = self.mouse_up(event)
                return touch_event
            elif event.button == 3 and self.down_button == 3:
                touch_event = InputEvent(InputManager.long_click,
                                         self.down_pos, self.up_pos,
                                         None, None)
                return touch_event
            else:
                return None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down(event)
            return None
        elif event.type == pygame.KEYDOWN:
            self.key_down(event)
            return None
        elif event.type == pygame.KEYUP:
            return self.key_up(event)

    def key_down(self, event):
        self.last_key = event.key
        self.down_time = time.time()

    def key_up(self, event):
        if self.last_key == event.key:
            if self.last_key == pygame.K_DOWN:
                direction = InputManager.down
            elif self.last_key == pygame.K_UP:
                direction = InputManager.up
            elif self.last_key == pygame.K_LEFT:
                direction = InputManager.left
            elif self.last_key == pygame.K_RIGHT:
                direction = InputManager.right
            elif self.last_key == pygame.K_RETURN:
                direction = InputManager.enter
            else:
                return None
            if direction is not None:
                return InputEvent(InputManager.key, None, None, None,
                                  direction)

    def mouse_down(self, event):
        self.down_pos = event.pos
        self.down_button = event.button
        self.down_time = time.time()

    def mouse_up(self, event):
        self.up_pos = event.pos
        if abs(self.down_pos[0] - self.up_pos[
            0]) < self.max_move_margin:
            if abs(self.down_pos[1] - self.up_pos[
                1]) < self.max_move_margin:
                if time.time() - InputManager.long_click_min_time > \
                        self.down_time:
                    return InputEvent(InputManager.long_click,
                                      self.down_pos,
                                      self.up_pos, None, None)
                else:
                    return InputEvent(InputManager.click,
                                      self.down_pos,
                                      self.up_pos, None, None)
            elif abs(self.down_pos[1] - self.up_pos[
                1]) > self.min_swipe_move:
                return InputEvent(InputManager.swipe, self.down_pos,
                                  self.up_pos, True, None)
        elif self.down_pos[1] - self.up_pos[1] < self.max_move_margin:
            if abs(self.down_pos[0] - self.up_pos[
                0]) > self.min_swipe_move:
                return InputEvent(InputManager.swipe, self.down_pos,
                                  self.up_pos, False, None)


class InputEvent():
    def __init__(self, event_type, down_pos, current_pos, vertical,
                 direction):
        self.type = event_type
        self.down_pos = down_pos
        self.current_pos = current_pos
        if event_type is InputManager.swipe and direction is None:
            if vertical:
                if self.down_pos[1] < self.current_pos[1]:
                    self.direction = InputManager.down
                else:
                    self.direction = InputManager.up
            else:
                if self.down_pos[0] < self.current_pos[0]:
                    self.direction = InputManager.right
                else:
                    self.direction = InputManager.left
        else:
            self.direction = direction
