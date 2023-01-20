from re import T
import loguru
from . import UpdateBase
from typing import Dict, Callable
from autogram import chat_actions


class Message(UpdateBase):
    name = 'message'
    media = ['audio','voice', 'video', 'photo', 'document', 'video_note']
    endpoints = {
        'command-endpoint': dict(),
        'user-endpoint': dict()
    }

    @classmethod
    def getCommands(cls, raw =True):
        """Get a list of commands or (command, callbackName) tuples"""
        if raw:
            return list(cls.endpoints['command-endpoint'])
        #
        out = list()
        for key in cls.endpoints['command-endpoint']:
            func = cls.endpoints['command-endpoint'][key]
            out.append((key.strip('/'), func))
        return out

    def __init__(self, update: Dict):
        self.logger = self.autogram.logger
        self.chat = update.pop('chat')
        self.id = update.pop('message_id')
        self.date = update.pop('date')
        self.sender = update.pop('from')
        self.attachments = update

        # parse entities
        endpoint = 'user-endpoint'
        if entities := update.get('entities'):
            text = None
            endpoint = 'command-endpoint'
            entities = update.pop('entities')
            #
            for entity in entities:
                typ = entity.get('type')
                if typ != 'bot_command':
                    return
                if text := self.attachments.get('text'):
                    setattr(self, 'text', text)
                    break
            #
            if not text:
                return
            #
            if handler := self.endpoints[endpoint].get(text):
                try:
                    handler(self)
                except Exception as e:
                    self.logger.exception(e)
            else:
                self.delete()
                self.autogram.sendMessage(
                    self.sender['id'],
                    'Unknown command'
                )
            return
        # dispatch callbacks
        for key in self.attachments.keys():
            if not self.endpoints[endpoint]:
                return
            if key in Message.media:
                self.handleMedia()
                break
            if handler := self.endpoints[endpoint].get(key):
                setattr(self, key, self.attachments.get(key))
                try:
                    handler(self)
                except Exception as e:
                    self.logger.exception(e)
            continue

    def __repr__(self):
        return f"Message({self.sender.get('username')}, {self.sender.get('id')})"

    @classmethod
    def onCommand(cls, command: str):
        command = f'/{command}'
        def wrapper(f : Callable):
            Message.endpoints['command-endpoint'] |= { command: f }
            return f
        return wrapper

    @classmethod
    def onMessageType(cls, typ: str):
        def wrapper(f : Callable):
            Message.endpoints['user-endpoint'] |= { typ: f }
            return f
        return wrapper

    def sendText(self, text: str, **kwargs):
        self.autogram.sendChatAction(self.sender['id'], chat_actions.typing)
        self.autogram.sendMessage(self.sender['id'], text, **kwargs)

    @loguru.logger.catch
    def textBack(self, text: str, **kwargs):
        self.autogram.sendChatAction(self.sender['id'], chat_actions.typing)
        kwargs |= {
            'reply_to_message_id' : self.id,
            'allow_sending_without_reply': "true"
        }
        self.autogram.sendMessage(self.sender['id'], text, **kwargs)

    def delete(self):
        self.autogram.deleteMessage(
            self.sender['id'],
            self.id
        )

    def handleMedia(self):
        index = self.autogram.mediaQuality()
        #
        for key in self.attachments.keys():
            if key not in Message.media:
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
                try:
                    handler(self)
                except Exception as e:
                    self.logger.exception(e)

