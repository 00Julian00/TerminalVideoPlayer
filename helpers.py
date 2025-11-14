import time
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)

def measure_exec_speed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed_us = (end - start) * 1_000_000  # microseconds
        elapsed_ms = elapsed_us / 1000
        logging.info(f"Execution time for {func.__name__}: {elapsed_ms:.3f} ms")
        return result
    return wrapper