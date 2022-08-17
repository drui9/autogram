from . import UpdateBase
from typing import Dict, Callable

class channelPost(UpdateBase):
    handler = None 
    name = 'channel_post'

    def __init__(self, update: Dict):
        print(update)

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

class editedChannelPost(UpdateBase):
    handler = None
    name = 'edited_channel_post'

    def __init__(self, update: Dict):
        print(update)

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)
