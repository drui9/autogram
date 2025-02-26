"""
@author: drui9
@description: Example usage
"""

import time
import requests
from loguru import logger
from threading import Event
from autogram import Autogram, Start, Update, ChatAction
from watchdog.observers import Observer
from contextlib import contextmanager


@contextmanager
def autoreload(path: str):
    event_handler = 1  # handler
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()


# --
class ExampleBot(Autogram):
    def __init__(self, config):
        super().__init__(config)
        self.exit = Event()
        self.userdata = {
            "chats": dict(),
            "groups": dict(),
            "supergroups": dict(),
            "users": {"banned": list(), "active": list()},
        }

    @property
    def stop(self):
        return self.exit.is_set()

    def run(self):
        """Custom implementation of bot.poll()"""
        super().run()  # initializes bot info, abstractmethod
        logger.debug(f"{self.username} initialized.")
        while not self.stop:  # should be endless loop
            try:
                offset = self.data("offset")  # fetch persisted offset
                for rep in self.poll(offset=offset).json()["result"]:
                    self.data("offset", rep.pop("update_id") + 1)  # persist new offset
                    with self.register[
                        "lock"
                    ]:  # ensure handlers are not modified during call
                        if handler := self.register["handlers"].get(
                            list(rep.keys())[-1]
                        ):
                            handler(self, self, rep)  # call handler. Maybe try except?
                time.sleep(4)  # rate limit
            except requests.exceptions.SSLError():
                pass
            except requests.exceptions.ReadTimeout:
                pass
            except requests.exceptions.ProxyError:
                pass
            except Exception:
                logger.exception("what?")

    @Autogram.add(Update.message)
    def message(self, bot: Autogram, update):
        logger.debug(update)
        # logger.debug(update["message"]["text"])
        # chat_id = update["message"]["chat"]["id"]
        # keyb = [
        #     [
        #         {"text": "Buy", "callback_data": "open-boy"},
        #         {"text": "Cancel", "callback_data": "buy-cancel"},
        #     ]
        # ]
        # data = {"reply_markup": bot.getInlineKeyboardMarkup(keyb)}
        # bot.sendMessage(chat_id, "Tickle me!", **data)

    # --
    @Autogram.add(Update.callback)
    def callback_query(self, bot: Autogram, update):
        logger.debug(update)
        # callback_id = update["callback_query"]["id"]
        # bot.answerCallbackQuery(callback_id, "Ha-ha-ha")

    @Autogram.add(Update.my_chat_member)
    def my_chat_member(self, bot: Autogram, update):
        logger.debug(update)

    @Autogram.add(Update.channel_post)
    def channel_post(self, bot: Autogram, update):
        logger.debug(update)


# ***************************** <start>
@Start()
def main(config):
    bot = ExampleBot(config)
    bot.run()


# ************ </start>
