import ast
import dataclasses
import logging
from pathlib import Path

from lxmsite import PageResource

LOGGER = logging.getLogger(__name__)


def mkfield(metadata):
    return dataclasses.field(metadata=metadata)


@dataclasses.dataclass
class ShelfConfig:
    """
    Defines how to handle the pages belonging to a specific shelf.
    """

    disabled_labels: list[str] = dataclasses.field(
        default_factory=list,
        metadata={"type": list, "required": False},
    )
    """
    list of shelf label slugs that should not be used to generate procedural "browser" pages.
    """

    default_template: str = dataclasses.field(
        default=None,
        metadata={"type": str, "required": True},
    )
    """
    Path to a registred jinja template to use for rendering all the page of the shelf.

    This is a default value that can be overriden individually by each page.
    """

    ignored_pages: list[str] = dataclasses.field(
        default_factory=list,
        metadata={"type": list, "required": False},
    )
    """
    list of page filenames that will be included in the final site but are not part of the procedural "browser" pages.
    """

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if value is None:
                raise ValueError(f"Field '{field.name}' is mandatory.")

    @classmethod
    def from_path(cls, file_path: Path) -> "ShelfConfig":
        """
        Unserialize a config from the given file.
        """
        content = file_path.read_text(encoding="utf-8")
        asdict = {}
        for index, line in enumerate(content.splitlines()):
            try:
                key, value = line.split(":", 1)
                key = key.strip(" ")
                value = value.strip(" ")
                value = ast.literal_eval(value)
                asdict[key] = value
            except Exception as error:
                raise ValueError(f"Invalid line {index} ({line}): {error}")

        ctx = f"(shelf config file '{file_path}')"
        for field in dataclasses.fields(cls):
            key = field.name
            field_required = field.metadata["required"]
            if key not in asdict:
                if field_required:
                    raise KeyError(f"Mandatory field '{key}' is not defined {ctx}.")
                continue
            value = asdict[key]
            if not isinstance(value, field.metadata["type"]):
                raise TypeError(
                    f"Field '{key}' must be of type '{field.type}', got '{type(value)}' {ctx}."
                )

        return cls(**asdict)


@dataclasses.dataclass
class ShelfResource:
    url_path: str
    config: ShelfConfig
    children: list[PageResource]

    def is_index(self, page: PageResource) -> bool:
        """
        Return True if the page is to be used as the index page of the self it belongs to.
        """
        if page not in self.children:
            return False
        return f"{self.url_path}/{page.slug}" == page.url_path
