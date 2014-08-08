import RPi.GPIO as GPIO
import logging

logger = logging.getLogger(__name__)


class GPIOManager():

    def __init__(self):
        GPIO.add_event_detect(23, GPIO.RISING, callback=self.printFunction, bouncetime=300)


    def printFunction(self):
        logger.error("Sakatu da")
