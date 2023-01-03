from collections import namedtuple

ChatActionTypes = namedtuple('ChatActions', ['typing', 'photo', 'video', 'audio', 'document'])
chat_actions = ChatActionTypes('typing', 'upload_photo', 'upload_video', 'upload_voice', 'upload_document')
# 
from .config import *
from .updates import *
from .main import Autogram
