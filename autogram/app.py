from autogram.base import Bot

class Autogram(Bot):
  def __init__(self, config) -> None:
    super().__init__(config)
    return

  def start(self):
    self.logger.info('Starting...')
