from config import *

class Logger:

    __level = logLevels.level

    @staticmethod
    def log_error(message):
        if Logger.__level >= logLevels.error:
            Logger.__log(message)

    @staticmethod
    def log_warn(message):
        if Logger.__level >= logLevels.warn:
            Logger.__log(message)

    @staticmethod
    def log_info(message):
        if Logger.__level >= logLevels.info:
            Logger.__log(message)

    @staticmethod
    def log_debug(message):
        if (Logger.__level >= logLevels.debug):
            Logger.__log(message)

    @staticmethod
    def __log(message):
        print message