import pygame


change_speed = 2


class DynamicBackground:

    def __init__(self, size):
        self.image_loaded = False
        self.size = size
        self.surface = pygame.Surface(self.size).convert()
        self.surface.fill((145, 16, 16))
        self.surface_image = pygame.Surface(self.size).convert()
        self.surface_image.fill((145, 16, 16))
        self.surface_image_last = pygame.Surface(self.size).convert()
        self.update = True
        self.screen_change_percent = 100

    def draw_background(self):
        if self.image_loaded:
            if self.screen_change_percent < 255:
                self.surface.fill((0, 0, 0))
                self.surface_image_last.set_alpha(
                    255 - self.screen_change_percent)
                self.surface_image.set_alpha(self.screen_change_percent)
                self.surface.blit(self.surface_image_last, (0, 0))
                self.surface.blit(self.surface_image, (0, 0))
                self.screen_change_percent += 5
                self.update = True
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
            self.surface_image_last = self.surface_image.copy()
            pos = (int((self.size[0] - image_size[0])/2),
                   (int(self.size[1] - image_size[1])/2))
            self.surface_image.blit(blur_surf_times(
                target, self.size[0]/40, 10), pos)
            self.screen_change_percent = 0
            self.image_loaded = True
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


def blur_surf_times(surface, amt, times):
    for i in range(times):
        surface = blur_surf(surface, amt)
    return surface


# http://www.akeric.com/blog/?p=720
def blur_surf(surface, amt):
    """
    Blur the given surface by the given 'amount'.  Only values 1 and greater
    are valid.  Value 1 = no blur.
    """

    scale = 1.0/float(amt)
    surf_size = surface.get_size()
    scale_size = (int(surf_size[0]*scale), int(surf_size[1]*scale))
    surf = pygame.transform.smoothscale(surface, scale_size)
    surf = pygame.transform.smoothscale(surf, surf_size)
    return surf
