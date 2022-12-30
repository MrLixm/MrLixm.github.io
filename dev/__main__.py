__all__ = ("start",)

import logging
import logging.config
import sys

import dev.c
import dev.cli

ROOT_PACKAGE: str = dev.__name__

logger = logging.getLogger(f"{ROOT_PACKAGE}.__main__")


def _configureLogging():
    """
    Configure the python logging module
    """

    def get_logs_level() -> int:

        if len(sys.argv) > 1 and sys.argv[1] == "--debug":
            return logging.DEBUG

        env = dev.c.Env.get(dev.c.Env.logs_debug)
        if env is not None and bool(int(env)):
            return logging.DEBUG

        return logging.INFO

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "fmt_standard": {
                "format": "{levelname: <7} | {asctime} |[{name}]{message}",
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
            f"{ROOT_PACKAGE}": {
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
    logger.info(f"[start] Started {dev.c.name} v{dev.c.__version__}")
    dev.cli.cli()
    return


if __name__ == "__main__":

    _configureLogging()
    start()
