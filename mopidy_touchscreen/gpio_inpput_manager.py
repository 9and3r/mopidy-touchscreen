import RPi.GPIO as GPIO
import logging
import pygame

logger = logging.getLogger(__name__)


class GPIOManager():

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(24, GPIO.BOTH, callback=right(), bouncetime=30)


def right(channel):
    dict = {}
    if GPIO.input(channel) == 1:
        dict['type'] = pygame.KEYUP
    else:
        dict['type'] = pygame.KEYDOWN
    dict['key'] = pygame.K_RIGHT
    event = pygame.event.Event(dict)
    pygame.event.post(event)






