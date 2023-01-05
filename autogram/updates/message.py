from . import UpdateBase
from typing import Dict, Callable
from autogram import chat_actions

attachments = [
    'animation', 'document', 'location', 'contact',
    'sticker', 'voice', 'video', 'poll',
]

class Message(UpdateBase):
    name = 'message'
    handler = None
    adminHandler = None

    def __init__(self, update: Dict):
        self.logger = self.autogram.logger
        self.chat = update.pop('chat')
        self.id = update.pop('message_id')
        self.date = update.pop('date')
        self.sender = update.pop('from')
        self.attachments = update

        # log username
        self.logger.info(f"user: {self.sender['username']}")

        ## if no admin, and you're not admin, ignore
        if not self.autogram.admin:
            if self.sender['username'] != self.autogram.config['admin_username']:
                self.autogram.deleteMessage(
                    self.sender['id'],
                    self.id
                )
                self.autogram.sendMessage(
                    self.sender['id'],
                    'No attendants!'
                )
                return
            self.autogram.admin = self.sender['id']
            if handler:=Message.adminHandler:
                handler(self)
            return
        elif self.sender['id'] == self.autogram.admin or self.sender['id'] == self.autogram.deputy_admin:
            if self.sender['id'] == self.autogram.admin:
                if self.autogram.deputy_admin:
                    self.autogram.sendMessage(
                        self.autogram.admin,
                        'Deputy logged out.'
                    )
                self.autogram.deputy_admin = None
            if handler:=Message.adminHandler:
                handler(self)
            return
        elif not self.autogram.deputy_admin:
            if (text := self.attachments.get('text')):
                if text.strip() == self.autogram.config['contingency_pwd']:
                    self.autogram.deputy_admin = self.sender['id']
                    self.autogram.sendMessage(
                        self.sender['id'],
                        'Deputy, welcome!'
                    )
                    self.autogram.sendMessage(
                        self.autogram.admin,
                        'Deputy logged in!'
                    )
                    return
        if handler := Message.handler:
           handler(self)
        return


    def __repr__(self):
        return str(vars(self))

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

    @classmethod
    def addAdminHandler(cls, handler: Callable):
        cls.adminHandler = handler

    def getPhoto(self, handler: Callable) -> bool:
        if not hasattr(self,'photo'):
            return False
        # 
        file_id = self.photo[-1]['file_id']
        def getter(file_info: Dict):
            file_path = file_info['file_path']
            content = self.autogram.downloadFile(file_path)
            handler(content)
        self.autogram.getFile(file_id, getter)
        return True

    def replyText(self, text: str):
        self.autogram.sendChatAction(self.chat['id'], chat_actions.typing)
        self.autogram.sendMessage(self.chat['id'], text)


class editedMessage(UpdateBase):
    handler = None
    name = 'edited_message'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'editedMessage: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)
