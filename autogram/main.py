import sys
import json
import loguru
import asyncio
import aiohttp
import requests
import threading
from typing import Callable
from typing import Dict, Any
from queue import Queue, Empty
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
#
from autogram import *
from autogram.webhook import MyServer
from bottle import request, response, post, run


class Autogram:
    api_url = 'https://api.telegram.org/'

    def __init__(self, config: Dict):
        self.config = config
        self._initialize_()

    def _initialize_(self):
        self.webhook = None
        self.host = '0.0.0.0'
        self.update_offset = 0
        self.httpRoutines = list()
        self.httpRequests = Queue()
        self.workerThreads = list()
        self.terminate = threading.Event()
        self.executor = ThreadPoolExecutor()
        self.port = self.config['tcp-port']
        self.timeout = aiohttp.ClientTimeout(self.config['tcp-timeout'])
        self.base_url = f"{Autogram.api_url}bot{self.config['telegram-token']}"
        # 
        logger_format = (
            "<green>{time:DD/MM/YYYY HH:mm:ss}</green> | "
            "<level>{level: <8}</level>|"
            "<cyan>{line}</cyan>:<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
            "<level>{message}</level>"
        )
        loguru.logger.remove()
        #
        lvl = 'DEBUG'
        if env := self.config.get('env'):
            if env == 1:
                lvl = self.config.get('log-level') or 'DEBUG'
        #
        loguru.logger.add(sys.stderr, format=logger_format, level=lvl)
        self.logger = loguru.logger

    def mediaQuality(self):
        if (qlty := self.config.get("media-quality") or 'high') == 'high':
            return 2
        elif qlty == 'medium':
            return 1
        return 0

    @loguru.logger.catch
    def send_online(self) -> threading.Thread:
        """Get this bot online in a separate daemon thread."""
        if self.config['tcp-ip']:
            hookPath = self.config['telegram-token'].split(":")[-1].lower()
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
            serv_thread = threading.Thread(target=runServer, args=(server,))
            serv_thread.name = 'Autogram::Bottle'
            serv_thread.daemon = True
            serv_thread.start()
            #
            self.webhook = f"{self.config['tcp-ip']}/{hookPath}"
            self.logger.debug(f'Webhook: {self.webhook}')
        # wrap and start main_loop
        def launch():
            try:
                if sys.platform != 'linux':
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                asyncio.run(self.main_loop())
            except KeyboardInterrupt:
                self.terminate.set()
            except Exception as e:
                loguru.logger.exception(e)
        #
        worker = threading.Thread(target=launch)
        worker.name = 'Autogram'
        worker.daemon = True
        worker.start()
        return worker

    async def main_loop(self):
        """Main control loop"""
        processor = asyncio.create_task(self.aioWebRequest())
        self.httpRequests.put((f'{self.base_url}/getMe',None,self.getMe))
        if self.webhook:
            url = f'{self.base_url}/setWebhook'
            self.httpRequests.put((url,{
                'params': {
                    'url': self.webhook
                }
            }, None))
        else:   # delete webhook
            def check_webhook(info: dict):
                if info['url']:
                    self.deleteWebhook()
            self.getWebhookInfo(check_webhook)
        #
        await asyncio.sleep(0)    # allow getMe to run
        await processor
        #
        self.terminate.set()
        self.logger.info('Autogram terminated.')

    @loguru.logger.catch
    def updateRouter(self, res: Any):
        """receive and route updates"""
        def handle(update: Dict):
            parser = None
            # parse update
            if payload:=update.get(Message.name):
                if payload['chat']['type'] == 'private':
                    parser = Message
                else:
                    parser = Notification
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
            # todo: implement all update types then allow through
            if parser.name != 'message':
                self.logger.critical(f"Unimplemented: {parser.name}")
                return
            #
            parser.autogram = self
            # todo: call in separate thread
            worker = self.executor.submit(parser, payload)
            self.workerThreads.append(worker)
        # 
        if type(res) == list:
            for update in res:
                if update['update_id'] >= self.update_offset:
                    self.update_offset = update['update_id'] + 1
                handle(update)
            return
        handle(res)
        return

    def toThread(self, *args):
        if self.terminate.is_set():
            return
        #
        to_remove = list()
        for thread in self.workerThreads:
            if not thread.done():
                continue
            try:
                thread.exception()
            except Exception as e:
                self.logger.exception(e)
            to_remove.append(thread)
        #
        for item in to_remove:
            self.workerThreads.remove(item)
        self.workerThreads.append(self.executor.submit(*args))

    @contextmanager
    def get_request(self):
        """fetch pending or failed task from tasks"""
        if self.failed:
            self.logger.info('Retrying failed request...')
            yield self.failed
            return
        elif self.webhook:
            if not self.terminate.is_set():
                if self.httpRequests.empty():
                    try:
                        yield self.httpRequests.get(timeout=3)
                    except Empty as e:
                        yield None
                    except Exception as e:
                        self.logger.exception(e)
                        self.terminate.set()
                        yield None
                else:
                    yield self.httpRequests.get(block=False)
            else:
                yield None
            return
        if not self.httpRequests.empty():
            yield self.httpRequests.get(block=False)
            return
        yield None

    @loguru.logger.catch()
    async def aioWebRequest(self):
        """Make asynchronous requests to the Telegram API"""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            self.failed = None
            #
            @loguru.logger.catch
            async def httpHandler():
                while not self.terminate.is_set():
                    if not self.httpRoutines:
                        await asyncio.sleep(0)
                        continue
                    #
                    for item in self.httpRoutines:
                        incoming, outgoing = item
                        #
                        resp, payload = incoming
                        _, _, callback = outgoing
                        if resp.ok:
                            self.httpRoutines.remove(item)
                            #
                            if payload and callback:
                                thread_worker = self.executor.submit(callback, payload)
                                self.workerThreads.append(thread_worker)
                        else:
                            self.logger.critical(f"HTTPError {resp.status} : ({link.split('/')[-1]})")
            #
            # start httpHandler
            asyncio.create_task(httpHandler())
            while not self.terminate.is_set():
                with self.get_request() as request:
                    if not request:
                        ## no webhook? convert to getJob task
                        if not self.webhook:
                            params = {
                                'params': {
                                    'offset': self.update_offset
                                }
                            }
                            url = f'{self.base_url}/getUpdates'
                            request = (url,params,self.updateRouter)
                        else:
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
                    ##
                    try:
                        error_detected = None
                        self.logger.debug(f'get: {link.split("/")[-1]}')
                        async with session.get(link,**kw) as resp:
                            data = None
                            if resp.ok:
                                data = await resp.json()
                            self.httpRoutines.append(((resp, data), request))
                    except KeyboardInterrupt:
                        self.terminate.set()
                    except aiohttp.client_exceptions.ClientConnectorError as e:
                        error_detected = e
                    except aiohttp.client_exceptions.ClientOSError as e:
                        error_detected = e
                    except asyncio.exceptions.TimeoutError as e:
                        error_detected = e
                    except Exception as e:
                        error_detected = e
                    finally:
                        if error_detected:
                            self.failed = (link,kw,callback)
                            self.logger.exception(error_detected)
                #
                await asyncio.sleep(0)

    @loguru.logger.catch()
    def webRequest(self, url: str, params={}, files=None):
        params = params or {}
        # send request
        try:
            if files:
                res = requests.get(url,params=params,files=files)
            else:
                res = requests.get(url,params=params)
        except Exception as e:
            self.logger.exception(e)
        finally:
            if res.ok:
                return True, json.loads(res.text)['result']
        #
        return False, res, url

    def shutdown(self):
        self.terminate.set()
        self.executor.shutdown()

    #***** start API calls *****#
    def getMe(self, me: Dict):
        """receive and parse getMe request."""
        self.logger.info('*** connected... ***')
        for k,v in me.items():
            setattr(self, k, v)

    @loguru.logger.catch()
    def downloadFile(self, file_path: str):
        url = f"https://api.telegram.org/file/bot{self.config['telegram-token']}/{file_path}"
        res = requests.get(url)
        if res.ok:
            return res.content
        else:
            self.logger.critical(f'file: [{file_path} -> Download failed: {res.status_code}')

    def sendChatAction(self, chat_id: int, action: str):
        params = {
            'chat_id': chat_id,
            'action': action
        }
        return self.webRequest(f'{self.base_url}/sendChatAction', params=params)

    def getFile(self, file_id: str):
        url = f'{self.base_url}/getFile'
        params = { 'file_id': file_id }
        return self.webRequest(url, params=params)

    def getChat(self, chat_id: int, handler: Callable):
        url = f'{self.base_url}/getChat'
        self.httpRequests.put((url, {
            'params': {
                'chat_id': chat_id
            }
        }, handler))

    def getWebhookInfo(self, handler: Callable):
        url = f'{self.base_url}/getWebhookInfo'
        self.httpRequests.put((url,None,handler))

    def sendMessage(self, chat_id: int, text: str, params={}):
        url = f'{self.base_url}/sendMessage'
        self.httpRequests.put((url, {
            'params': {
                'chat_id': chat_id,
                'text': text
            }|params
        }, None))

    def forwardMessage(self, chat_id: int, from_chat_id: int, msg_id: int):
        url = f'{self.base_url}/forwardMessage'
        self.httpRequests.put((url,{
            'params': {
                'chat_id': chat_id,
                'from_chat_id': from_chat_id,
                'message_id': msg_id
            }
        },None))

    def editMessageText(self, chat_id: int, msg_id: int, text: str, params={}):
        url = f'{self.base_url}/editMessageText'
        self.httpRequests.put((url,{
            'params': {
                'text':text,
                'chat_id': chat_id,
                'message_id': msg_id
            }|params
        },None))

    def editMessageCaption(self, chat_id: int, msg_id: int, capt: str, params={}):
        url = f'{self.base_url}/editMessageCaption'
        self.httpRequests.put((url, {
            'params': {
                'chat_id': chat_id,
                'message_id': msg_id,
                'caption': capt
            }|params
        }, None))

    def editMessageReplyMarkup(self, chat_id: int, msg_id: int, markup: str, params={}):
        url = f'{self.base_url}/editMessageReplyMarkup'
        self.httpRequests.put((url,{
            'params': {
                'chat_id':chat_id,
                'message_id':msg_id,
                'reply_markup': markup
            }|params
        }, None))

    def deleteMessage(self, chat_id: int, msg_id: int):
        url = f'{self.base_url}/deleteMessage'
        self.httpRequests.put((url,{
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

    def __repr__(self) -> str:
        return f"Autogram({self.config})"

