import dataclasses
import json
import logging
import runpy
from pathlib import Path

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
    DST_ROOT: Path | None = mkfield({"type": (Path, type(None))})
    TEMPLATES_ROOT: Path = mkfield({"type": Path})
    DEFAULT_DOCUTILS_SETTINGS: dict = mkfield({"type": dict})
    SITE_URL: str = mkfield({"type": str})
    PUBLISH_MODE: bool = mkfield({"type": bool})
    DEFAULT_PAGE_ICON: str = mkfield({"type": str})
    DEFAULT_STYLESHEETS: list[str] = mkfield({"type": list})
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
