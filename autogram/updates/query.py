from . import UpdateBase
from typing import Dict, Callable


class callbackQuery(UpdateBase):
    handler = None
    name = 'callback_query'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'callbackQuery: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

class shippingQuery(UpdateBase):
    handler = None
    name = 'shipping_query'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'shippingQuery: {update}')
    
    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

class precheckoutQuery(UpdateBase):
    handler = None
    name = 'pre_checkout_query'
    
    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'precheckoutQuery: {update}')
    
    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

