from . import UpdateBase
from typing import Dict, Callable
from autogram import chat_actions
from threading import Lock


class Message(UpdateBase):
    name = 'message'
    handler = None
    media = ['audio','voice', 'video', 'photo', 'document', 'video_note']
    endpoints = {
        'command-endpoint': dict(),
        'user-endpoint': dict()
    }

    def __init__(self, update: Dict):
        self.logger = self.autogram.logger
        self.chat = update.pop('chat')
        self.id = update.pop('message_id')
        self.date = update.pop('date')
        self.sender = update.pop('from')
        self.attachments = update

        # check admin
        if not self.autogram.admin:
            if self.autogram.config['admin_username'] == self.sender['username']:
                self.autogram.admin = self.sender['id']

        # dry function
        def parambulate():
            """disparch msg elements to their callback functions"""
            endpoint = 'user-endpoint'

            # parse entities
            if ( entities := update.get('entities') ):
                text = None
                endpoint = 'command-endpoint'
                entities = update.pop('entities')

                for entity in entities:
                    text = self.attachments.get('text')
                    if text:
                        break

                if not text:
                    self.toAdmin()
                    return

                if (uid := self.sender['id']) != self.autogram.admin:
                    if uid != self.autogram.deputy_admin:
                       if text != '/start':
                            self.deleteMessage()
                            return

                if handler := self.endpoints[endpoint].get(text):
                    handler(self)
                else:
                    self.deleteMessage()
                    self.autogram.sendMessage(
                        self.sender['id'],
                        'Unknown command'
                    )
                return

            # dispatch callbacks
            hit = False
            for key in self.attachments.keys():
                if not self.endpoints[endpoint]:
                    self.toAdmin()
                    return
                if key in Message.media:
                    break
                if handler := self.endpoints[endpoint].get(key):
                    setattr(self, key, self.attachments.get(key))
                    handler(self)
                    hit = True

            # forward to admin -> default action
            if not hit:
                self.toAdmin()
                return

        ## if no admin, and you're not admin, ignore
        if not self.autogram.admin:
            self.deleteMessage()
            self.autogram.sendMessage(
                self.sender['id'],
                'No attendants!'
            )
            return
        elif self.sender['id'] == self.autogram.admin or self.sender['id'] == self.autogram.deputy_admin:
            if self.sender['id'] == self.autogram.admin:
                if self.autogram.deputy_admin:
                    self.autogram.sendMessage(
                        self.autogram.admin,
                        "You're back! Letting deputy out."
                    )
                    self.autogram.sendMessage(
                        self.autogram.deputy_admin,
                        "You've been logged out."
                    )
                self.autogram.deputy_admin = None
            parambulate()
            return
        elif not self.autogram.deputy_admin:
            if (text := self.attachments.get('text')):
                if text.strip() == self.autogram.config['contingency_pwd']:
                    self.autogram.deputy_admin = self.sender['id']
                    self.deleteMessage()
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
        parambulate()
        return

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def onCommand(cls, command: str):
        def wrapper(f):
            Message.endpoints['command-endpoint'] |= { command: f }
            return f
        return wrapper

    @classmethod
    def onMessageType(cls, typ: str):
        def wrapper(f):
            Message.endpoints['user-endpoint'] |= { typ: f }
            return f
        return wrapper

    def toAdmin(self):
        if self.sender['id'] == self.autogram.admin:
            self.handleMedia()
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
            'reply_to_message_id' : self.id,
            'allow_sending_without_reply': "true"
        })

    def deleteMessage(self):
        self.autogram.deleteMessage(
            self.chat['id'],
            self.id
        )

    def handleMedia(self):
        index = 2
        if (quality := self.autogram.media_quality) == 'medium':
            index = 1
        elif quality == 'low':
            index = 0

        media = Message.media
        for key in self.attachments.keys():
            if key not in media:
                self.logger.debug(f"unknown media: {key}")
                continue
            item = self.attachments[key]
            if type(item) == list:
                item = item[index]
            file_id = item['file_id']
            success, file_info = self.autogram.getFile(file_id)
            if not success:
                self.logger.exception(file_info)
                return
            file_path = file_info['file_path']
            content = self.autogram.downloadFile(
                file_path
            )
            self.file = {
                'name': file_path.split('/')[-1],
                'bytes': content
            }|file_info
            if handler := self.endpoints['user-endpoint'].get(key):
                handler(self)

class editedMessage(UpdateBase):
    handler = None
    name = 'edited_message'

    def __init__(self, update: Dict):
        self.autogram.logger.debug(f'editedMessage: {update}')

    @classmethod
    def addHandler(cls, handler: Callable):
        cls.handler = handler
        cls.subscribed_updates.add(cls.name)
