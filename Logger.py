import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from threading import Lock


class ColoredFormatter(logging.Formatter):
    COLOR_MAP = {
        logging.DEBUG: "\033[90m",  # Bright black (gray)
        logging.INFO: "\033[92m",  # Green
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",  # Red
        logging.CRITICAL: "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLOR_MAP.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


class Logger:
    _instances = {}
    _lock = Lock()

    def __new__(cls, name: str = __name__, *args, **kwargs):
        with cls._lock:
            if name not in cls._instances:
                instance = super(Logger, cls).__new__(cls)
                cls._instances[name] = instance
            return cls._instances[name]

    def __init__(self, name: str = __name__, log_file: str = None, level: int = logging.INFO):
        if hasattr(self, "_initialized"):
            return  # Prevent reinitialization

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        log_format = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"

        formatter = logging.Formatter(log_format, datefmt)
        color_formatter = ColoredFormatter(log_format, datefmt)

        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(color_formatter)
        self.logger.addHandler(console_handler)

        # Optional file handler
        if log_file:
            log_path = Path(log_file)
            os.makedirs(log_path.parent, exist_ok=True)

            file_handler = logging.FileHandler(log_file, mode='a')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self._initialized = True

    # Overridden logging methods for direct use
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def get_logger(self):
        return self.logger
