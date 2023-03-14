'''
Python module for Mopidy Pummeluff frontend.
'''

__all__ = (
    'PummeluffFrontend',
)

from logging import getLogger
from threading import Event

import pykka
from mopidy import core as mopidy_core

from .threads import GPIOHandler, TagReader

LOGGER = getLogger(__name__)


class PummeluffFrontend(pykka.ThreadingActor, mopidy_core.CoreListener):
    '''
    Pummeluff frontend which basically reacts to GPIO button pushes and touches
    of RFID tags.
    '''

    def __init__(self, config, core):
        super().__init__()
        self.config       = config
        self.core         = core
        self.stop_event   = Event()
        self.en_gpio     = config['pummeluff']['en_gpio']
        if self.en_gpio:
            self.gpio_handler = GPIOHandler(core=core, config=config, stop_event=self.stop_event)

        self.tag_reader   = TagReader(core=core, stop_event=self.stop_event, config=config)

    def on_start(self):
        '''
        Start GPIO handler & tag reader threads.
        '''
        if self.en_gpio:
            self.gpio_handler.start()

        self.tag_reader.start()

    def on_stop(self):
        '''
        Set threading stop event to tell GPIO handler & tag reader threads to
        stop their operations.
        '''
        self.stop_event.set()
