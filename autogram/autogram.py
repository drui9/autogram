import json
from threading import Event
from autogram.base import Bot

# --
class Autogram(Bot):
  #--
  def __init__(self, config):
    self.initialized = Event()
    return super().__init__(config)

  #--
  def run(self):
    if not self.initialized.is_set():
      #-- load settings
      try:
        self.data('offset')
      except KeyError:
        self.data('offset', 0)
      #-- load self
      if (bot := self.getMe()).ok:
        for name, value in bot.json().items():
          setattr(self, name, value)
        self.initialized.set()
    #--
    offset = self.data('offset')
    for rep in self.poll(offset=offset).json()['result']:
      self.data('offset', rep.pop('update_id') + 1)
      with self.register['lock']:
        if handler := self.register['handlers'].get(list(rep.keys())[-1]):
          handler(self, rep)
