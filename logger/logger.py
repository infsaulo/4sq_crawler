import logging
import socket
import os

class Logger:
    """
    Implements e logging system. According with the logging
    library it applies every level of logging from DEBUG to CRITICAL according with the user cases.

    Attrs:
       log_filename: containing a name where the log messages gonna be written.
       log_name: containing the name of logger object. For while is a proper machine name appended with the process_id where
        logger is instancied.

    Methods:
        put_message: writes some message to the logger object
    """
    def __init__(self, log_name='', log_filename=None):
        if log_filename:
            self.logger = logging.getLogger(socket.gethostname() + ':' + str(os.getpid()) + log_name)
            if not self.logger.handlers:
                file_handler = logging.FileHandler(log_filename)
                file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                self.logger.addHandler(file_handler)
                self.logger.setLevel(logging.CRITICAL)
                self.logger.setLevel(logging.ERROR)
                self.logger.setLevel(logging.WARNING)
                self.logger.setLevel(logging.INFO)
                self.logger.setLevel(logging.DEBUG)

    def put_message(self, logger_level, message):
        """
        Writes some message to the logger object and put the 
        content in a log file.
        
        Args:
            logger_level: is a string defining what level the
            message is to be. According with the logging
            documentation, the levels are: 'critical',
            'error', 'warning', 'info', 'debug'.
            message: can be a string, or some Exception object
        """
        if logger_level == 'critical':
            self.logger.critical(message)
        elif logger_level == 'error':
            self.logger.error(message)
        elif logger_level == 'warning':
            self.logger.warning(message)
        elif logger_level == 'info':
            self.logger.info(message)
        elif logger_level == 'debug':
            self.logger.debug(message)
