import logging
from pythonjsonlogger import jsonlogger

class CustomLogger:
    """
    Custom json logger
    """
    def __init__(self):
        self.logger = self._addJsonFormat()
    
    def _addJsonFormat(self):
        logger     = logging.getLogger('AcmeBot')
        logHandler = logging.StreamHandler()
        logHandler.setLevel(logging.INFO)
        
        # TODO: unify the json logger default fields
        custom_format = ' '.join([
            '%(asctime)s',
            '%(name)s',
            '%(module)s',
            '%(funcName)s',
            '%(levelname)s',
            '%(message)s'])

        logHandler.setFormatter(jsonlogger.JsonFormatter(custom_format, datefmt='%m/%d/%Y %I:%M:%S %p'))
        logger.addHandler(logHandler)
        logger.setLevel(logging.INFO)
        return logger



