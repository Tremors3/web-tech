import logging

class bcolors:
    GREEN = '\033[32m'
    RESET = '\033[0m'
    DEBUG = '\033[34m'
    INFO = '\033[37m'
    WARNING = '\033[33m'
    ERROR = '\033[31m'
    CRITICAL = '\033[91m'

class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG:    bcolors.DEBUG    + "%(asctime)s - %(levelname)s - %(message)s" + bcolors.RESET,
        logging.INFO:     bcolors.INFO     + "%(asctime)s - %(levelname)s - %(message)s" + bcolors.RESET,
        logging.WARNING:  bcolors.WARNING  + "%(asctime)s - %(levelname)s - %(message)s" + bcolors.RESET,
        logging.ERROR:    bcolors.ERROR    + "%(asctime)s - %(levelname)s - %(message)s" + bcolors.RESET,
        logging.CRITICAL: bcolors.CRITICAL + "%(asctime)s - %(levelname)s - %(message)s" + bcolors.RESET,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        return logging.Formatter(log_fmt).format(record)
