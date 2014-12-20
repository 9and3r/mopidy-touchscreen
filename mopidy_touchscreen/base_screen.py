__author__ = 'ander'


class BaseScreen():

    def __init__(self, size, base_size, manager, fonts):
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.fonts = fonts

    def update(self, surface):
        pass

    def event(self, event):
        pass
