import queue
from . import ChatActionTypes
from multiprocessing import Queue

#
chat_actions = ChatActionTypes(
    'typing',
    'upload_photo',
    'upload_video',
    'upload_voice',
    'upload_document'
  )

class Autogram:
    # terminate = threading.Event() >> extern :updates
    #info = dict() >> extern :updates
    #
    def __init__(self, token :str):
        self.token = token
        self.updates = Queue()

    def start(self):
        while not self.terminate.is_set():
            try:
                update = self.updates.get(timeout=7)
                print(update)
            except queue.Empty:
                continue
