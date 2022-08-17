import os
import time
from typing import Any
from alive_progress import alive_bar
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# 
from autogram import Autogram
from autogram.updates.message import Message



@Message.addHandler
def textHandler(message: Message):
    print(message.attachments)


# hot reload watcher
class Watcher(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.launch()

    def launch(self):
        pub_addr = os.getenv('PUBLIC_URL')
        token = os.getenv('TELEGRAM_TOKEN')
        self.bot = Autogram(token)
        self.bot_thread = self.bot.send_online(pub_addr)


    def on_any_event(self, event: Any):
        if '.py' not in event.src_path:
            return
        # 
        self.bot.terminate.set()
        self.bot_thread.join()
        # 
        print('Reloading ...')
        with alive_bar(5) as bar:
            try:
                for _ in range(5):
                    time.sleep(1)
                    bar()
            except KeyboardInterrupt:
                return
        self.launch()


if __name__ == '__main__':
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    # 
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()
