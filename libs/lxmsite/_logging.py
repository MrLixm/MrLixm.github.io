import enum
import logging
import sys


class LogColors(enum.Enum):
    reset = "\x1b[0m"
    black = "\x1b[30m"
    black_bold = "\x1b[30;1m"
    black_faint = "\x1b[30;2m"
    red = "\x1b[31m"
    red_bold = "\x1b[31;1m"
    red_faint = "\x1b[31;2m"
    green = "\x1b[32m"
    green_bold = "\x1b[32;1m"
    green_faint = "\x1b[32;2m"
    yellow = "\x1b[33m"
    yellow_bold = "\x1b[33;1m"
    yellow_faint = "\x1b[33;2m"
    blue = "\x1b[34m"
    blue_bold = "\x1b[34;1m"
    blue_faint = "\x1b[34;2m"
    magenta = "\x1b[35m"
    magenta_bold = "\x1b[35;1m"
    magenta_faint = "\x1b[35;2m"
    cyan = "\x1b[36m"
    cyan_bold = "\x1b[36;1m"
    cyan_faint = "\x1b[36;2m"
    white = "\x1b[37m"
    white_bold = "\x1b[37;1m"
    white_faint = "\x1b[37;2m"
    grey = "\x1b[39m"


class ColoredFormatter(logging.Formatter):

    COLOR_BY_LEVEL = {
        logging.DEBUG: LogColors.white_faint,
        logging.INFO: LogColors.blue,
        logging.WARNING: LogColors.yellow,
        logging.ERROR: LogColors.red,
        logging.CRITICAL: LogColors.red_bold,
    }

    class DefaultDict(dict):
        def __missing__(self, key):
            return f"{{{key}}}"

    COLOR_MAPPING = DefaultDict({color.name: color.value for color in LogColors})

    def __init__(self, disable_coloring: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._disable_coloring = disable_coloring

    def format(self, record):
        on = not self._disable_coloring
        level_color = self.COLOR_BY_LEVEL.get(record.levelno, None)
        if level_color:
            record.level_color = level_color.value if on else ""
        for color in LogColors:
            setattr(record, color.name, color.value if on else "")

        message = super().format(record)
        if hasattr(record, "resolve_color"):
            message = message.format_map(self.COLOR_MAPPING)
        if not message.endswith(LogColors.reset.value) and on:
            message += LogColors.reset.value
        return message


def configure_logging(
    level=logging.DEBUG,
    disable_coloring: bool = False,
):
    """
    Configure the builtin python logging with custom settings.
    """
    logging.basicConfig(
        level=level,
        stream=sys.stdout,
    )
    log_format = "{level_color}{levelname: <7} {black_bold}| {asctime} {name: <25} |{reset}{level_color} {message}"
    log_formatter = ColoredFormatter(
        fmt=log_format,
        style="{",
        disable_coloring=disable_coloring,
    )
    for handler in logging.getLogger().handlers:
        handler.setFormatter(log_formatter)
