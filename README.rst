****************************
Mopidy-Touchscreen
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-Touchscreen.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Touchscreen/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-Touchscreen.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Touchscreen/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/9and3r/modipy-touchscreen/master.png?style=flat
    :target: https://travis-ci.org/9and3r/modipy-touchscreen
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/9and3r/modipy-touchscreen/master.svg?style=flat
   :target: https://coveralls.io/r/9and3r/modipy-touchscreen?branch=master
   :alt: Test coverage

Mopidy extension to show info on a display and control from it

.. image:: http://i60.tinypic.com/i4l0fq.jpg


Installation
============

Install by running::

    pip install Mopidy-Touchscreen

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-Touchscreen to your Mopidy configuration file::

    [touchscreen]
    enabled = true

Features
=============

Working
-------

*Seek Track
*Play/Pause
*Mute/Unmute
*Change volume
*Next/Previous track
*See track info (track name, album, artist, cover image)

Planned
-------

-Resolution on config file
-Shuffle on/off
-Repeat one/on/off
-Playback list and control
-Playlists
-Library
-Menu (exit mopidy, restart...)
-Use keyboard or GPIO buttons instead of touchscreen

Screenshots
===========

.. image:: http://tinypic.com/r/i4l0fq/8

.. image:: http://tinypic.com/r/nd7vk1/8
Extension running on [Texy's display](http://www.raspberrypi.org/forums/viewtopic.php?f=93&t=65566)

Project resources
=================

- `Source code <https://github.com/9and3r/mopidy-touchscreen>`_
- `Issue tracker <https://github.com/9and3r/mopidy-touchscreen/issues>`_
- `Download development snapshot <https://github.com/9and3r/mopidy-touchscreen/archive/master.tar.gz#egg=Mopidy-Touchscreen-dev>`_


Changelog
=========

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
