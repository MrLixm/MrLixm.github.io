import ast
import dataclasses
import logging
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
    config: ShelfConfig
    children: list[Path]
    url_path: str
