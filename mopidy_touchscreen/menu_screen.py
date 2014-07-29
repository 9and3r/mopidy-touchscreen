from .list_view import ListView
from .screen_objects import *
import mopidy
import os
import socket


class MenuScreen():

    def __init__(self, size, base_size, manager):
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.ip = None
        self.screen_objects = ScreenObjectsManager()

        #Exit mopidy button
        button = TouchAndTextItem(self.manager.fonts['icon'], u"\ue611", (0, self.base_size), None)
        self.screen_objects.set_touch_object("exit_icon", button)
        button = TouchAndTextItem(self.manager.fonts['base'], "Exit Mopidy", (button.get_right_pos(), self.base_size), None)
        self.screen_objects.set_touch_object("exit", button)

        #Shutdown button
        button = TouchAndTextItem(self.manager.fonts['icon'], u"\ue60b", (0, self.base_size * 2), None)
        self.screen_objects.set_touch_object("shutdown_icon", button)
        button = TouchAndTextItem(self.manager.fonts['base'], "Shutdown", (button.get_right_pos(), self.base_size * 2), None)
        self.screen_objects.set_touch_object("shutdown", button)

        #Restart button
        button = TouchAndTextItem(self.manager.fonts['icon'], u"\ue609", (0, self.base_size * 3), None)
        self.screen_objects.set_touch_object("restart_icon", button)
        button = TouchAndTextItem(self.manager.fonts['base'], "Restart", (button.get_right_pos(), self.base_size * 3), None)
        self.screen_objects.set_touch_object("restart", button)

        #IP addres
        button = TouchAndTextItem(self.manager.fonts['base'], "IP: ", (0, self.base_size * 4), None)
        self.screen_objects.set_touch_object("ip", button)

        #self.list_view = ListView((0,self.base_size),(self.size[0],self.size[1]-2*self.base_size), self.base_size, manager.fonts)
        #self.list_view.set_list(["Exit mopidy", "Shutdown", "Restart"])



    def update(self, screen):
        self.screen_objects.render(screen)
        #self.list_view.render(screen)

    def touch_event(self, touch_event):
        #clicked = self.list_view.touch_event(touch_event)
        clicked = self.screen_objects.get_touch_objects_in_pos(touch_event.current_pos)
        for key in clicked:
            if key == "exit_icon" or key == "exit":
                mopidy.utils.process.exit_process()
            elif key == "shutdown_icon" or key == "shutdown":
                os.system("shutdown now -h")
            elif key == "ip":
                self.check_connection()

    def check_connection(self):
        try:
            self.manager.set_connection(False, True)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.ip = s.getsockname()[0]
            s.close()
            self.screen_objects.get_touch_object("ip").set_text("IP: " + self.ip, "None")
            self.manager.set_connection(True, False)
        except socket.error:
            s.close()
            self.ip = None
            self.screen_objects.get_touch_object("ip").set_text("IP: No internet", "None")
            self.manager.set_connection(False, False)

