from . import UpdateBase
from typing import Dict, Callable
from contextlib import contextmanager


class callbackQuery(UpdateBase):
    name = 'callback_query'

    def __init__(self, update: Dict):
        self.answered = False
        self.id = update.pop('id')
        self.data = update.pop('data')
        self.sender = update.pop('from')
        self.message = update.pop('message')
        self.chat_instance = update.pop('chat_instance')
        #
        if self.handler:
            try:
                self.handler()
            except Exception as e:
                self.logger.exception(e)
            finally:
                if not self.answered:
                    self.answerCallbackQuery()
        else:
            self.logger.debug(f"Unimplemented: {self}")
        return

    def answerCallbackQuery(self, **kwargs):
        if 'params' not in kwargs.keys():
            kwargs |= {'params': {}}
        self.autogram.answerCallbackQuery(self.id, **kwargs)
        self.answered = True
        return

    def delete(self):
        """Delete trigger message"""
        chat_id = self.message['chat']['id']
        msg_id = self.message['message_id']
        self.autogram.deleteMessage(chat_id, msg_id)

    def __repr__(self) -> str:
        return f"CallbackQuery(id: {self.id}, data: {self.data})"

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

