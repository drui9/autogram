from . import UpdateBase
from typing import Dict, Callable


class precheckoutQuery(UpdateBase):
    name = 'pre_checkout_query'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'precheckoutQuery: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

