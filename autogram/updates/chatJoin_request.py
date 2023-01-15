from . import UpdateBase
from typing import Dict, Callable


class chatJoinRequest(UpdateBase):
    name = 'chat_join_request'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'chatJoinRequest: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

