import sys
import json
import time
import loguru
import asyncio
import aiohttp
import requests
import threading
from typing import Callable
from typing import Dict, Any
from queue import Queue, Empty
from contextlib import contextmanager
from pyngrok import ngrok, conf as ngrokconf
from concurrent.futures import ThreadPoolExecutor
#
from autogram import *
from autogram.webhook import MyServer
from bottle import request, response, post, run


class Autogram:
    api_url = 'https://api.telegram.org/'

    def __init__(self, config: Dict):
        self.token :str|None = config.get('telegram-token')
        if not self.token:
            print('Missing bot token!')
            sys.exit(1)
        #
        self.config = config
        self._initialize_()

    def _initialize_(self):
        self.webhook = None
        self.host = '0.0.0.0'
        self.edited_ = set()
        self.deleted_ = set()
        self.public_ip = None
        self.update_offset = 0
        self.seenUpdates= list()
        self.ngrok_tunnel = None
        self.httpRoutines = list()
        self.httpRequests = Queue()
        self.failing_endpoints = list()
        self.terminate = threading.Event()
        self.port = self.config['tcp-port']
        self.executor = ThreadPoolExecutor()
        self.base_url = f"{Autogram.api_url}bot{self.token}"
        self.timeout = aiohttp.ClientTimeout(self.config['tcp-timeout'])
        #
        self.guard = {
            'lock': threading.Lock(),
            'pending': Queue(),
            'thread': None
        }
        #
        self.worker_threads = {
            'normal': list(),
            'high': list(),
        }
        self.locks = {
            'session': threading.Lock(),
        }
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
        self.getMe()
        return

    def mediaQuality(self):
        if (qlty := self.config.get("media-quality") or 'high') == 'high':
            return 2
        elif qlty == 'medium':
            return 1
        return 0

    @loguru.logger.catch
    def send_online(self) -> threading.Thread:
        """Get this bot online in a separate daemon thread."""
        if not self.token:
            raise RuntimeError("Send online without token?!")
        if public_ip := self.config['tcp-ip']:
            hookPath = self.token.split(":")[-1].lower()
            @post(f'/{hookPath}')
            def hookHandler():
                self.updateRouter(request.json)
                response.content_type = 'application/json'
                return json.dumps({'ok': True})
            #
            def runServer(server: Any):
                run(server=server, quiet=True)
            #
            server = MyServer(host=self.host,port=self.port)
            serv_thread = threading.Thread(target=runServer, args=(server,))
            serv_thread.name = 'Autogram::Bottle'
            serv_thread.daemon = True
            serv_thread.start()
            # check public ip availability
            if public_ip == 'ngrok':
                ngrok_config = ngrokconf.PyngrokConfig(
                    ngrok_version='v3',
                    ngrok_path= self.config.get('ngrok-path'),
                    auth_token= self.config.get('ngrok-token'),
                    config_path= self.config.get('ngrok-config-path')
                )
                ngrokconf.set_default(ngrok_config)
                try:
                    self.ngrok_tunnel = ngrok.connect()
                    ngrok.get_ngrok_process().stop_monitor_thread()
                    public_ip = self.ngrok_tunnel.public_url
                except Exception as e:
                    self.logger.critical(e)
                    self.shutdown()
            #
            self.public_ip = public_ip
            if not self.terminate.is_set():
                self.webhook = f"{self.public_ip}/{hookPath}"
                self.logger.debug(f'Webhook: {self.webhook}')
        # wrap and start
        def launch():
            if self.terminate.is_set():
                return
            try:
                if sys.platform != 'linux':
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                asyncio.run(self.main_loop())
            except KeyboardInterrupt:
                self.shutdown()
            except Exception as e:
                self.logger.exception(e)
            finally:
                if not self.terminate.is_set():
                    self.shutdown()
        #
        worker = threading.Thread(target=launch)
        worker.name = 'Autogram'
        worker.start()
        return worker

    @loguru.logger.catch()
    async def main_loop(self):
        """Main control loop"""
        processor = asyncio.create_task(self.aioWebRequest())
        if self.webhook:
            url = f'{self.base_url}/setWebhook'
            self.httpRequests.put((url,{
                'params': {
                    'url': self.webhook
                }
            }, None))
        else:   # delete webhook
            def check_webhook(info: dict):
                if url := info['url']:
                    self.logger.debug(f'Webhook deleted: {url}')
            self.deleteWebhook()
            self.getWebhookInfo(check_webhook)
        #
        await processor
        return

    @loguru.logger.catch
    def updateRouter(self, res: Any):
        """receive and route updates"""
        def handle(update: Dict):
            if (uid := update['update_id']) in self.seenUpdates:
                return
            #
            parser = None
            self.seenUpdates.append(uid)
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
            done_routes = ['message', 'callback_query']
            if parser.name not in done_routes:
                self.logger.critical(f"Unimplemented: {parser.name}")
                return
            #
            parser.autogram = self
            self.toThread(parser,payload)
        #
        if type(res) == list:
            for update in res:
                if update['update_id'] >= self.update_offset:
                    self.update_offset = update['update_id'] + 1
                handle(update)
            return
        handle(res)
        return

    def popWorkers(self, workers: list):
        for item in workers:
            key, task = item
            self.worker_threads[key].remove(task)
            continue
        return

    @loguru.logger.catch
    def threadGuard(self):
        workers = 0
        to_remove = list()
        self.guard['lock'].acquire()
        while not self.terminate.is_set():
            try:
                worker = self.guard['pending'].get(timeout=3)
                priority, work = worker
                #
                self.worker_threads[priority].append(work)
                workers += 1
            except Empty:
                continue
            #
            for key in self.worker_threads:
                for task in self.worker_threads[key]:
                    #
                    _ , tsk, cb, errh = task
                    if not tsk.done():
                        continue
                    # fetch results or exceptions
                    try:
                        result = tsk.result()
                        if cb:
                            self.toThread(cb, result)
                    except Exception as e:
                        if errh:
                            errh(e)
                        else:
                            self.logger.exception(e)
                    to_remove.append((key, task))
                    workers -= 1
            #
            self.popWorkers(to_remove)
            to_remove.clear()
        # shutdown executor
        if not workers:
            self.guard['lock'].release()
            return
        elif self.worker_threads['high'] or self.worker_threads['normal']:
            self.logger.debug("Terminating worker threads...")
            #
            for task in self.worker_threads['normal']:
                tsk_id, tsk, cb, _ = task
                if not tsk.done() and not tsk.running():
                    if tsk.cancel():
                        self.logger.debug(f"[{tsk_id}] canceled.")
                    else:
                        self.logger.debug(f"[{tsk_id}] rejected cancel request.")
                elif done := tsk.done() and cb and not tsk.exception():
                    self.logger.debug(f"[{tsk_id}] completed but was ignored on termination.")
                elif done and (e := tsk.exception()):
                    self.logger.exception(e)
                continue
            #
            for worker in self.worker_threads['high']:
                tsk_id, tsk, cb, _ = worker
                if tsk.done():
                    to_remove.append(('high',worker))
                    # propagate result
                    if cb and not tsk.exception():
                        cb(tsk.result())
                    elif e := tsk.exception():
                        self.logger.exception(e)
                        self.logger.debug(f"[{tsk_id}] finished with an error.")
                elif not tsk.running():
                    if tsk.cancel():
                        self.logger.debug(f"[{tsk_id}] : Not started! Canceled.")
                    else:
                        self.logger.debug(f"[{tsk_id}] : Cancel failed!")
                else:
                    self.logger.debug(f"[{tsk_id}] : thread is busy!")
                continue
            self.executor.shutdown(wait=False, cancel_futures=True)
        #
        self.logger.debug("Tasks terminated.")
        self.guard['lock'].release()
        return

    @loguru.logger.catch()
    def toThread(self, *args, callback :Callable|None = None, errHandler :Callable|None = None, priority :str|None = None):
        if self.locks['session'].locked():
            self.logger.debug(f"[{args[0].__name__}] : Blocked execution")
            return
        #
        if not self.guard['lock'].locked():
            self.guard['thread'] = threading.Thread(target=self.threadGuard)
            self.guard['thread'].name = 'Autogram::ThreadGuard'
            self.guard['thread'].start()
        # append worker to priority group
        result = False
        if not priority or (result := (priority not in list(self.worker_threads.keys()))):
            if result:
                self.logger.debug(f"Undefined task priority: {priority}: {args}")
            priority = 'normal'
        #
        tsk_id = args[0].__name__
        try:
            task = self.executor.submit(*args)
            self.guard['pending'].put((priority, (tsk_id, task, callback, errHandler)))
            return task
        except RuntimeError:
            self.shutdown()
        return

    @contextmanager
    def get_request(self):
        """fetch pending or failed task from tasks"""
        if self.failed:
            prev = self.failed
            self.failed = None
            yield prev
            if prev == self.failed:
                time.sleep(2)
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
                        self.shutdown()
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
        return

    @loguru.logger.catch
    async def httpHandler(self):
        while not self.terminate.is_set():
            if not self.httpRoutines:
                await asyncio.sleep(1)
                continue
            #
            for item in self.httpRoutines:
                if self.terminate.is_set():
                    return
                #
                incoming, outgoing = item
                resp, payload = incoming
                link, _, callback = outgoing
                endpoint = link.split('/')[-1]
                #
                if resp.ok:
                    if endpoint in self.failing_endpoints:
                        self.failing_endpoints.remove(endpoint)
                    #
                    if (data := payload.get('result')) and callback:
                        self.toThread(callback, data)
                    elif self.config.get('echo-responses'):
                            self.logger.debug(payload)
                    continue
                elif resp.status == 401:
                    self.logger.critical("Invalid token. Closing...")
                    self.shutdown()
                elif endpoint not in self.failing_endpoints:
                    if payload:
                        self.logger.critical(f"[{endpoint}] HTTP{resp.status} : {endpoint} : {payload}")
                    else:
                        self.logger.critical(f"[{endpoint}] HTTP{resp.status} : {outgoing}")
                # ignore repeated output
                self.failing_endpoints.append(endpoint)
                continue
            # clear handled routines
            self.httpRoutines.clear()

    @loguru.logger.catch()
    async def aioWebRequest(self):
        """Make asynchronous requests to the Telegram API"""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            self.failed = None
            asyncio.create_task(self.httpHandler())
            #
            while not self.terminate.is_set():
                with self.get_request() as request:
                    if not request:
                        if not self.webhook:
                            params = {
                                'params': {
                                    'offset': self.update_offset
                                }
                            }
                            url = f'{self.base_url}/getUpdates'
                            request = (url, params, self.updateRouter)
                            self.httpRequests.put(request)
                        await asyncio.sleep(0)
                        continue
                    #
                    link, kw, _ = request
                    kw = kw or dict()
                    defaults = {
                        'params': {
                            "limit": 81,
                            "offset": self.update_offset,
                            "timeout": self.timeout.total,
                        }
                    }
                    if not kw.get('params'):
                        kw.update(**defaults)
                    else:
                        kw['params'] |= defaults['params']
                    ##
                    if self.terminate.is_set():
                        return
                    #
                    error_detected = None
                    try:
                        async with session.get(link,**kw) as resp:
                            data = None
                            if resp.ok:
                                data = await resp.json()
                            self.logger.debug(f'[{resp.status}] GET /{link.split("/")[-1]}')
                            self.httpRoutines.append(((resp, data), request))
                            await asyncio.sleep(0)
                    except KeyboardInterrupt:
                        self.shutdown()
                    except aiohttp.ClientConnectorError as e:
                        error_detected = e
                    except aiohttp.ClientOSError as e:
                        error_detected = e
                    except asyncio.TimeoutError as e:
                        error_detected = e
                    except RuntimeError as e:
                        error_detected = e
                    except Exception as e:
                        error_detected = e
                        self.shutdown()
                        self.logger.exception(e)
                    finally:
                        if error_detected:
                            self.failed = request
                #
                await asyncio.sleep(0)

    @loguru.logger.catch()
    def webRequest(self, url: str, params={}, files=None):
        res = None
        params = params or {}
        # send request
        try:
            if files:
                res = requests.get(url,params=params,files=files)
            else:
                res = requests.get(url,params=params)
            #
            if res.ok:
                return True, json.loads(res.text)['result']
        except requests.exceptions.ConnectionError:
            self.logger.critical('Connection Error')
            self.shutdown()
        except Exception as e:
            self.logger.exception(e)
        return False, (url, res)

    def shutdown(self, callback :Callable|None = None):
        """callback: your exit function that takes `msg : str`"""
        if self.locks['session'].locked() or self.terminate.is_set():
            return
        # block further updates
        try:
            ngrok.disconnect(self.public_ip)
        except:
            pass
        #
        # start termination
        self.terminate.set()
        if callback:
            try:
                callback()
            except Exception as e:
                self.logger.exception(e)
        # prevent toThread in subsequent calls
        if not self.locks['session'].locked():
            self.locks['session'].acquire()
        # terminate and wait for threadGuard
        self.logger.info('Autogram::terminating...')
        if self.guard['lock'].locked():
            self.guard['thread'].join()
        #
        self.logger.info('Autogram::terminated.')
        return

    #***** start API calls *****#
    def getMe(self):
        """Authenticate bot"""
        url = f'{self.base_url}/getMe'
        ok, res = self.webRequest(url)
        if not ok:
            self.logger.critical("getMe() failed!")
            self.shutdown()
        else:
            for k,v in res.items():
                setattr(self, k, v)

    @loguru.logger.catch()
    def downloadFile(self, file_path: str):
        url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        res = requests.get(url)
        if res.ok:
            return res.content
        else:
            self.logger.critical(f'file: [{file_path} -> Download failed: {res.status_code}')

    @loguru.logger.catch()
    def getFile(self, file_id: str):
        url = f'{self.base_url}/getFile'
        return self.webRequest(url, params={'file_id' : file_id})

    @loguru.logger.catch()
    def getChat(self, chat_id: int, handler: Callable):
        url = f'{self.base_url}/getChat'
        self.httpRequests.put((url, {
            'params': {
                'chat_id': chat_id
            }
        }, handler))

    @loguru.logger.catch()
    def getWebhookInfo(self, handler: Callable):
        url = f'{self.base_url}/getWebhookInfo'
        self.httpRequests.put((url,None,handler))

    @loguru.logger.catch()
    def sendChatAction(self, chat_id: int, action: str):
        params = {
            'chat_id': chat_id,
            'action': action
        }
        return self.webRequest(f'{self.base_url}/sendChatAction', params=params)

    @loguru.logger.catch()
    def sendMessage(self, chat_id :int|str, text :str, **kwargs):
        callback = None
        if 'callback' in kwargs.keys():
            callback = kwargs.pop('callback')
        #
        url = f'{self.base_url}/sendMessage'
        if kwargs.get('urgent'):
            kwargs.pop('urgent')
            params = {
                'params': {
                    'chat_id': chat_id,
                    'text': text,
                } | kwargs
            }
            return self.webRequest(url, **params)
        self.httpRequests.put((url,{
            'params': {
                'chat_id': chat_id,
                'text': text,
            } | kwargs
        } , callback))
        return False, (url, "Add `urgent=True` to kwargs")

    @loguru.logger.catch()
    def deleteMessage(self, chat_id: int, msg_id: int):
        if msg_id in self.deleted_:
            return False
        self.deleted_.add(msg_id)
        url = f'{self.base_url}/deleteMessage'
        self.httpRequests.put((url,{
            'params': {
                'chat_id': chat_id,
                'message_id': msg_id
            }
        }, None))
        return True

    @loguru.logger.catch()
    def deleteWebhook(self):
        url = f'{self.base_url}/deleteWebhook'
        return self.webRequest(url)

    @loguru.logger.catch()
    def editMessageText(self, chat_id: int, msg_id: int, text: str, **kwargs):
        if msg_id in self.deleted_:
            return False
        _hash = hash((chat_id, msg_id, text))
        if _hash in self.edited_:
            return True
        self.edited_.add(_hash)
        #
        url = f'{self.base_url}/editMessageText'
        self.httpRequests.put((url, {
            'params': {
                'text':text,
                'chat_id': chat_id,
                'message_id': msg_id
            } | kwargs
        },None))
        return True

    @loguru.logger.catch()
    def editMessageCaption(self, chat_id: int, msg_id: int, capt: str, params={}):
        url = f'{self.base_url}/editMessageCaption'
        self.httpRequests.put((url, {
            'params': {
                'chat_id': chat_id,
                'message_id': msg_id,
                'caption': capt
            }|params
        }, None))

    @loguru.logger.catch()
    def editMessageReplyMarkup(self, chat_id: int, msg_id: int, markup: str, params={}):
        if msg_id in self.deleted_:
            return False
        #
        url = f'{self.base_url}/editMessageReplyMarkup'
        self.httpRequests.put((url,{
            'params': {
                'chat_id':chat_id,
                'message_id':msg_id,
                'reply_markup': markup
            }|params
        }, None))
        return True

    @loguru.logger.catch()
    def forwardMessage(self, chat_id: int, from_chat_id: int, msg_id: int):
        url = f'{self.base_url}/forwardMessage'
        self.httpRequests.put((url,{
            'params': {
                'chat_id': chat_id,
                'from_chat_id': from_chat_id,
                'message_id': msg_id
            }
        },None))

    @loguru.logger.catch()
    def answerCallbackQuery(self, query_id, text :str|None = None, params : dict|None = None):
        url = f'{self.base_url}/answerCallbackQuery'
        params = params or {}
        text = text or ''
        params.update({
            'callback_query_id':query_id,
            'text': text[:199] # 200 max characters
        })
        return self.webRequest(url, params)

    @loguru.logger.catch()
    def sendPhoto(self,chat_id: int, photo_bytes: bytes, caption: str|None = None, params: dict|None = None):
        params = params or {}
        url = f'{self.base_url}/sendPhoto'
        params.update({
            'chat_id':chat_id,
            'caption': caption,
        })
        self.sendChatAction(chat_id,chat_actions.photo)
        return self.webRequest(url,params=params,files={'photo':photo_bytes})

    @loguru.logger.catch()
    def sendAudio(self,chat_id: int,audio_bytes: bytes, caption: str|None = None, params: dict|None = None):
        params = params or {}
        url = f'{self.base_url}/sendAudio'
        params.update({
            'chat_id':chat_id,
            'caption': caption
        })
        self.sendChatAction(chat_id,chat_actions.audio)
        return self.webRequest(url,params,files={'audio':audio_bytes})

    @loguru.logger.catch()
    def sendDocument(self,chat_id: int ,document_bytes: bytes, caption: str|None = None, params: dict|None = None):
        params = params or {}
        url = f'{self.base_url}/sendDocument'
        params.update({
            'chat_id':chat_id,
            'caption':caption
        })
        self.sendChatAction(chat_id,chat_actions.document)
        return self.webRequest(url,params,files={'document':document_bytes})

    @loguru.logger.catch()
    def sendVideo(self,chat_id: int ,video_bytes: bytes, caption: str|None = None, params: dict|None = None ):
        params = params or {}
        url = f'{self.base_url}/sendVideo'
        params.update({
            'chat_id':chat_id,
            'caption':caption
        })
        self.sendChatAction(chat_id,chat_actions.video)
        return self.webRequest(url,params,files={'video':video_bytes})

    @loguru.logger.catch()
    def forceReply(self, params: dict|None = None):
        params = params or {}
        markup = {
            'force_reply': True,
        }|params
        return json.dumps(markup)

    @loguru.logger.catch()
    def getKeyboardMarkup(self, keys: list, params: dict|None = None):
        params = params or {}
        markup = {
            "keyboard":[row for row in keys]
        }|params
        return json.dumps(markup)

    @loguru.logger.catch()
    def getInlineKeyboardMarkup(self, keys: list, params: dict|None = None):
        params = params or {}
        markup = {
            'inline_keyboard':keys
        }|params
        return json.dumps(markup)

    @loguru.logger.catch()
    def parseFilters(self, filters: dict|None = None):
        filters = filters or {}
        keys = list(filters.keys())
        return json.dumps(keys)

    @loguru.logger.catch()
    def removeKeyboard(self, params: dict|None = None):
        params = params or {}
        markup = {
            'remove_keyboard': True,
        }|params
        return json.dumps(markup)

    def __repr__(self) -> str:
        return f"Autogram({self.config})"

