from . import UpdateBase
from typing import Dict, Callable

class Notification(UpdateBase):
    name = 'notification'

    def __init__(self, update: Dict):
        self.notice = update
        self.autogram.logger.debug(f'Notification: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler

    def __repr__(self):
        return str(vars(self))

