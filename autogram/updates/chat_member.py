from . import UpdateBase
from typing import Dict, Callable


class chatMember(UpdateBase):
    name = 'chat_member'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'chatMember: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

