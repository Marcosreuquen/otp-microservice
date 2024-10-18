import logging
from datetime import datetime

class Logger:
    # Colores para los logs
    COLORS = {
        'INFO': '\033[94m',  # Azul
        'WARNING': '\033[93m',  # Amarillo
        'ERROR': '\033[91m',  # Rojo
        'DEBUG': '\033[92m',  # Verde
        'RESET': '\033[0m'    # Reset
    }

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)


    @staticmethod
    def _log(level, *args, sep=' ', end='\n'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = sep.join(map(str, args))  # Convierte los argumentos en un solo string como lo hace print
        color = Logger.COLORS.get(level, Logger.COLORS['RESET'])
        reset_color = Logger.COLORS['RESET']
        print(f"{color}[{timestamp}] [{level}] {message}{reset_color}", end=end)

    @staticmethod
    def info(*args, sep=' ', end='\n'):
        Logger._log('INFO', *args, sep=' ', end='\n')
    @staticmethod
    def warning(*args, sep=' ', end='\n'):
        Logger._log('WARNING', *args, sep=' ', end='\n')
    @staticmethod
    def error(*args, sep=' ', end='\n'):
        Logger._log('ERROR', *args, sep=' ', end='\n')
    @staticmethod
    def debug(*args, sep=' ', end='\n'):
        Logger._log('DEBUG', *args, sep=' ', end='\n')