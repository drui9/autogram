import os
import loguru
from autogram.base import Bot
from sqlalchemy import create_engine


class Autogram(Bot):
  def __init__(self, config) -> None:
    super().__init__(config)
    return

  def start(self):
    self.webhook_addr = self.config.get('AUTOGRAM_ENDPOINT') or os.getenv('AUTOGRAM_ENDPOINT')
    if self.webhook_addr:
      res = self.setWebhook(self.webhook_addr)
    else:
      res = self.deleteWebhook()
    if not res.ok:
      self.do_err('Prepare updates source failed!')
