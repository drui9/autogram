import queue
from autogram.base import Bot

# --
class Autogram(Bot):
  def __init__(self, config) -> None:
    """Initialize parent object"""
    return super().__init__(config)

  def start(self):
    """Launch the bot"""
    if (bot := self.getMe()).ok:
      print(self.poll().json())
    

  def shutdown(self):
    """Gracefully terminate the bot"""
    self.terminate.set()
