from threading import Event
from autogram.base import Bot
from abc import abstractmethod

# --
class Autogram(Bot):
  def __init__(self, config):
    self.initialized = Event()
    return super().__init__(config)

  #--
  @abstractmethod
  def run(self):
    if not self.initialized.is_set():
      #-- load settings
      try:
        self.data('offset')
      except KeyError:
        self.data('offset', 0)
      #-- load self
      if (bot := self.getMe()).status_code != 200:
        raise RuntimeError(bot.json())
      #--
      info = bot.json()['result']
      for name, value in info.items():
        setattr(self, name, value)
      return self.initialized.set()

