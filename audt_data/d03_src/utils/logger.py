"""
[augmented urban data triangulation (audt)]
[audt-data]
[Logger]
[Module containing ColorfulFormatter, returned classes for logger]
[Matt Franchi]
"""

import logging
import os
import inspect
from termcolor import colored

from functools import partial, partialmethod


class ColorfulFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": {"color": "black", "attrs": []},
        "INFO": {"color": "blue", "attrs": []},
        "WARNING": {"color": "yellow", "attrs": []},
        "ERROR": {"color": "red", "attrs": []},
        "CRITICAL": {"color": "red", "attrs": []},
        "SUCCESS": {"color": "green", "attrs": []},
    }

    def format(self, record):
        log_level = record.levelname
        msg = super().format(record)
        return colored(
            msg,
            self.COLORS.get(log_level)["color"],
            attrs=self.COLORS.get(log_level)["attrs"],
        )


def add_logging_level(level_name, level_num, method_name=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `level_name` becomes an attribute of the `logging` module with the value
    `level_num`.
    `methodName` becomes a convenience method for both `logging` itself
    and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`).
    If `methodName` is not specified, `levelName.lower()` is used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> add_logging_level('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel('TRACE')
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError(f"{level_name} already defined in logging module")
    if hasattr(logging, method_name):
        raise AttributeError(
            f"{method_name} already defined in logging module"
        )
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError(f"{method_name} already defined in logger class")

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # https://stackoverflow.com/a/35804945
    # https://stackoverflow.com/a/55276759
    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(
        logging.getLoggerClass(),
        method_name,
        partialmethod(logging.getLoggerClass().log, level_num),
    )
    setattr(logging, method_name, partial(logging.log, level_num))


def get_module_name(name=None):
    """
    Get a clean module name from the caller's module or a provided name.
    If the name is part of the audt project, it will be shortened to the relative path.
    """
    if name == "__main__":
        # Get the caller's filename if called from main
        frame = inspect.stack()[2]
        filepath = frame.filename
        name = filepath
    
    if isinstance(name, str) and "audt" in name:
        # For files in the audt project, extract the part after 'audt/'
        parts = name.split('audt/')
        if len(parts) > 1:
            return f"audt.{parts[1].replace('/', '.').replace('.py', '')}"
    
    return name


def setup_logger(name=__name__, log_level=logging.INFO):
    """
    Set up a logger for the AUDT project.
    
    Args:
        name: The logger name, defaults to the module name
        log_level: The logging level to use (default: INFO)
    
    Returns:
        A configured logger instance
    """
    logging.getLogger().setLevel(logging.CRITICAL)
    
    # Get a clean module name
    module_name = get_module_name(name)
    
    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)

    if logger.hasHandlers():
        logger.handlers.clear()

    try:
        add_logging_level("SUCCESS", 25)
    except AttributeError as e:
        logger.debug(e)

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers - add AUDT prefix
    format_str = "%(asctime)s - [audt] - %(name)s - %(levelname)s - %(message)s"
    formatter = ColorfulFormatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(ch)

    # prevent propagation of log messages to parent logger
    logger.propagate = False

    # disable root logger
    logging.getLogger().handlers = []

    return logger
