import os
import pexpect
import threading
import datetime
from loguru import logger
from multiprocessing import Queue

class IP:
    ngrok_config = f"/home/{os.getenv('USER')}/.ngrok2/ngrok.yml"
    
    @classmethod
    def del_config(cls):
        if os.path.exists(cls.ngrok_config):
            os.remove(cls.ngrok_config)
        return

    @classmethod
    def make_config(cls, token :str):
        cls.del_config()
        ngrok = pexpect.spawn(f'ngrok authtoken {token}')
        ngrok.wait()
        ngrok.close()
        return os.path.exists(cls.ngrok_config)
    
    def __init__(self, token =None, httpPort=80):
        self.ip = Queue()
        self.__current = None
        self.token = token
        self.expiry = None
        self.port = httpPort
        self.logger = logger
        self.delta = datetime.timedelta(minutes=100)
        self.disconnect = threading.Event()
        self.terminate = threading.Event()
        self.disconnect.set()
        #
        self.iploop = threading.Thread(target=self.loop)
        self.iploop.daemon = True
        self.iploop.start()
        self.logger.debug(f'Opening http tunnel to {httpPort}')
        
    def loop(self):
        if self.token:
            self.make_config(self.token)
        else:
            self.del_config()
        ngrok = pexpect.spawn(f'ngrok http {self.port}')
        status = ['connecting', 'online', 'reconnecting']
        flag = "Session Status"
        collect = False
        expect_ip = False
        collected = list()
        collect_ip = False
        collected_ip = list()
        seen = list()
        while not self.terminate.is_set():
            try:
                # check expiry
                if self.expiry and datetime.datetime.utcnow() > self.expiry:
                    self.expiry = None
                    raise pexpect.exceptions.EOF("Expired")
                #
                char = ngrok.read_nonblocking(timeout=3).decode()
                if char == ' ':
                    if seen and seen[-1] == ' ':
                        continue
                elif collect:
                    collected.append(char)
                    if (st:= ''.join(collected)) in status:
                        collect = False
                        collected.clear()
                        if st == 'online':
                            expect_ip = True
                        else:
                            self.disconnect.set()
                    continue
                seen.append(char)
                if len(seen) < len(flag):
                    continue
                if expect_ip:
                    if ''.join(seen[-10:]) == 'Forwarding':
                        collect_ip = True
                        collected_ip.clear()
                if collect_ip:
                    collected_ip.append(char)
                    if collected_ip[-1] == '>':
                        collect_ip = False
                        expect_ip = False
                        split = "https://"
                        theip = f"{split}{''.join(collected_ip[:-3]).split(split)[-1]}"
                        self.ip.put(theip)
                        self.disconnect.clear()
                        if not self.expiry and not self.token:
                            self.expiry = datetime.datetime.utcnow() + self.delta
                _flag = ''.join(seen[-len(flag):])
                if _flag == flag:
                    collect = True
                    seen.clear()
            except pexpect.exceptions.TIMEOUT:
                continue
            except pexpect.exceptions.EOF:
                self.logger.info('Restarting ngrok')
                ngrok.close()
                ngrok = pexpect.spawn(f'ngrok http {self.port}')
                collect = False
                expect_ip = False
                collected.clear()
                collect_ip = False
                collected_ip.clear()
                seen.clear()
            except:
                break
        ngrok.close()
        self.disconnect.set()
        return

    def __repr__(self):
        if self.disconnect.is_set():
            if not self.iploop.is_alive():
                raise ChildProcessError('Ngrok process exited.')
            self.logger.info('Renewing tunnel ip')
            ip = self.ip.get(timeout=None)
            if ip != self.__current:
                self.__current = ip
        self.logger.info('Tunnel connected')
        return self.__current
