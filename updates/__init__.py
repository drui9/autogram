from threading import Event
import loguru

# shutdown notifier
terminate = Event()
logger = loguru.logger

# define endpoint
endpoint = 'https://api.telegram.org/'

# import modules
from updates.hook import WebHook  # noqa: F401, E402
from updates.short import ShortPoll  # noqa: F401, E402
