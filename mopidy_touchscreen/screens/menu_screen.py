import os
import socket

from base_screen import BaseScreen

from ..graphic_utils import ListView


class MenuScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.ip = None
        self.list = ListView((0, 0), size, base_size, fonts['base'])

        self.list_items = ["Exit Mopidy", "Shutdown", "Restart", "IP: "]

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
                os.system("pkill mopidy")
            elif clicked == 1:
                if os.system("gksu -- shutdown now -h") != 0:
                    os.system("sudo shutdown now -h")
            elif clicked == 2:
                if os.system("gksu -- shutdown -r now") != 0:
                    os.system("sudo shutdown -r now")
            elif clicked == 3:
                self.check_connection()

    # Will check internet connection
    def check_connection(self):
        try:
            self.manager.set_connection(False, True)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.ip = s.getsockname()[0]
            s.close()
            self.list_items[3] = "IP: " + self.ip
            self.list.set_list(self.list_items)
            self.manager.set_connection(True, False)
        except socket.error:
            s.close()
            self.ip = None
            self.list_items[3] = "IP: No internet"
            self.list.set_list(self.list_items)
            self.manager.set_connection(False, False)
