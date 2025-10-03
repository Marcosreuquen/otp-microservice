import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Per-run filename with timestamp
_run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
_log_filename = os.path.join(LOG_DIR, f"otp-microservice-{_run_ts}.log")

# Create module-level logger
_logger = logging.getLogger("otp")
_logger.setLevel(logging.DEBUG)

# File handler (rotating to be safe)
_file_handler = RotatingFileHandler(_log_filename, maxBytes=10 * 1024 * 1024, backupCount=3)
_file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_file_handler.setFormatter(_file_formatter)
_logger.addHandler(_file_handler)

# Console handler with simple colors
class _ColorFormatter(logging.Formatter):
    COLORS = {
        'INFO': '\033[94m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'DEBUG': '\033[92m',
        'RESET': '\033[0m'
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        message = super().format(record)
        return f"{color}{message}{reset}"

_console_handler = logging.StreamHandler()
_console_formatter = _ColorFormatter("%(asctime)s [%(levelname)s] %(message)s")
_console_handler.setFormatter(_console_formatter)
_logger.addHandler(_console_handler)


class Logger:
    """Wrapper around the module logger. Use Logger.info/debug/warning/error.

    Logs are sent both to console and into a per-run file under `logs/`.
    """

    @staticmethod
    def info(*args, sep=' '):
        _logger.info(sep.join(map(str, args)))

    @staticmethod
    def warning(*args, sep=' '):
        _logger.warning(sep.join(map(str, args)))

    @staticmethod
    def error(*args, sep=' '):
        _logger.error(sep.join(map(str, args)))

    @staticmethod
    def debug(*args, sep=' '):
        _logger.debug(sep.join(map(str, args)))

    @staticmethod
    def get_logger():
        return _logger