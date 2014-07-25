from .list_view import ListView


class Tracklist():

    def __init__(self, size, base_size,manager):
        self.size = size
        self.base_size = base_size
        self.list_view = ListView((0,self.base_size),(self.size[0],self.size[1]-2*self.base_size), self.base_size, manager.fonts)
        self.list_view.set_list(["track 1","track 2","track 3","track 4","track 5","track 6","track 7","track 8","track 9","track 10","track 11","track 12","track 13","track 14"])

    def update(self, screen):
        pass

    def update(self, screen):
        self.list_view.render(screen)

    def touch_event(self, touch_event):
        self.list_view.touch_event(touch_event)