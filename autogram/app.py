import os
import loguru
from autogram.base import Bot
from autogram.models import *
from requests.exceptions import ConnectionError


class Autogram(Bot):
  def __init__(self, config) -> None:
    """Initialize super, then database metadata respectively"""
    super().__init__(config)
    Base.metadata.create_all(bind=self.engine)
    return

  def prepare(self):
    """Confirm auth through getMe(), then check update methods"""
    res = self.getMe()
    if not res.ok:
      self.do_err(msg=str(res.json()))
    self.logger.info(res.json())
    self.webhook_addr = self.config.get('AUTOGRAM_ENDPOINT') or os.getenv('AUTOGRAM_ENDPOINT')
    if self.webhook_addr:
      res = self.setWebhook(self.webhook_addr)
    else:
      res = self.deleteWebhook()
    if not res.ok:
      self.do_err(msg=(str(res.json()) or 'Initialization error'))
    return

  def start(self):
    try:
      self.prepare()
      self.terminate.wait(timeout=10)
    except ConnectionError:
      self.terminate.set()
      self.logger.critical('Connection Error!')
    finally:
      self.shutdown()

  def shutdown(self):
    if self.terminate.is_set():
      try:
        res = self.getWebhookInfo()
        if not res.ok:
          return
        if not res.json()['result']['url']:
          return
      except:
        return
    # delete webhook and exit
    try:
      res = self.deleteWebhook()
      if not res.ok:
        raise RuntimeError()
      self.logger.info('Deleted webhook.')
    except Exception as e:
      self.logger.critical('/deleteWebhook failed!')
    finally:
      self.terminate.set()
