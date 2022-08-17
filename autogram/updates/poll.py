from . import UpdateBase
from typing import Dict, Callable

class Poll(UpdateBase):
    handler = None
    name = 'poll'

    def __init__(self, update: Dict):
        print(update)
    
    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

class pollAnswer(UpdateBase):
    handler = None 
    name = 'poll_answer'
    
    def __init__(self, update: Dict):
        print(update)
    
    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)
