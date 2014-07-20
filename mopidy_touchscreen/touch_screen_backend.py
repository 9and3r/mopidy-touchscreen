import pykka
from mopidy import backend
import logging

logger = logging.getLogger(__name__)

class TouchScreenBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(TouchScreenBackend, self).__init__()
        self.audio = audio
        logger.error("backend funciona")

    def on_receive(self, message):
        logger.error("heldu naiz")
        if message['action'] == 'volume':
            logger.error("bolumena aldatzen")
            self.audio.set_volume(message['value'])