import logging
import random
import time
from typing import Callable

from django.conf import settings

logger = logging.getLogger(__name__)

SleepFn = Callable[[float], None]


def _default_sleep(seconds: float) -> None:
    time.sleep(seconds)


def send_email(
    *,
    email: str,
    subject: str,
    message: str,
    sleep_fn: SleepFn | None = None,
) -> None:
    """Simulate email delivery by sleeping and writing to the log."""
    delay_range = getattr(settings, "MAILING_SEND_DELAY_RANGE", (5, 20))
    sleep = sleep_fn or _default_sleep
    sleep(random.randint(*delay_range))

    logger.info(
        "Send EMAIL to %s | subject=%r | message=%r",
        email,
        subject,
        message,
    )
