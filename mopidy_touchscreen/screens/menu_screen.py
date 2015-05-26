import os
import socket

from base_screen import BaseScreen

from ..graphic_utils import ListView


class MenuScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts, core):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.ip = None
        self.core = core
        self.list = ListView((0, 0), (size[0], size[1]-base_size),
                             base_size, fonts['base'])

        self.list_items = ["Random", "Repeat", "Single", "Consume",
                           "Exit Mopidy", "Shutdown", "Restart", "IP: "]

        self.list.set_list(self.list_items)

    def should_update(self):
        return self.list.should_update()

    def update(self, screen, update_type, rects):
        update_all = (update_type == BaseScreen.update_all)
        self.list.render(screen, update_all, rects)

    def touch_event(self, event):
        clicked = self.list.touch_event(event)
        if clicked is not None:
            if clicked == 0:
                random = not self.core.tracklist.get_random().get()
                self.core.tracklist.set_random(random)
            elif clicked == 1:
                repeat = not self.core.tracklist.get_repeat().get()
                self.core.tracklist.set_repeat(repeat)
            elif clicked == 2:
                single = not self.core.tracklist.get_single().get()
                self.core.tracklist.set_single(single)
            elif clicked == 3:
                consume = not self.core.tracklist.get_consume().get()
                self.core.tracklist.set_consume(consume)
            elif clicked == 4:
                os.system("pkill mopidy")
            elif clicked == 5:
                if os.system("gksu -- shutdown now -h") != 0:
                    os.system("sudo shutdown now -h")
            elif clicked == 6:
                if os.system("gksu -- shutdown -r now") != 0:
                    os.system("sudo shutdown -r now")
            elif clicked == 7:
                self.check_connection()

    # Will check internet connection
    def check_connection(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.ip = s.getsockname()[0]
            s.close()
            self.list_items[7] = "IP: " + self.ip
            self.list.set_list(self.list_items)
        except socket.error:
            s.close()
            self.ip = None
            self.list_items[7] = "IP: No internet"
            self.list.set_list(self.list_items)

    def options_changed(self):
        active = []
        if self.core.tracklist.random.get():
            active.append(0)
        if self.core.tracklist.repeat.get():
            active.append(1)
        if self.core.tracklist.single.get():
            active.append(2)
        if self.core.tracklist.consume.get():
            active.append(3)
        self.list.set_active(active)

    def set_connection(self, connection, loading):
        internet = self.touch_text_manager.get_touch_object(
            "internet")
        if loading:
            internet.set_text(u"\ue627", None)
            internet.set_active(False)
        else:
            internet.set_text(u"\ue602", None)
            internet.set_active(connection)
