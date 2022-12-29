__all__ = ("start",)

import logging
import logging.config
import sys

from . import c
from . import cli


logger = logging.getLogger(f"{c.__name__}.__main__")


def _configureLogging():
    """
    Configure the python logging module
    """

    def get_logs_level() -> int:

        if len(sys.argv) > 1 and sys.argv[1] == "--debug":
            return logging.DEBUG

        env = c.Env.get(c.Env.logs_debug)
        if env is not None and bool(int(env)):
            return logging.DEBUG

        return logging.INFO

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "fmt_standard": {
                "format": "{levelname: <7} | {asctime} |[{name: >30}]{message}",
                "style": "{",
            }
        },
        "handlers": {
            "hl_console": {
                "level": "DEBUG",
                "formatter": "fmt_standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            f"{c.__name__}": {
                "handlers": ["hl_console"],
                "level": get_logs_level(),
                "propagate": False,
            },
            f"__main__": {
                "handlers": ["hl_console"],
                "level": logging.DEBUG,
                "propagate": False,
            },
        },
    }
    # register
    logging.config.dictConfig(logging_config)
    return


def start():
    """
    Start the application.
    """
    logger.info(f"[start] Started {c.name} v{c.__version__}")
    cli.cli()
    return


if __name__ == "__main__":

    _configureLogging()
    start()
