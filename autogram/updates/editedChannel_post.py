from . import UpdateBase
from typing import Dict, Callable


class editedChannelPost(UpdateBase):
    name = 'edited_channel_post'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'editedChannelPost: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

