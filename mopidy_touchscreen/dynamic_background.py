import random


class DynamicBackground():
    def __init__(self):
        self.current = get_valid_color()
        self.target = get_valid_color()

    def draw_background(self, surface):
        same = True
        for x in range(0, 3):
            if self.current[x] > self.target[x]:
                self.current[x] -= 1
            elif self.current[x] < self.target[x]:
                self.current[x] += 1
            if self.current != self.target:
                same = False
        if same:
            self.target = get_valid_color()
        surface.fill(self.current)


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