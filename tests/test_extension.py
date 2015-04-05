# from __future__ import unicode_literals

import unittest

import pygame

from mopidy_touchscreen import Extension

from mopidy_touchscreen.graphic_utils.list_view import ListView


# ,touch_screen as frontend_lib


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        self.assertIn('[touchscreen]', config)
        self.assertIn('enabled = true', config)

    def test_get_config_schema(self):
        pass
        # ext = Extension()

        # schema = ext.get_config_schema()

        # TODO Test the content of your config schema
        # self.assertIn('username', schema)
        # self.assertIn('password', schema)

    def test_list_view(self):
        pygame.init()
        font = pygame.font.SysFont("arial", 200/6)
        list = ListView((0, 0), (200, 200), 200/6, font)
        list.set_list(["item1", "item2", "item3"])
