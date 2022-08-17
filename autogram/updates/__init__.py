from abc import ABC, abstractclassmethod
from loguru import logger
import json


class UpdateBase(ABC):
    subscribed_updates = set()
    autogram = None

    @classmethod
    def filter_updates(cls):
        # todo: filter updates
        filtered = {}
        return json.dumps(filtered)

    @abstractclassmethod
    def addHandler(cls):
        pass

    def __init__(self):
        self.autogram = UpdateBase.autogram
        self.logger = logger


from .channel import channelPost, editedChannelPost
from .chat import chatMember, myChatMember, chatJoinRequest
from .inline import inlineQuery, chosenInlineResult
from .message import Message, editedMessage
from .poll import Poll, pollAnswer
from .query import callbackQuery, shippingQuery, precheckoutQuery

__all__ = [
    'UpdateBase',
    'Poll', 'pollAnswer', 
    'Message','editedMessage', 
    'channelPost', 'editedChannelPost',
    'inlineQuery', 'chosenInlineResult',
    'chatMember', 'myChatMember', 'chatJoinRequest',
    'callbackQuery', 'shippingQuery', 'precheckoutQuery'
]
