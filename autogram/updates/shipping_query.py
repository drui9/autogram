from . import UpdateBase
from typing import Dict, Callable


class shippingQuery(UpdateBase):
    name = 'shipping_query'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'shippingQuery: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

