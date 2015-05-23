import pygame

change_speed = 2


class DynamicBackground:

    def __init__(self, size):
        self.image_loaded = False
        self.size = size
        self.surface = pygame.Surface(self.size).convert()
        self.surface.fill((145, 16, 16))
        self.surface_image = pygame.Surface(self.size).convert()
        self.update = True

    def draw_background(self):
        if self.image_loaded:
            return self.surface_image.copy()
        else:
            return self.surface.copy()

    def should_update(self):
        if self.update:
            self.update = False
            return True
        else:
            return False

    def set_background_image(self, image):
        if image is not None:
            image_size = get_aspect_scale_size(image, self.size)
            target = pygame.transform.smoothscale(image, image_size)
            target.set_alpha(150)
            self.image_loaded = True
            self.surface_image.fill((0, 0, 0))
            pos = ((self.size[0] - image_size[0])/2,
                   (self.size[1] - image_size[1])/2)
            self.surface_image.blit(target, pos)
        else:
            self.image_loaded = False
        self.update = True


def get_aspect_scale_size(img, new_size):
    size = img.get_size()
    aspect_x = new_size[0] / float(size[0])
    aspect_y = new_size[1] / float(size[1])
    if aspect_x > aspect_y:
        aspect = aspect_x
    else:
        aspect = aspect_y
    new_size = (int(aspect*size[0]), int(aspect*size[1]))
    return new_size
