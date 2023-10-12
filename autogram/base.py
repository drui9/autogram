import os
import re
import time
import json
import loguru
import threading
import requests
from typing import Any
from queue import Queue
from requests.models import Response
from autogram.webserver import WebServer
from bottle import request, response, post, run, get
from autogram.config import save_config
from . import chat_actions


class Bot():
  endpoint = 'https://api.telegram.org/'

  def __init__(self, config :dict) -> None:
    """Initialize parent database object"""
    super().__init__()
    self.updates = Queue()
    self.logger = loguru.logger
    self.terminate = threading.Event()
    self.requests = requests.session()
    self.config = config or self.do_err(msg='Please pass a config <object :Dict>!')
    if not self.config.get("telegram-token"):
      self.config.update({
          "telegram-token" : os.getenv('AUTOGRAM_TG_TOKEN') or self.do_err(msg='Missing bot token!') # noqa: E501
        })

  def do_err(self, err_type =RuntimeError, msg ='Error!'):
    """Clean terminate the program on errors."""
    self.terminate.set()
    raise err_type(msg)

  def settings(self, key :str, val: Any|None=None):
    """Get or set value of key in config"""
    if val:
       self.config.update({key: val})
       save_config(self.config)
       return val
    elif not (ret := self.config.get(key)):
      self.do_err(msg=f'Missing key in config: {key}')
    return ret

  def media_quality(self):
    """Get preffered media quality."""
    if (quality := self.settings("media-quality").lower() or 'low') == 'low':
      return 0
    elif quality == 'high':
      return 2
    return 1

  def setWebhook(self, hook_addr : str):
    if not re.search('^(https?):\\/\\/[^\\s/$.?#].[^\\s]*$', hook_addr):
      raise RuntimeError('Invalid webhook url. format <https://...>')
    # ensure hook_addr stays reachable
    @get('/')
    def ping():
      return json.dumps({'ok': True})
    # keep-alive service
    def keep_alive():
      self.logger.info('Keep-alive started.')
      while not self.terminate.is_set():
        try:
          res = self.requests.get(hook_addr)
          if not res.ok:
            raise RuntimeError(f'Webhook {hook_addr} unreachable: {res.status_code}')
        except Exception as e:
          self.logger.exception(e)
        time.sleep(10)
    # start keep-alive
    alive_guard = threading.Thread(target=keep_alive)
    alive_guard.name = 'Autogram:Keep-alive'
    alive_guard.daemon = True
    alive_guard.start()
    # receive updates
    @post('/')
    def hookHandler():
      response.content_type = 'application/json'
      self.updates.put(request.json)
      return json.dumps({'ok': True})
    #
    def runServer(server: Any):
      return run(server=server, quiet=True)
    #
    server = WebServer(host="0.0.0.0", port=self.settings('lport'))
    serv_thread = threading.Thread(target=runServer, args=(server,))
    serv_thread.name = 'Autogram:Bottle'
    serv_thread.daemon = True
    serv_thread.start()
    # inform telegram
    url = f'{self.endpoint}bot{self.settings("telegram-token")}/setWebhook'
    params = {
      'url': hook_addr
    }
    return self.requests.get(url, params=params)

  def short_poll(self):
    """Start fetching updates in seperate thread"""
    def getter():
      failed = False
      offset = 0
      while not self.terminate.is_set():
        try:
          data = {
            'timeout': 3,
            'params': {
              'offset': offset,
              'limit': 10,
              'timeout': 1
            }
          }
          res = self.getUpdates(**data)
        except Exception:
          time.sleep(2)
          continue
        #
        if not res.ok:
          if not failed:
            time.sleep(2)
            failed = True
          else:
            self.terminate.set()
        else:
          updates = res.json()['result']
          for update in updates:
            offset = update['update_id'] + 1
            self.updates.put(update)
          # rate-limit
          poll_interval = 2
          time.sleep(poll_interval)
      return
    poll = threading.Thread(target=getter)
    poll.name = 'Autogram:short_polling'
    poll.daemon = True
    poll.start()

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
