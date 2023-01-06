from abc import ABC, abstractclassmethod
from typing import Callable
from loguru import logger
import json


class UpdateBase(ABC):
    subscribed_updates = set()
    autogram = None

    @classmethod
    def filter_updates(cls):
        # todo: filter updates
        filtered = {}
        print(filtered)
        return json.dumps(filtered)

    def __init__(self):
        self.autogram = UpdateBase.autogram
        self.logger = logger


from .channel import channelPost, editedChannelPost
from .chat import chatMember, myChatMember, chatJoinRequest
from .inline import inlineQuery, chosenInlineResult
from .message import Message, editedMessage
from .poll import Poll, pollAnswer
from .query import callbackQuery, shippingQuery, precheckoutQuery

## extras
from .notices import Notification

__all__ = [
    'UpdateBase',
    'Notification',
    'Poll', 'pollAnswer',
    'Message','editedMessage',
    'channelPost', 'editedChannelPost',
    'inlineQuery', 'chosenInlineResult',
    'chatMember', 'myChatMember', 'chatJoinRequest',
    'callbackQuery', 'shippingQuery', 'precheckoutQuery'
]
