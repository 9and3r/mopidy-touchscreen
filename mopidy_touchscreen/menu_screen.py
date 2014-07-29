from .list_view import ListView

class MenuScreen():

    def __init__(self, size, base_size, manager):
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.list_view = ListView((0,self.base_size),(self.size[0],self.size[1]-2*self.base_size), self.base_size, manager.fonts)
        self.list_view.set_list(["Exit mopidy", "Shutdown", "Restart"])

    def update(self, screen):
        self.list_view.render(screen)

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event)
        if clicked is not None:
            pass