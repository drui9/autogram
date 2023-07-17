from collections import namedtuple
#
ChatActionTypes = namedtuple(
  'ChatActions', [
    'typing',
    'photo',
    'video',
    'audio',
    'document'
    ])
#
chat_actions = ChatActionTypes(
    'typing',
    'upload_photo',
    'upload_video',
    'upload_voice',
    'upload_document'
  )
#
from autogram.config import Start, save_config, load_config
from autogram.app import Autogram


__all__ = [
  'Start', 'save_config', 'load_config',
  'Autogram', 'chat_actions'
]
