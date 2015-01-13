import random
import logging

change_speed = 2


class DynamicBackground():
    def __init__(self):
        self.current = get_valid_color()
        self.target = get_valid_color()
        self.auto_mode = True
        self.target_current_same = False

    def draw_background(self, surface):
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
        surface.fill(self.current)

    def set_target_color(self, color):
        if color is not None:
            self.target = get_similar_valid_color(color)
            self.auto_mode = False
            self.target_current_same = False
        else:
            self.auto_mode = True
            self.target = get_valid_color()
            self.target_current_same = False

# It will return the same color if sum is less than 510
# Otherwise a darker color will be returned
# White text should be seen ok with this background color

def get_similar_valid_color(color):
    sum = color[0] + color[1] + color[2]
    new_color = [0, 0, 0]
    if sum > 510:
        rest = (sum - 510)/3 + 1
        for x in range(0,3):
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