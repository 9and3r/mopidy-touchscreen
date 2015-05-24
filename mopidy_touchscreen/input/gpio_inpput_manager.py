import logging

import RPi.GPIO as GPIO

import pygame


logger = logging.getLogger(__name__)


class GPIOManager():
    def __init__(self, pins):
        GPIO.setmode(GPIO.BCM)

        # Left Button
        GPIO.setup(pins['left'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pins['left'], GPIO.BOTH, callback=left,
                              bouncetime=30)

        # Right Button
        GPIO.setup(pins['right'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pins['right'], GPIO.BOTH,
                              callback=right,
                              bouncetime=30)

        # Up Button
        GPIO.setup(pins['up'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pins['up'], GPIO.BOTH, callback=up,
                              bouncetime=30)

        # Down Button
        GPIO.setup(pins['down'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pins['down'], GPIO.BOTH, callback=right,
                              bouncetime=30)

        # Enter Button
        GPIO.setup(pins['enter'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pins['enter'], GPIO.BOTH,
                              callback=right,
                              bouncetime=30)


def right(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        type = pygame.KEYUP
    else:
        type = pygame.KEYDOWN
        dict['unicode'] = None
    dict['key'] = pygame.K_RIGHT
    event = pygame.event.Event(type, dict)
    pygame.event.post(event)


def left(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        type = pygame.KEYUP
    else:
        type = pygame.KEYDOWN
        dict['unicode'] = None
    dict['key'] = pygame.K_RIGHT
    event = pygame.event.Event(type, dict)
    pygame.event.post(event)


def down(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        type = pygame.KEYUP
    else:
        type = pygame.KEYDOWN
        dict['unicode'] = None
    dict['key'] = pygame.K_DOWN
    event = pygame.event.Event(type, dict)
    pygame.event.post(event)


def up(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        type = pygame.KEYUP
    else:
        type = pygame.KEYDOWN
        dict['unicode'] = None
    dict['key'] = pygame.K_UP
    event = pygame.event.Event(type, dict)
    pygame.event.post(event)


def enter(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        type = pygame.KEYUP
    else:
        type = pygame.KEYDOWN
        dict['unicode'] = None
    dict['key'] = pygame.K_RETURN
    event = pygame.event.Event(type, dict)
    pygame.event.post(event)
