import re
import json
import requests
from typing import Any
from loguru import logger
from . import chat_actions
from threading import Lock
from requests.models import Response
from autogram.config import save_config

# --
class Bot():
  endpoint = 'https://api.telegram.org/'
  register = {
    'lock': Lock(),
    'handlers': dict()
  }
  #--
  @classmethod
  def add(cls, name: str):
    def wrapper(fn):
      with cls.register['lock']:
        cls.register['handlers'] |= {name : fn}
      return fn
    return wrapper
  #--
  def __init__(self, config :dict) -> None:
    self.requests = requests.session()
    self.config = config or self.do_err(msg='Please pass a config <object :Dict>!')
    if not self.config.get("telegram-token"):
      self.do_err(msg='Missing bot token!')

  def do_err(self, msg :str, err_type =RuntimeError):
    """Utility: Raise error"""
    logger.critical(msg)
    raise err_type(msg)

  def data(self, key :str, val :Any|None=None):
    """Persistent data storage"""
    if 'data' not in self.config:
      self.config['data'] = dict()
    if val != None:
      self.config['data'].update({key:val})
      return save_config(self.config)
    elif (ret := self.config['data'].get(key)) == None:
      self.do_err(f'Key[{key}] not in store!', err_type=KeyError)
    return ret

  def settings(self, key :str, val: Any|None=None, save=False):
    """Get or set value of key in config"""
    if val != None:
      self.config.update({key: val})
      return save_config(self.config)
    elif (ret := self.config.get(key)) == None:
      self.do_err(msg=f'Missing key in config: {key}', err_type=KeyError)
    return ret

  def setWebhook(self, hook_addr : str):
    if not re.search('^(https?):\\/\\/[^\\s/$.?#].[^\\s]*$', hook_addr):
      raise RuntimeError('Invalid webhook url. format <https://...>')
    #--
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/setWebhook'
    params = {
      'url': hook_addr
    }
    return self.requests.get(url, params=params)

  def poll(self, offset=0, limit=10, timeout=7):
    """Poll updates"""
    with self.register['lock']:
      data = {
        'timeout': timeout,
        'params': {
          'allowed_updates': json.dumps(list(self.register['handlers'].keys())),
          'timeout': timeout // 2,
          'offset': offset,
          'limit': limit,
        }
      }
    return self.getUpdates(**data)

  def getMe(self) -> Response:
    """Fetch `bot` information"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/getMe'
    return self.requests.get(url)

  def getUpdates(self, **kwargs) -> Response:
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/getUpdates'
    return self.requests.get(url, **kwargs)

  def downloadFile(self, file_path: str) -> Response:
    """Downloads a file with file_path got from getFile(...)"""
    url = f'https://api.telegram.org/file/bot{self.settings("telegram-token")}/{file_path}'
    return self.requests.get(url)

  def getFile(self, file_id: str) -> Response:
    """Gets details of file with file_id"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/getFile'
    return self.requests.get(url, params={'file_id': file_id})

  def getChat(self, chat_id: int) -> Response:
    """Gets information on chat_id"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/getChat'
    return self.requests.get(url, params={'chat_id': chat_id})

  def getWebhookInfo(self) -> Response:
    """Gets information on currently set webhook"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/getWebhookInfo'
    return self.requests.get(url)

  def sendChatAction(self, chat_id: int, action: str) -> Response:
    """Sends `action` to chat_id"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/sendChatAction'
    params = {
      'chat_id': chat_id,
      'action': action
    }
    return self.requests.get(url, params=params)

  def sendMessage(self, chat_id :int|str, text :str, **kwargs) -> Response:
    """Sends `text` to `chat_id`"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/sendMessage'
    params = {
    'params': {
      'chat_id': chat_id,
      'text': text,
    } | kwargs
    }
    return self.requests.get(url, **params)

  def deleteMessage(self, chat_id: int, msg_id: int) -> Response:
    """Deletes message sent <24hrs ago"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/deleteMessage'
    params= {
      'chat_id': chat_id,
      'message_id': msg_id
    }
    return self.requests.get(url, params=params)

  def deleteWebhook(self, drop_pending = False) -> Response:
    """Deletes webhook value"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/deleteWebhook'
    return self.requests.get(url, params={'drop_pending_updates': drop_pending})

  def editMessageText(self, chat_id: int, msg_id: int, text: str, **kwargs) -> Response:
    """Edit message sent <24hrs ago"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/editMessageText'
    params = {
      'params': {
        'text':text,
        'chat_id': chat_id,
        'message_id': msg_id
      } | kwargs
    }
    return self.requests.get(url, **params)

  def editMessageCaption(self, chat_id: int, msg_id: int, capt: str, params={}) -> Response:  # noqa: E501
    """Edit message caption"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/editMessageCaption'
    params = {
      'params': {
      'chat_id': chat_id,
      'message_id': msg_id,
      'caption': capt
      }|params
    }
    return self.requests.get(url, **params)

  def editMessageReplyMarkup(self, chat_id: int, msg_id: int, markup: str, params={}) -> Response:  # noqa: E501
    """Edit reply markup"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/editMessageReplyMarkup'
    params = {
    'params': {
      'chat_id':chat_id,
      'message_id':msg_id,
      'reply_markup': markup
    }|params
    }
    return self.requests.get(url, **params)

  def forwardMessage(self, chat_id: int, from_chat_id: int, msg_id: int) -> Response:
    """Forward message with message_id from from_chat_id to chat_id"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/forwardMessage'
    params = {
    'params': {
      'chat_id': chat_id,
      'from_chat_id': from_chat_id,
      'message_id': msg_id
    }
    }
    return self.requests.get(url, **params)

  def answerCallbackQuery(self, query_id, text :str|None =None, params : dict|None =None) -> Response:  # noqa: E501
    """Answers callback queries with text: str of len(text) < 200"""
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/answerCallbackQuery'
    params = params or {}
    text = text or 'Updated!'
    params.update({
    'callback_query_id':query_id,
    'text': text[:200]
    })
    return self.requests.get(url, params=params)

  def sendPhoto(self,chat_id: int, photo_bytes: bytes, caption: str|None = None, params: dict|None = None) -> Response:  # noqa: E501
    """Sends a photo to a telegram user"""
    params = params or {}
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/sendPhoto'
    params.update({
      'chat_id':chat_id,
      'caption': caption,
    })
    self.sendChatAction(chat_id, chat_actions.photo)
    return self.requests.get(url, params=params, files={'photo': photo_bytes})

  def sendAudio(self,chat_id: int,audio :bytes|str, caption: str|None = None, params: dict|None = None) -> Response:  # noqa: E501
    """Sends an audio to a telegram user"""
    params = params or {}
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/sendAudio'
    params |= {
      'chat_id':chat_id,
      'caption': caption
    }
    self.sendChatAction(chat_id, chat_actions.audio)
    if isinstance(audio, bytes):
      return self.requests.get(url, params=params, files={'audio': audio})
    params.update({'audio': audio})
    return self.requests.get(url, params=params)

  def sendDocument(self,chat_id: int ,document_bytes: bytes, caption: str|None = None, params: dict|None = None) -> Response:  # noqa: E501
    """Sends a document to a telegram user"""
    params = params or {}
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/sendDocument'
    params.update({
      'chat_id':chat_id,
      'caption':caption
    })
    self.sendChatAction(chat_id, chat_actions.document)
    self.requests.get(url, params=params, files={'document': document_bytes})

  def sendVideo(self,chat_id: int ,video_bytes: bytes, caption: str|None = None, params: dict|None = None ) -> Response:  # noqa: E501
    """Sends a video to a telegram user"""
    params = params or {}
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/sendVideo'
    params.update({
      'chat_id':chat_id,
      'caption':caption
    })
    self.sendChatAction(chat_id, chat_actions.video)
    return self.requests.get(url, params=params,files={'video':video_bytes})

  def forceReply(self, params: dict|None = None) -> str:
    """Returns forceReply value as string"""
    params = params or {}
    markup = {
      'force_reply': True,
    }|params
    return json.dumps(markup)

  def getKeyboardMarkup(self, keys: list, params: dict|None =None) -> str:
    """Returns keyboard markup as string"""
    params = params or {}
    markup = {
      "keyboard":[row for row in keys]
    } | params
    return json.dumps(markup)

  def getInlineKeyboardMarkup(self, keys: list, params: dict|None =None) -> str:
    params = params or {}
    markup = {
      'inline_keyboard':keys
    }|params
    return json.dumps(markup)

  def parseFilters(self, filters: dict|None =None) -> str:
    filters = filters or {}
    return json.dumps(filters.keys())

  def removeKeyboard(self, params: dict|None =None) -> str:
    params = params or {}
    markup = {
      'remove_keyboard': True,
    }|params
    return json.dumps(markup)
