import os
import socket
import mopidy

from .screen_objects import ScreenObjectsManager, TouchAndTextItem
from .input_manager import InputManager
from .base_screen import BaseScreen


class MenuScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.ip = None
        self.screen_objects = ScreenObjectsManager()

        # Exit mopidy button
        button = TouchAndTextItem(self.manager.fonts['icon'],
                                  u"\ue611",
                                  (0, 0), None)
        self.screen_objects.set_touch_object("exit_icon", button)
        button = TouchAndTextItem(self.fonts['base'],
                                  "Exit Mopidy",
                                  (button.get_right_pos(),
                                   0),
                                  None)
        self.screen_objects.set_touch_object("exit", button)

        # Shutdown button
        button = TouchAndTextItem(self.fonts['icon'],
                                  u"\ue60b",
                                  (0, self.base_size * 1), None)
        self.screen_objects.set_touch_object("shutdown_icon", button)
        button = TouchAndTextItem(self.fonts['base'],
                                  "Shutdown",
                                  (button.get_right_pos(),
                                   self.base_size * 1),
                                  None)
        self.screen_objects.set_touch_object("shutdown", button)

        # Restart button
        button = TouchAndTextItem(self.fonts['icon'],
                                  u"\ue609",
                                  (0, self.base_size * 2), None)
        self.screen_objects.set_touch_object("restart_icon", button)
        button = TouchAndTextItem(self.fonts['base'],
                                  "Restart",
                                  (button.get_right_pos(),
                                   self.base_size * 2),
                                  None)
        self.screen_objects.set_touch_object("restart", button)

        # IP addres
        button = TouchAndTextItem(self.fonts['base'], "IP: ",
                                  (0, self.base_size * 3), None)
        self.screen_objects.set_touch_object("ip", button)

    def update(self, screen, update_all):
        self.screen_objects.render(screen)

    def touch_event(self, event):
        if event.type == InputManager.click:
            clicked = self.screen_objects.get_touch_objects_in_pos(
                event.current_pos)
            for key in clicked:
                if key == "exit_icon" or key == "exit":
                    mopidy.utils.process.exit_process()
                elif key == "shutdown_icon" or key == "shutdown":
                    if os.system("gksu -- shutdown now -h") != 0:
                        os.system("shutdown now -h")
                elif key == "restart_icon" or key == "restart":
                    if os.system("gksu -- shutdown -r now") != 0:
                        os.system("shutdown -r now")
                elif key == "ip":
                    self.check_connection()

    # Will check internet connection
    def check_connection(self):
        try:
            self.manager.set_connection(False, True)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.ip = s.getsockname()[0]
            s.close()
            self.screen_objects.get_touch_object("ip").set_text(
                "IP: " + self.ip, "None")
            self.manager.set_connection(True, False)
        except socket.error:
            s.close()
            self.ip = None
            self.screen_objects.get_touch_object("ip").set_text(
                "IP: No internet", "None")
            self.manager.set_connection(False, False)
