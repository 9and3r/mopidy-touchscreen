class BaseScreen():

    update_all = 0
    update_partial = 1
    no_update = 2

    def __init__(self, size, base_size, manager, fonts):
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.fonts = fonts

    def update(self, surface, update_type, rects):
        pass

    def event(self, event):
        pass

    def change_screen(self, direction):
        return False

    def should_update(self):
        return BaseScreen.update_partial
