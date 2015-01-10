import random

change_speed = 2

import pygame



class DynamicBackground():
    def __init__(self, size):
        self.size = size
        self.current = get_valid_color()
        self.target = get_valid_color()
        self.surface = None

    def draw_background(self, surface):
        same = True
        for x in range(0, 3):
            if abs(self.current[x]-self.target[x]) < change_speed:
                self.current[x] = self.target[x]
            else:
                if self.current[x] > self.target[x]:
                    self.current[x] -= change_speed
                elif self.current[x] < self.target[x]:
                    self.current[x] += change_speed
                if self.current != self.target:
                    same = False
        #if same:
        #    self.target = get_valid_color()
        surface.fill(self.current)
        if self.surface is not None:
            surface.blit(self.surface,(0,0))

    def set_target_color(self, color, surface):
        self.target = [color[0], color[1], color[2]]
        #irudi = pygame.Surface(surface.get_size())
        #pygame.transform.laplacian(surface, irudi)
        irudi = surface
        target = pygame.Surface(self.size)
        pygame.transform.smoothscale(irudi, self.size, target)
        target.set_alpha(80)
        self.surface = target


# Returns an array with 3 integers in range of 0-255
# The sum of the three integers will be lower than 255*2
# (510) to avoid very bright colors
# White text should be seen ok with this background color


def get_valid_color():
    color = [0, 0, 0]
    total = 0
    for i in range(0, 3):
        color[i] = random.randint(0, 255)
        total += color[i]
    extra = total - 510
    if extra > 0:
        i = random.randint(0, 2)
        color[i] -= extra
    return color