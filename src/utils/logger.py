from colorama import Fore, Style
import logging

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    format = "%(asctime)s - %(name)-17s - %(levelname)-8s - %(message)s"

    FORMATS = {
        logging.DEBUG: Fore.LIGHTBLACK_EX + format + Style.RESET_ALL,
        logging.INFO: grey + format + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CustomLogger:

    def __init__(self, name: str, min_level: int = logging.DEBUG):
        self.__logger: logging.Logger = logging.getLogger(name)
        self.__logger.setLevel(min_level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(min_level)
        console_handler.setFormatter(CustomFormatter())
        self.__logger.addHandler(console_handler)

    def set_min_level(self, min_level: int):
        self.__logger.setLevel(min_level)
        for handler in self.__logger.handlers:
            handler.setLevel(min_level)

    def debug(self, msg: str, *args):
        self.__logger.debug(msg, *args)

    def info(self, msg: str, *args):
        self.__logger.info(msg, *args)

    def warn(self, msg: str, *args):
        self.__logger.warning(msg, *args)

    def error(self, msg: str, *args):
        self.__logger.error(msg, *args)
