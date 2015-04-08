import random

import pygame

change_speed = 2


class DynamicBackground():
    def __init__(self, size):
        self.current = get_valid_color()
        self.target = get_valid_color()
        self.auto_mode = True
        self.image_loaded = False
        self.size = size
        self.surface = pygame.Surface(self.size).convert()
        self.target_current_same = False

    def draw_background(self):
        if self.image_loaded:
            return self.surface.copy()
        else:
            if not self.target_current_same:
                for x in range(0, 3):
                    if abs(self.current[x]-self.target[x]) < change_speed:
                        self.current[x] = self.target[x]
                        self.target_current_same = True
                    else:
                        self.target_current_same = False
                        if self.current[x] > self.target[x]:
                            self.current[x] -= change_speed
                        elif self.current[x] < self.target[x]:
                            self.current[x] += change_speed
            if self.auto_mode and self.target_current_same:
                self.target = get_valid_color()
                self.target_current_same = False
            self.surface.fill(self.current)
            return self.surface.copy()

    def set_target_color(self, color, image):
        if color is not None:
            self.auto_mode = False
            self.target_current_same = False
            self.target = get_similar_valid_color(color)
        else:
            self.auto_mode = True
            self.target = get_valid_color()
            self.target_current_same = False

        if image is not None:
            image_size = get_aspect_scale_size(image, self.size)
            target = pygame.transform.smoothscale(image, image_size)
            target.set_alpha(150)
            self.image_loaded = True
            self.surface.fill((0, 0, 0))
            pos = ((self.size[0] - image_size[0])/2,
                   (self.size[1] - image_size[1])/2)
            self.surface.blit(target, pos)
        else:
            self.image_loaded = False

# It will return the same color if sum is less than 510
# Otherwise a darker color will be returned
# White text should be seen ok with this background color


def get_similar_valid_color(color):
    sum = color[0] + color[1] + color[2]
    new_color = [0, 0, 0]
    if sum > 510:
        rest = (sum - 510)/3 + 1
        for x in range(0, 3):
            new_color[x] = color[x] - rest
        return new_color
    else:
        return color

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


def get_aspect_scale_size(img, (bx, by)):
    size = img.get_size()
    aspect_x = bx / float(size[0])
    aspect_y = by / float(size[1])
    if aspect_x > aspect_y:
        aspect = aspect_x
    else:
        aspect = aspect_y

    new_size = (int(aspect*size[0]), int(aspect*size[1]))
    return new_size
