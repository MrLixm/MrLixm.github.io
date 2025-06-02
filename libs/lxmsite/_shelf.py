import ast
import dataclasses
import logging
from pathlib import Path
from typing import Any

from lxmsite import PageResource
from lxmsite._utils import mkpagerel

LOGGER = logging.getLogger(__name__)


def mkfield(metadata):
    return dataclasses.field(metadata=metadata)


@dataclasses.dataclass
class ShelfConfig:
    """
    Defines how to handle the pages belonging to a specific shelf.
    """

    ignored_pages: list[str] = dataclasses.field(
        default_factory=list,
        metadata={"type": list, "required": False},
    )
    """
    list of page filenames that will be included in the final site but are not part of the procedural "browser" pages.
    """

    disable_rss: bool = dataclasses.field(
        default=False,
        metadata={"type": bool, "required": False},
    )

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
            if not line:
                continue
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
    """
    path to the shelf directory, relative to site root
    """
    config: ShelfConfig
    children: list[PageResource]

    def iterate(self, ignore_index: bool = False):
        """
        Return only children that are supposed to be parsed.

        Use ``self.children`` to return all children.
        """
        for child in self.children:
            if self.is_ignored(child):
                continue
            if ignore_index and self.is_index(child):
                continue
            if child.status == child.status.unlisted:
                continue
            yield child

    @property
    def name(self):
        return Path(self.url_path).name

    @property
    def rss_feed_url(self) -> str:
        """
        Get the url to the rss feed file; relative to the site root.

        Note that the file may not exists.
        """
        # TODO expose the filename as configurable in the ShelfConfig
        return f"{self.url_path}/{self.name}.rss.xml"

    def get_index_page(self) -> PageResource | None:
        """
        Get the index page for this shelf, if it has been added as children.
        """
        try:
            return next(page for page in self.children if self.is_index(page))
        except StopIteration:
            return None

    def is_index(self, page: PageResource) -> bool:
        """
        Return True if the page is to be used as the index page of the self it belongs to.
        """
        if page not in self.children:
            return False
        return f"{self.url_path}/index.html" == page.url_path

    def is_ignored(self, page: PageResource) -> bool:
        """
        Determine if the given page is marked as ignored in the shelf config.
        """
        page_rel_url = mkpagerel(page.url_path, self.url_path + "/.shelf")
        return page_rel_url in self.config.ignored_pages

    def iterate_children_by_last_created(
        self,
        reverse: bool = False,
        ignore_index: bool = False,
    ):
        """
        Args:
            reverse: if True return last created first, and oldest last.
            ignore_index: if True do not yield the page that is index of the shelf
        """

        def _sorter(page: PageResource) -> str:
            if not page.metadata.date_created:
                return ""
            return page.metadata.date_created.isoformat()

        for child in sorted(
            self.iterate(ignore_index=ignore_index),
            key=_sorter,
            reverse=reverse,
        ):
            yield child

    def group_children_by_metadata(
        self,
        metadata_name: str,
        ignore_index: bool = False,
    ) -> dict[Any, list[PageResource]]:
        """
        Return children grouped by their value for the given metadata.

        Args:
            metadata_name: valid name of a metadata for pages.
            ignore_index: if True do not yield the page that is index of the shelf

        Returns:
            mapping of metadata value: list of pages
        """
        groups = {}
        for child in self.iterate(ignore_index=ignore_index):
            value = child.metadata.get(metadata_name)
            groups.setdefault(value, []).append(child)

        return groups


@dataclasses.dataclass
class ShelfLibrary:
    """
    A collection of shelves.

    Easier to manipulate from jinja templates than a vanilla list.
    """

    shelves: list[ShelfResource]

    def __iter__(self):
        for shelf in self.shelves:
            yield shelf

    def get(self, shelf_name: str) -> ShelfResource | None:
        """
        Get the shelf with the given name.
        """
        for shelf in self.shelves:
            if shelf.name == shelf_name:
                return shelf
        return None
