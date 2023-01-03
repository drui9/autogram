from . import UpdateBase
from typing import Dict, Callable
from autogram import chat_actions

attachments = [
    'animation',
    'document',
    'location',
    'contact',
    'sticker',
    'voice',
    'video',
    'poll',
]


class Message(UpdateBase):
    handler = None
    name = 'message'

    def __init__(self, update: Dict):
        print(update)
        self.id = update.pop('message_id')
        self.date = update.pop('date')
        self.chat = update.pop('chat')
        self.sender = update.pop('from')
        self.attachments = update
        #
        if handler:=Message.handler:
            handler(self)
    
    def __repr__(self):
        return str(vars(self))

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)

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

    def forward(self):
        pass


class editedMessage(UpdateBase):
    handler = None
    name = 'edited_message'
    
    def __init__(self, update: Dict):
        print(update)

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)
