from . import UpdateBase
from typing import Dict, Callable


class editedMessage(UpdateBase):
    name = 'edited_message'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'editedMessage: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

