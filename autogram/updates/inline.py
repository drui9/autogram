from . import UpdateBase
from typing import Dict, Callable

class inlineQuery(UpdateBase):
    handler = None
    name = 'inline_query'

    def __init__(self, update: Dict):
        print(update)

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

class chosenInlineResult(UpdateBase):
    handler = None
    name = 'chosen_inline_result'

    def __init__(self, update: Dict):
        print(update)

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)
