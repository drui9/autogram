from . import UpdateBase
from typing import Dict, Callable


class inlineQuery(UpdateBase):
    name = 'inline_query'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'inlineQuery: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

