from . import UpdateBase
from typing import Dict, Callable


class callbackQuery(UpdateBase):
    name = 'callback_query'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'callbackQuery: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

