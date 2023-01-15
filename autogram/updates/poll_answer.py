from . import UpdateBase
from typing import Dict, Callable


class pollAnswer(UpdateBase):
    name = 'poll_answer'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'pollAnswer: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

