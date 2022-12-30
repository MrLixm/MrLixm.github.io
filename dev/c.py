"""
Constants.
Lowest level module.
"""
from __future__ import annotations

__all__ = ("name", "__version__")

import enum
import os
from typing import Any

__version_major__ = 0
__version_minor__ = 1
__version_patch__ = 0
__version__ = f"{__version_major__}.{__version_minor__}.{__version_patch__}"
if __version_prerelease__ := "":
    __version__ += f"-{__version_prerelease__}"

name = "blogdev"


""" ------------------------------------------------------------------------------------
ENVIRONMENT VARIABLES

All are optionals.
"""

ENVPREFIX = name.upper()


class Env(enum.Enum):

    logs_debug = f"{ENVPREFIX}_LOGS_DEBUG"
    """
    Set logging to debug level
    """

    debug = f"{ENVPREFIX}_DEBUG"
    """
    Enable the debug mode for the application
    """

    @classmethod
    def __all__(cls):
        return [attr for attr in cls]

    @classmethod
    def __asdict__(cls) -> dict[str, str]:
        out = dict()
        for attr in cls.__all__():
            out[str(attr.value)] = cls.get(attr)
        return out

    @classmethod
    def get(cls, key: Env, default: Any = None) -> str | None | Any:
        return os.environ.get(str(key.value), default)
