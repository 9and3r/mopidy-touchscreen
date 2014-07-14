from __future__ import unicode_literals

import logging
import os

# TODO: Remove entirely if you don't register GStreamer elements below
import pygst
pygst.require('0.10')
import gst
import gobject

from mopidy import config, ext


__version__ = '0.1.0'

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
        # TODO: Comment in and edit, or remove entirely
        #schema['username'] = config.String()
        #schema['password'] = config.Secret()
        return schema

    def setup(self, registry):
        # You will typically only implement one of the following things
        # in a single extension.
	from .touch_screen import TouchScreen
        registry.add('frontend', TouchScreen)
        
