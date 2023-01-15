from . import UpdateBase
from typing import Dict, Callable


class chosenInlineResult(UpdateBase):
    name = 'chosen_inline_result'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'chosenInlineResult: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

