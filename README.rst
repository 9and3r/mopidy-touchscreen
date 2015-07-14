******************
Mopidy-Touchscreen
******************

.. image:: https://img.shields.io/pypi/v/Mopidy-Touchscreen.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Touchscreen/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-Touchscreen.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Touchscreen/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/9and3r/mopidy-touchscreen/develop.svg?style=flat
    :target: https://travis-ci.org/9and3r/mopidy-touchscreen
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/9and3r/mopidy-touchscreen/develop.svg?style=flat
   :target: https://coveralls.io/r/9and3r/mopidy-touchscreen?branch=develop
   :alt: Test coverage

Extension for displaying track info and controlling Mopidy from a touch screen
using `PyGame <http://www.pygame.org/>`_/SDL.

Cover images are downloaded from `last.fm <http://www.last.fm/api>`_


Dependencies
============

- ``Mopidy`` >= 1.0
- ``Pykka`` >= 1.1
- ``pygame``


Installation
============

Install by running::

    pip install Mopidy-Touchscreen

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Basic Configuration
===================

Before starting Mopidy, you must add configuration for
Mopidy-Touchscreen to your Mopidy configuration file::

    [touchscreen]
    enabled = true
    screen_width = 320
    screen_height = 240
    resolution_factor = 8
    cursor = True
    fullscreen = False
    cache_dir = $XDG_CACHE_DIR/mopidy/touchscreen

The following configuration values are available:

- ``touchscreen/enabled``: If the Touchscreen extension should be enabled or
  not.

- ``touchscreen/screen_width``: The width of the resolution you want to use in
  pixels.

- ``touchscreen/screen_height``: The width of the resolution you want to use in
  pixels.
  
- ``touchscreen/resolutin_factor``: This value sets how big content is shown. Smaller values will make content bigger and less content will be displayed at once.

- ``touchscreen/cursor``: If the mouse cursor should be shown. (If you use a
  touchscreen it should be false)

- ``touchscreen/fullscreen``: If you want to be shown as a window or in
  fullscreen.

- ``touchscreen/screen_width``: The folder to be used as cache. Defaults to
  ``$XDG_CACHE_DIR/mopidy/touchscreen``, which usually means
  ``~/.cache/mopidy/touchscreen``


How to Setup
============

Use the basic configuration to setup as most standard screens works fine without further configuration.

Raspberry Pi
------------

If you are using this on a raspberry pi you have to run mopidy with root privileges:

Run Mopidy with root privileges
```````````````````````````````

You can use ``sudo mopidy``.

In case you are using musicbox edit ``/etc/init.d/mopidy`` file. Change ``DAEMON_USER=mopidy`` to ``DAEMON_USER=root``

Do not forget that this is a workaround and that mopidy will run with root privileges.

LCD Shields
```````````

If you are using a LCD Shield in Raspberry Pi you need to config your LCD:

Configure your LCD Shield
'''''''''''''''''''''''''

Add to the config the next variables::

    [touchscreen]
    sdl_fbdev = /dev/fb1
    sdl_mousdrv = TSLIB
    sdl_mousedev = event0

This is just an example. It may work but each LCD Shield seems to have its own configuration. 
To find your values find an example of using pygame with your LCD Shield and it should be something like this in the code::

    os.environ["SDL_FBDEV"] = "/dev/fb1"
    os.environ["SDL_MOUSEDRV"] = "TSLIB"
    os.environ["SDL_MOUSEDEV"] = "event0"
    
GPIO Buttons
````````````

You can use GPIO buttons to controll mopidy touchscreen. To do that set the configuration::

    [touchscreen]
    gpio = True
    gpio_left = 4
    gpio_right = 27
    gpio_up = 22
    gpio_down = 23
    gpio_enter = 24

You can choose what pins to use:

- ``touchscreen/gpio``: If you want to use gpio buttons. If this is set to false other gpio configuration values will be ignored.
- ``touchscreen/gpio_left``: Pin used to simulate left key press.
- ``touchscreen/gpio_right``: Pin used to simulate right key press.
- ``touchscreen/gpio_up``: Pin used to simulate up key press.
- ``touchscreen/gpio_down``: Pin used to simulate down key press.
- ``touchscreen/gpio_enter``: Pin used to simulate enter key press.
    
All pins numbers are in BCM mode. You can check `here <http://raspberrypi.stackexchange.com/a/12967>`_ to see the numbers for your board.

The buttons must be connected to GROUND.

Pin - Button - Ground

How To Use
==========

You can use it with a touchscreen or mouse clicking on the icons. 
In case you are using a keyboard use arrow keys to navigate and enter to select.
The GPIO buttons simulate keyboard keys so the use is exactly the same as using a keyboard.

Help
====

You can use `mopidy discuss <https://discuss.mopidy.com/>`_
or send an email to `9and3r@gmail.com <mailto:9and3r@gmail.com>`_


Features
========


* See track info (track name, album, artist, cover image)
* Seek Track
* Play/Pause
* Mute/Unmute
* Change volume
* Next/Previous track
* Library
* Menu (exit mopidy, restart...)
* Shuffle on/off
* Repeat one/on/off
* Playback list and song selection
* Playlists
* Use keyboard or GPIO buttons instead of touchscreen


Screenshots
===========

.. image:: http://oi57.tinypic.com/29yjgwo.jpg


Video
=====

`Example video running the extension <https://www.youtube.com/watch?v=KuYoIb8Q2LI>`_


Project resources
=================

- `Source code <https://github.com/9and3r/mopidy-touchscreen>`_
- `Issue tracker <https://github.com/9and3r/mopidy-touchscreen/issues>`_
- `Download development snapshot <https://github.com/9and3r/mopidy-touchscreen/archive/master.tar.gz#egg=Mopidy-Touchscreen-dev>`_


Changelog
=========

v1.0.0 (2015-05-26)
-------------------

- Require Mopidy v1.0
- Update to work with changed core playback API in Mopidy 1.0
- Search working
- GPIO and Keyboard support
- Resolution factor to adapt the interface for different screen sizes (Thanks to `Syco54645 <https://github.com/Syco54645>`_)
- Background image
- Lower CPU usage (Update screen only when needed)
- Bug Fixes

v0.3.2 (2015-01-09)
-------------------

- Bug Fixes
- UI changes
- Smoth text scrolling
- Search albums, artist or songs (Not fully implemented. Basic functionality)

v0.2.1 (2014-08-02)
-------------------

- Font will be included on installation

v0.2.0 (2014-08-02)
-------------------

- First working version
