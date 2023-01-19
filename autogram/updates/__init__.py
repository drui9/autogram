import json
import loguru
from typing import Any, Callable

class UpdateBase():
    logger = loguru.logger
    subscribed_updates = set()
    autogram : Any = None
    handler : Callable = None
    text: str = ''

    @classmethod
    def filter_updates(cls):
        # todo: filter updates
        filtered = {}
        print(filtered)
        return json.dumps(filtered)

    def __init__(self):
        self.autogram = UpdateBase.autogram
#
from .chosenInline_result import chosenInlineResult
from .editedChannel_post import editedChannelPost
from .precheckout_query import precheckoutQuery
from .chatJoin_request import chatJoinRequest
from .edited_message import editedMessage
from .callback_query import callbackQuery
from .shipping_query import shippingQuery
from .myChat_member import myChatMember
from .inline_query import inlineQuery
from .channel_post import channelPost
from .chat_member import chatMember
from .poll_answer import pollAnswer
from .notices import Notification
from .message import Message
from .poll import Poll
#

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
