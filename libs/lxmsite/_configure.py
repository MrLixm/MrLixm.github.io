import dataclasses
import json
import logging
import runpy
from pathlib import Path
from typing import Callable

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class ShelfLabel:
    """
    A page's metadata field collected to generate procedural "browser" pages.
    """

    name: str
    """
    An human-readable pretty name with any characters.
    """

    rst_key: str
    """
    The name of the rst field from which the page will get its label.
    """

    slug: str
    """
    url-safe name to use for web page generation
    """

    sorter: Callable[[list[str]], list[str]] = sorted
    """
    Determine how to sort the collection of metadata aggregated from all the pages.

    This is a Callable (function) that:

    - Receives: a list of strings whose value is the raw one from the source page.
    - Returns: the same values but sorted as preferred for this driver.
    """

    @classmethod
    def from_name(cls, name: str) -> "ShelfLabel":
        """
        A shortand method where the name is used to derives all other fields.
        """
        return cls(name=name, rst_key=name, slug=name)


def mkfield(metadata):
    return dataclasses.field(metadata=metadata)


@dataclasses.dataclass
class SiteConfig:
    """
    User configuration that affect how the site is built.

    All the fields are mandatory and there is no defaults.
    """

    SRC_ROOT: Path = mkfield({"type": Path})
    DST_ROOT: Path | None = mkfield({"type": (Path, type(None))})
    TEMPLATES_ROOT: Path = mkfield({"type": Path})
    SHELF_LABELS: list[ShelfLabel] = mkfield({"type": list})
    DEFAULT_DOCUTILS_SETTINGS: dict = mkfield({"type": dict})
    SITE_URL: str = mkfield({"type": str})
    PUBLISH_MODE: bool = mkfield({"type": bool})
    HEADER_NAV: dict[str, str] = mkfield({"type": dict})

    def sanitize(self):
        """
        Perform some user-input sanitization.
        """
        self.SRC_ROOT = self.SRC_ROOT.resolve()
        self.DST_ROOT = self.DST_ROOT.resolve() if self.DST_ROOT else None
        self.TEMPLATES_ROOT = self.TEMPLATES_ROOT.resolve()
        self.SITE_URL = self.SITE_URL.rstrip("/")
        for name, path in self.HEADER_NAV.items():
            if path.startswith("./"):
                self.HEADER_NAV[name] = path.removeprefix("./")

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

    def debug(self) -> str:
        """
        Return the config content as a human-debuggable string.
        """
        return "SiteConfig" + json.dumps(
            dataclasses.asdict(self),
            indent=4,
            default=str,
        )
