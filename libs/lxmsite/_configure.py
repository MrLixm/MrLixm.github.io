import dataclasses
import logging
import runpy
from pathlib import Path

from lxmsite import ShelfLabel

LOGGER = logging.getLogger(__name__)


def mkfield(metadata):
    return dataclasses.field(metadata=metadata)


@dataclasses.dataclass
class SiteConfig:
    """
    User configuration that affect how the site is built.

    All the fields are mandatory and there is no defaults.
    """

    SRC_ROOT: Path = mkfield({"type": Path})
    TEMPLATES_ROOT: Path = mkfield({"type": Path})
    SHELF_LABELS: list[ShelfLabel] = mkfield({"type": list})
    DEFAULT_DOCUTILS_SETTINGS: dict = mkfield({"type": dict})

    @classmethod
    def from_path(cls, path: Path) -> "SiteConfig":
        """
        Unserialize a config from the given file.
        """
        context = runpy.run_path(str(path))
        config_dict = {}
        for field in dataclasses.fields(cls):
            if field.name not in context:
                raise KeyError(
                    f"Field '{field.name}' is not defined in site config file."
                )
            option_value = context[field.name]
            if not isinstance(option_value, field.metadata["type"]):
                raise TypeError(
                    f"Field '{field.name}' must be of type '{field.type}', got '{type(option_value)}'"
                )
            config_dict[field.name] = context[field.name]

        return cls(**config_dict)
