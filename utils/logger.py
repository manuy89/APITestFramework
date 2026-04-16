import logging
import logging.handlers
import os
import queue
import threading
from config.paths import LOGS_DIR

LOGS_DIR.mkdir(exist_ok=True)

_queue = queue.Queue()
_listener = None
_listener_lock = threading.Lock()


def _start_listener():
    global _listener
    with _listener_lock:
        if _listener is None:
            worker_id = os.getenv("PYTEST_XDIST_WORKER", "master")
            log_file = LOGS_DIR / f"test_run_{worker_id}.log"

            formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

            fh = logging.FileHandler(log_file, mode="w")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)

            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)

            _listener = logging.handlers.QueueListener(_queue, fh, ch, respect_handler_level=True)
            _listener.start()


def get_logger(name):
    _start_listener()
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        queue_handler = logging.handlers.QueueHandler(_queue)
        logger.addHandler(queue_handler)
    return logger


def stop_listener():
    global _listener
    if _listener:
        _listener.stop()
        _listener = None
