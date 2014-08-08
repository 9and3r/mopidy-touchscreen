import RPi.GPIO as GPIO
import logging
import pygame

logger = logging.getLogger(__name__)


class GPIOManager():

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        # Left Button
        GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(4, GPIO.BOTH, callback=left, bouncetime=30)

         # Right Button
        GPIO.setup(21, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(21, GPIO.BOTH, callback=right, bouncetime=30)

         # Up Button
        GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(22, GPIO.BOTH, callback=up, bouncetime=30)

         # Down Button
        GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(23, GPIO.BOTH, callback=right, bouncetime=30)

         # Enter Button
        GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(24, GPIO.BOTH, callback=right, bouncetime=30)






def right(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        type = pygame.KEYUP
    else:
        type = pygame.KEYDOWN
    dict['key'] = pygame.K_RIGHT
    event = pygame.event.Event(type, dict)
    pygame.event.post(event)

def left(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        type = pygame.KEYUP
    else:
        type = pygame.KEYDOWN
    dict['key'] = pygame.K_RIGHT
    event = pygame.event.Event(type, dict)
    pygame.event.post(event)

def down(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        type = pygame.KEYUP
    else:
        type = pygame.KEYDOWN
    dict['key'] = pygame.K_DOWN
    event = pygame.event.Event(type, dict)
    pygame.event.post(event)

def up(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        type = pygame.KEYUP
    else:
        type = pygame.KEYDOWN
    dict['key'] = pygame.K_UP
    event = pygame.event.Event(type, dict)
    pygame.event.post(event)

def enter(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        type = pygame.KEYUP
    else:
        type = pygame.KEYDOWN
    dict['key'] = pygame.K_RETURN
    event = pygame.event.Event(type, dict)
    pygame.event.post(event)





