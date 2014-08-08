import RPi.GPIO as GPIO
import logging

logger = logging.getLogger(__name__)


class GPIOManager():

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(24, GPIO.BOTH, callback=self.printFunction, bouncetime=30)

    def printFunction(self, channel):
        logger.error(channel)





