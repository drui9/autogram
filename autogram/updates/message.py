from . import UpdateBase
from typing import Dict, Callable
from autogram import chat_actions
from threading import Lock

attachments = [
    'animation', 'document', 'location', 'contact',
    'sticker', 'voice', 'video', 'poll',
]

class Message(UpdateBase):
    name = 'message'
    handler = None
    endpoints = {
        'admin': dict(),
        'users': dict()
    }

    def __init__(self, update: Dict):
        self.logger = self.autogram.logger
        self.chat = update.pop('chat')
        self.id = update.pop('message_id')
        self.date = update.pop('date')
        self.sender = update.pop('from')
        self.attachments = update

        # log username
        self.logger.info(f"{self.sender['username']}: {list(self.attachments.keys())}")

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
            for key in self.attachments.keys():
                if handler := self.endpoints['admin'].get(key):
                    setattr(self, key, self.attachments.get(key))
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
            for key in self.attachments.keys():
                if handler := self.endpoints['admin'].get(key):
                    setattr(self, key, self.attachments.get(key))
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
        ## parse guest msg content
        for key in self.attachments.keys():
            if handler := self.endpoints['users'].get(key):
                setattr(self, key, self.attachments.get(key))
                handler(self)
        return

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def onCommandType(cls, typ: str):
        def wrapper(f):
            Message.endpoints['admin'] |= { typ: f }
            return f
        return wrapper

    @classmethod
    def onMessageType(cls, typ: str):
        def wrapper(f):
            Message.endpoints['users'] |= { typ: f }
            return f
        return wrapper

    def getAudio(self) -> bool:
        """getAudio"""
        if not hasattr(self,'audio'):
            return None
        print(self.audio)
        # lock file_path resource
        resource = {
            'lock': None,
            'file_path': None
        }
        def getter(file_info: Dict):
            resource['file_path'] = file_info['file_path']
            resource['lock'].release()

        file_id = self.audio['file_id']
        self.autogram.getFile(file_id, getter)
        with (lock := Lock()):
            resource['lock'] = lock
            lock.acquire()
            file_name = resource['file_path'].split('/')[-1]
            return {
                'name': file_name,
                'id': self.audio['file_id'],
                'size': self.audio['file_size'],
                'duration': self.audio['duration'],
                'mime_type': self.audio['mime_type'],
                'content': self.autogram.downloadFile(resource['file_path'])
            }

    def getVideo(self, thumbnail: bool = False) -> bool:
        """getVideo"""
        if not hasattr(self,'video'):
            return None
        # lock file_path resource
        resource = {
            'lock': None,
            'file_path': None
        }
        def getter(file_info: Dict):
            resource['file_path'] = file_info['file_path']
            resource['lock'].release()

        file_id = self.video['file_id']
        self.autogram.getFile(file_id, getter)
        with (lock := Lock()):
            resource['lock'] = lock
            lock.acquire()
            file_name = resource['file_path'].split('/')[-1]
            return {
                'name': file_name,
                'id': self.video['file_id'],
                'width': self.video['width'],
                'height': self.video['height'],
                'size': self.video['file_size'],
                'duration': self.video['duration'],
                'mime_type': self.video['mime_type'],
                'content': self.autogram.downloadFile(resource['file_path'])
            }

    def getPhoto(self, quality: str='high') -> bool:
        """getPhoto of quality [low, medium, high]"""
        if not hasattr(self,'photo'):
            return None
        photo = self.photo.copy()
        self.photo = dict()
        for idx, item in enumerate(photo):
            self.photo |= { idx : item }
        # select download quality
        level = 2
        if quality == 'low':
            level = 0
        elif quality == 'medium':
            level = 1

        # lock file_path resource
        resource = {
            'lock': None,
            'file_path': None
        }
        def getter(file_info: Dict):
            resource['file_path'] = file_info['file_path']
            resource['lock'].release()

        file_id = self.photo[level]['file_id']
        self.autogram.getFile(file_id, getter)
        with (lock := Lock()):
            resource['lock'] = lock
            lock.acquire()
            file_name = resource['file_path'].split('/')[-1]
            return {
                'name': file_name,
                'id': self.photo[level]['file_id'],
                'width': self.photo[level]['width'],
                'height': self.photo[level]['height'],
                'size': self.photo[level]['file_size'],
                'content': self.autogram.downloadFile(resource['file_path'])
            }
    def getFile(self, typ: str, params: dict):
        """getFile information & bytes"""
        if not hasattr(self, typ):
            return None

    def toAdmin(self):
        if self.sender['id'] == self.autogram.admin:
            return
        self.autogram.forwardMessage(
            self.autogram.admin,
            self.sender['id'],
            self.id
        )

    def sendText(self, text: str):
        self.autogram.sendChatAction(self.sender['id'], chat_actions.typing)
        self.autogram.sendMessage(self.sender['id'], text)

    def replyText(self, text: str):
        self.autogram.sendChatAction(self.sender['id'], chat_actions.typing)
        self.autogram.sendMessage(self.sender['id'], text, params={
            'reply_to_message_id' : self.id
        })

class editedMessage(UpdateBase):
    handler = None
    name = 'edited_message'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'editedMessage: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)
