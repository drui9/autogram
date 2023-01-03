"""
@author: The Alchemist
@url: https://sp3rtah.github.io/sp3rtah
@license: MIT
"""
import os
import sys
import time
import json
import loguru
import asyncio
import aiohttp
import requests as _requests
from queue import Queue
from threading import Event
from typing import Dict, List
from contextlib import contextmanager
from typing import Callable
import threading

#
from . import *
from autogram.hooker import MyServer
from bottle import request, response, post, run


class Autogram:
    api_url = 'https://api.telegram.org/'

    def __init__(self, token: str):
        """
        class Autogram:
        """
        self.token = token
        self._initialize_()

    def _initialize_(self):
        self.timeout = aiohttp.ClientTimeout(4)
        self.base_url = f'{Autogram.api_url}bot{self.token}'
        # 
        self.routines = set()
        self.admin = None       # bot system admin
        self.groups = set()     # groups we're in
        self.channels = set()   # channels we're in
        # 
        self.port = 4004
        self.host = '0.0.0.0'
        self.webhook = None
        self.update_offset = 0
        self.requests = Queue()
        self.terminate = Event()
        # 
        self.setup_logger()

    def __repr__(self) -> str:
        return str(vars(self))

    @loguru.logger.catch
    def send_online(self, publicIP = '') -> threading.Thread:
        """Get this bot online in a separate daemon thread."""
        if publicIP:
            hookPath = self.token.split(":")[-1]
            @post(f'/{hookPath}')
            def hookHandler():
                self.updateRouter(request.json)
                response.content_type = 'application/json'
                return json.dumps({'ok': True})
            # 
            def runServer(server: MyServer):
                run(server=server, quiet=True)
            # 
            server = MyServer(host=self.host,port=self.port)
            svr_thread = threading.Thread(target=runServer,args=(server,))
            svr_thread.name = 'Bottle Server'
            svr_thread.daemon = True
            svr_thread.start()
            #
            self.webhook = f'{publicIP}/{hookPath}'
            self.logger.info(f'Webhook: {self.webhook}')
        # 
        def launch():
            try:
                if sys.platform != 'linux':
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                asyncio.run(self.main_loop())
            except KeyboardInterrupt:
                self.terminate.set()
                _pending = self.requests.unfinished_tasks
                if _pending:
                    self.logger.info(f'[autogram]: {_pending} update tasks...')
            except Exception:
                raise
        worker = threading.Thread(target=launch)
        worker.name = 'Autogram'
        worker.daemon = True
        worker.start()
        return worker

    def setup_logger(self):
        """prepare logger and log levels"""
        self.logger = loguru.logger

    def getMe(self, me: Dict):
        """receive and parse getMe request."""
        self.logger.info('*** connected... ***')
        for k,v in me.items():
            setattr(self, k, v)

    @loguru.logger.catch()
    def updateRouter(self, res: Dict|List):
        """receive and route updates"""
        def handle(update: Dict):
            parser = None
            # parse update
            if payload:=update.get(Message.name):
                parser = Message
            elif payload:=update.get(editedMessage.name):
                parser = editedMessage
            elif payload:=update.get(channelPost.name):
                parser = channelPost
            elif payload:=update.get(editedChannelPost.name):
                parser = editedChannelPost
            elif payload:=update.get(inlineQuery.name):
                parser = inlineQuery
            elif payload:=update.get(chosenInlineResult.name):
                parser = chosenInlineResult
            elif payload:=update.get(callbackQuery.name):
                parser = callbackQuery
            elif payload:=update.get(shippingQuery.name):
                parser = shippingQuery
            elif payload:=update.get(precheckoutQuery.name):
                parser = precheckoutQuery
            elif payload:=update.get(Poll.name):
                parser = Poll
            elif payload:=update.get(pollAnswer.name):
                parser = pollAnswer
            elif payload:= update.get(myChatMember.name):
                parser = myChatMember
            elif payload:=update.get(chatMember.name):
                parser = chatMember
            elif payload:= update.get(chatJoinRequest.name):
                parser = chatJoinRequest
            # 
            if not parser:
                return
            else:
                parser.autogram = self
                parse_thread = threading.Thread(target=parser,args=(payload,))
                parse_thread.daemon = True
                parse_thread.start()
        # 
        if type(res) == list:
            for update in res:
                if update['update_id'] >= self.update_offset:
                    self.update_offset = update['update_id'] + 1
                handle(update)
            return
        handle(res)

    async def main_loop(self):
        """Main control loop"""
        self.logger.debug('Main loop started...')
        self.routines.add(asyncio.create_task(self.aioWebRequest()))
        self.requests.put((f'{self.base_url}/getMe',None,self.getMe))
        if self.webhook:
            url = f'{self.base_url}/setWebhook'
            self.requests.put((url,{
                'params': {
                    'url': self.webhook
                }
            }, None))
        else:   # delete webhook
            def check_webhook(info: dict):
                if info['url']:
                    self.deleteWebhook()
            self.getWebhookInfo(check_webhook)
        await asyncio.sleep(0)  # wait for init to finish
        while not self.terminate.is_set():
            if not self.requests.empty():
                await asyncio.sleep(0)
                continue
            if not self.webhook:    ## use short polling
                params = {
                    'params': {
                        'offset': self.update_offset
                    }
                }
                url = f'{self.base_url}/getUpdates'
                self.requests.put((url,params,self.updateRouter))
            await asyncio.sleep(0)
        # 
        if not self.terminate.is_set():
            self.terminate.set()
            await asyncio.gather(*self.routines)
        self.logger.debug('Main loop terminated.')

    @loguru.logger.catch()
    @contextmanager
    def get_request(self):
        """fetch a new webrequest task from pending tasks"""
        if self.failed:
            self.logger.info('Fetching failed request...')
            yield self.failed
        elif self.requests.empty():
            yield None
        else:
            yield self.requests.get(block=False)

    @loguru.logger.catch()
    async def aioWebRequest(self):
        """Make asynchronous requests to the Telegram API"""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            max_fail_count = 12
            failed_requests = 0
            prev_count = 0
            self.failed = None

            while not self.terminate.is_set():
                if failed_requests > max_fail_count:
                    self.logger.critical(f'Too many failed requests: {failed_requests}. Shutting down...')
                    self.terminate.set()
                    break

                if failed_requests > prev_count:
                    prev_count = failed_requests
                    if failed_requests > 4:
                        self.timeout = aiohttp.ClientTimeout(failed_requests)
                    if self.requests.empty():
                        self.logger.debug(f'Last request failed. Retrying in {failed_requests}...')
                        await asyncio.sleep(failed_requests)
                    self.logger.debug(f'Retrying...')
                # 
                with self.get_request() as request:
                    if not request:
                        await asyncio.sleep(0)
                        continue
                    link, kw, callback = request
                    kw = kw or dict()
                    defaults = {
                        'params': {
                            "limit": 81,
                            "offset": self.update_offset,
                            "timeout": self.timeout.total - 1,
                        }
                    }
                    if not kw.get('params'):
                        kw.update(**defaults)
                    else:
                        kw['params'] |= defaults['params']
                    try:
                        self.logger.debug(f'get: {link.split("/")[-1]} [timeout]: {self.timeout.total}')
                        async with session.get(link,**kw) as resp:
                            if resp.ok:
                                data = await resp.json()
                                if callback:
                                    payload = data['result']
                                    if payload:
                                        callback(payload)
                                if failed_requests > 0:
                                   failed_requests -= 1
                                   self.failed = None
                            else:
                                self.logger.critical(f'{resp.status}: {await resp.json()}: {link}: {kw}: {callback}')
                                self.terminate.set()
                                break
                    except aiohttp.client_exceptions.ClientConnectorError as e:
                        self.logger.critical(f'[terminate]: {str(e)}')
                        self.terminate.set()
                        break
                    except asyncio.exceptions.TimeoutError as e:
                        failed_requests += 1
                        self.logger.critical(f'[fails: {failed_requests}]: timeout: {link.split("/")[-1]}')
                        self.failed = (link,kw,callback)
                    except KeyboardInterrupt:
                        self.terminate.set()
                    except Exception as e:
                        self.terminate.set()
                        self.logger.exception(e)
                    # 
                    if failed_requests == 0:
                        if self.requests.empty():
                            await asyncio.sleep(0)
                        self.timeout = aiohttp.ClientTimeout(4)
                        continue

    def webRequest(self, url: str, params={}, files=None):
        params = params or {}
        # send request
        if files:
            res = _requests.get(url,params=params,files=files)
        else:
            res = _requests.get(url,params=params)
        if not res.ok:
            return False, res, url
        return True, json.loads(res.text)['result']

    def sendChatAction(self, chat_id: int, action: str):
        params = {
            'chat_id': chat_id,
            'action': action
        }
        return self.webRequest(f'{self.base_url}/sendChatAction', params=params)

    def getFile(self, file_id: str, callback: Callable):
        url = f'{self.base_url}/getFile'
        self.requests.put((url,{
            'params': {
                'file_id': file_id
            }
        }, callback))

    def getChat(self, chat_id: int, handler: Callable):
        url = f'{self.base_url}/getChat'
        self.requests.put((url, {
            'params': {
                'chat_id': chat_id
            }
        }, handler))

    def getWebhookInfo(self, handler: Callable):
        url = f'{self.base_url}/getWebhookInfo'
        self.requests.put((url,None,handler))

    @loguru.logger.catch()
    def downloadFile(self, file_path: str):
        url = f'https://api.telegram.org/file/bot{self.token}/{file_path}'
        res = _requests.get(url)
        if res.ok:
            return res.content
        else:
            self.logger.critical(f'file: [{file_path} -> Download failed: {res.status_code}')

    @loguru.logger.catch()
    def sendMessage(self, chat_id: int, text: str, params={}):
        url = f'{self.base_url}/sendMessage'
        self.requests.put((url, {
            'params': {
                'chat_id': chat_id,
                'text': text
            }|params
        }, None))

    @loguru.logger.catch()
    def forwardMessage(self, chat_id: int, from_chat_id: int, msg_id: int):
        url = f'{self.base_url}/sendMessage'
        self.requests.put((url,{
            'params': {
                'chat_id': chat_id,
                'from_chat_id': from_chat_id,
                'message_id': msg_id
            }
        },None))

    @loguru.logger.catch()
    def editMessageText(self, chat_id: int, msg_id: int, text: str, params={}):
        url = f'{self.base_url}/editMessageText'
        self.requests.put((url,{
            'params': {
                'text':text,
                'chat_id': chat_id,
                'message_id': msg_id
            }|params
        },None))

    @loguru.logger.catch()
    def editMessageCaption(self, chat_id: int, msg_id: int, capt: str, params={}):
        url = f'{self.base_url}/editMessageCaption'
        self.requests.put((url, {
            'params': {
                'chat_id': chat_id,
                'message_id': msg_id,
                'caption': capt
            }|params
        }, None))

    @loguru.logger.catch()
    def editMessageReplyMarkup(self, chat_id: int, msg_id: int, markup: str, params={}):
        url = f'{self.base_url}/editMessageReplyMarkup'
        self.requests.put((url,{
            'params': {
                'chat_id':chat_id,
                'message_id':msg_id,
                'reply_markup': markup
            }|params
        }, None))

    @loguru.logger.catch()
    def deleteMessage(self, chat_id: int, msg_id: int):
        url = f'{self.base_url}/deleteMessage'
        self.requests.put((url,{
            'params': {
                'chat_id': chat_id,
                'message_id': msg_id
            }
        }, None))

    def deleteWebhook(self):
        url = f'{self.base_url}/deleteWebhook'
        return self.webRequest(url)

    def answerCallbackQuery(self, query_id,text:str= None, params : dict= None):
        url = f'{self.base_url}/answerCallbackQuery'
        params.update({
            'callback_query_id':query_id,
            'text':text
        })
        return self.webRequest(url, params)

    def sendPhoto(self,chat_id: int, photo_bytes: bytes, caption: str= None, params: dict= None):
        params = params or {}
        url = f'{self.base_url}/sendPhoto'
        params.update({
            'chat_id':chat_id,
            'caption': caption,
        })
        self.sendChatAction(chat_id,chat_actions.photo)
        return self.webRequest(url,params=params,files={'photo':photo_bytes})

    def sendAudio(self,chat_id: int,audio_bytes: bytes, caption: str= None, params: dict= None):
        params = params or {}
        url = f'{self.base_url}/sendAudio'
        params.update({
            'chat_id':chat_id,
            'caption': caption
        })
        self.sendChatAction(chat_id,chat_actions.audio)
        return self.webRequest(url,params,files={'audio':audio_bytes})

    def sendDocument(self,chat_id: int ,document_bytes: bytes, caption: str= None, params: dict= None):
        params = params or {}
        url = f'{self.base_url}/sendDocument'
        params.update({
            'chat_id':chat_id,
            'caption':caption
        })
        self.sendChatAction(chat_id,chat_actions.document)
        return self.webRequest(url,params,files={'document':document_bytes})

    def sendVideo(self,chat_id: int ,video_bytes: bytes, caption: str = None, params: dict= None ):
        params = params or {}
        url = f'{self.base_url}/sendVideo'
        params.update({
            'chat_id':chat_id,
            'caption':caption
        })
        self.sendChatAction(chat_id,chat_actions.video)
        return self.webRequest(url,params,files={'video':video_bytes})

    def forceReply(self, params: dict= None):
        params = params or {}
        markup = {
            'force_reply': True,
        }|params
        return json.dumps(markup)

    def getKeyboardMarkup(self, keys: list, params: dict= None):
        params = params or {}
        markup = {
            "keyboard":[row for row in keys]
        }|params
        return json.dumps(markup)

    def getInlineKeyboardMarkup(self, keys: list, params: dict= None):
        params = params or {}
        markup = {
            'inline_keyboard':keys
        }|params
        return json.dumps(markup)

    def parseFilters(self, filters: dict= None):
        keys = list(filters.keys())
        return json.dumps(keys)

    def removeKeyboard(self, params: dict= None):
        params = params or {}
        markup = {
            'remove_keyboard': True,
        }|params
        return json.dumps(markup)
