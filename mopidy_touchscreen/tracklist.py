from .list_view import ListView


class Tracklist():

    def __init__(self, size, base_size,manager):
        self.size = size
        self.base_size = base_size
        self.list_view = ListView((0,self.base_size),(self.size[0],self.size[1]-2*self.base_size), self.base_size, manager.fonts)
        self.list_view.set_list(["track 1","track 2"])

    def update(self, screen):
        pass

    def update(self, screen):
        self.list_view.render(screen)