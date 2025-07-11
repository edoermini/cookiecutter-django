import logging
from collections.abc import Callable
from functools import wraps
from time import monotonic

from django.core.cache import cache

logger = logging.getLogger(__name__)


def no_simultaneous_execution(lock_expiration_time: int = 600):
    """Prevent simultaneous execution of a task with the same *args and **kwargs.

    Args:
        lock_expiration_time (int, optional): Temporal window expressed in seconds \
            within there are no simultaneous
        executions of the same task. Defaults to 600.

    Returns:
        Callable: Decorated task.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def _wrapper(self, *args, **kwargs):
            # Create lock_id used as cache key
            lock_id = f"{self.name}-{args!s}-{kwargs!s}"
            # Timeout with a small diff, so we'll leave the lock delete
            # to the cache if it's close to being auto-removed/expired
            timeout_at = monotonic() + lock_expiration_time - 3
            # Try to acquire a lock, or put task back on queue
            lock_acquired = cache.add(lock_id, value=True, timeout=lock_expiration_time)
            if not lock_acquired:
                logger.debug(
                    "Execution of %s skipped, another process is running.",
                    str(self.name),
                )

                return None
            try:
                return func(self, *args, **kwargs)
            finally:
                # Release the lock
                if monotonic() < timeout_at:
                    cache.delete(lock_id)

        return _wrapper

    return decorator
