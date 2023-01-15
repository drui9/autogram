from . import UpdateBase
from typing import Dict, Callable

class channelPost(UpdateBase):
    handler = None
    name = 'channel_post'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'channelPost: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

