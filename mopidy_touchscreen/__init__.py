from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext

from .touch_screen import TouchScreen
from .touch_screen_backend import TouchScreenBackend


__version__ = '0.2.2'

# TODO: If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)


class Extension(ext.Extension):
    dist_name = 'Mopidy-Touchscreen'
    ext_name = 'touchscreen'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['screen_width'] = config.Integer(minimum=1)
        schema['screen_height'] = config.Integer(minimum=1)
        schema['cursor'] = config.Boolean()
        schema['fullscreen'] = config.Boolean()
        schema['cache_dir'] = config.Path()
        schema['gpio'] = config.Boolean()
        schema['gpio_left'] = config.Integer()
        schema['gpio_right'] = config.Integer()
        schema['gpio_up'] = config.Integer()
        schema['gpio_down'] = config.Integer()
        schema['gpio_enter'] = config.Integer()
	schema['sdl_fbdev'] = config.String()
	schema['sdl_mousdrv'] = config.String()
	schema['sdl_mousedev'] = config.String()
        return schema

    def setup(self, registry):
        registry.add('frontend', TouchScreen)

        # Backend used for controling volume
        registry.add('backend', TouchScreenBackend)
