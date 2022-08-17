from . import UpdateBase
from typing import Dict, Callable

class myChatMember(UpdateBase):
    handler = None
    name = 'my_chat_member'

    def __init__(self, update: Dict):
        print(update)
    
    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

class chatMember(UpdateBase):
    handler = None
    name = 'chat_member'

    def __init__(self, update: Dict):
        print(update)
    
    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

class chatJoinRequest(UpdateBase):
    handler = None
    name = 'chat_join_request'
    
    def __init__(self, update: Dict):
        print(update)
    
    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)
