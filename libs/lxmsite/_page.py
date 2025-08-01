import dataclasses
import datetime
import enum
import logging
from pathlib import Path
from typing import Any

from lxmsite import SiteConfig
from . import mdlib
from ._utils import mkpagerel

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PageMetadata:
    """
    Additional metadata about the page, bringing extra context to its content.

    This is mostly use in the htlm site head. See https://ogp.me/
    """

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta/name
    authors: list[str] = dataclasses.field(default_factory=list)
    keywords: list[str] = dataclasses.field(default_factory=list)

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/lang
    # https://www.w3.org/International/articles/language-tags/
    language: str = "en"

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel#icon
    icon: str = ""
    """
    link to an icon file, relative to the page it was extracted from.
    """

    title: str = ""  # https://ogp.me/#metadata
    type: str = ""  # https://ogp.me/#types
    image: str = ""  # https://ogp.me/#metadata
    """
    link to an image file, relative to the page it was extracted from.
    """
    image_alt: str = ""

    description: str = ""  # https://ogp.me/#optional

    # // anything else that is non-standardized

    # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#http%3a%2f%2fpurl.org%2fdc%2felements%2f1.1%2fdate
    date_created: datetime.datetime | None = None
    # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#http%3a%2f%2fpurl.org%2fdc%2felements%2f1.1%2fdate
    date_modified: datetime.datetime | None = None
    extras: dict[str, str] = dataclasses.field(default_factory=dict)

    def get(self, name: str) -> Any:
        """
        Get a metadata based on its name, no matter if it's a known attribute or an extra.
        """
        if name in vars(self):
            return getattr(self, name)
        if name in self.extras:
            return self.extras[name]

        available = list(vars(self)) + list(self.extras)
        raise ValueError(
            f"No metadata with name '{name}' found; "
            f"must be one of {','.join(available)}"
        )


class PageStatus(enum.Enum):
    published = enum.auto()
    unlisted = enum.auto()
    """
    page is built and published but not listed in shelf
    """


@dataclasses.dataclass
class PageResource:
    """
    A page is a markdown document that will be translated to a single web page.

    A page may be child of zero or one shelf.
    """

    title: str
    metadata: PageMetadata
    url_path: str
    """
    relative to the site root
    """
    html_content: str
    html_template: str | None = None
    """
    path of the template to use relative to the config TEMPLATE_ROOT
    """

    status: PageStatus = PageStatus.published

    stylesheets: list[str] = dataclasses.field(default_factory=list)
    """
    collections of link to stylesheets file, relative to the site root
    """

    def __str__(self):
        return f"<{self.url_path} ({self.title})>"

    @property
    def slug(self) -> str:
        """
        The last part of the url path (the page "url name")
        """
        return self.url_path.split("/")[-1]


def unserialize_stylesheets(serialized: str) -> list[str]:
    if serialized:
        serialized = serialized.replace("\n", "")
        return [
            stylesheet.strip()
            for stylesheet in serialized.split(",")
            if stylesheet.strip()
        ]
    return []


def read_page(
    file_path: Path,
    site_config: SiteConfig,
    default_metadata: dict[str, str],
) -> PageResource:

    parsed = mdlib.read_markdown(
        file_path=file_path,
        settings=site_config.DEFAULT_MARKDOWN_SETTINGS,
    )
    title = parsed.title
    content = parsed.html
    content = '<div class="src-md">\n' + content + "\n</div>"

    src_root = site_config.SRC_ROOT
    url_path: Path = file_path.relative_to(src_root)
    url_path: Path = url_path.with_suffix(".html")
    url_path: str = url_path.as_posix()

    raw_metadata = parsed.metadata
    src_metadata = default_metadata.copy()
    default_stylesheets = unserialize_stylesheets(src_metadata.pop("stylesheets", ""))
    default_stylesheets = [
        path if path.startswith("http") else mkpagerel(path, url_path)
        for path in default_stylesheets
    ]

    # TODO maybe add a system of tokens like every value that starts with "//" get
    #   expanded with mkpagerel. Instead of hardcoding keys that need expansion.
    if "image" in src_metadata:
        src_metadata["image"] = mkpagerel(src_metadata["image"], url_path)

    # page-defined metadata take priority over provided default metadata
    src_metadata.update(raw_metadata)

    template = src_metadata.pop("template", None)

    raw_stylesheets: str = src_metadata.pop("stylesheets", "")
    if stylesheets_add := raw_stylesheets.startswith("+"):
        raw_stylesheets = raw_stylesheets[1:]
    stylesheets: list[str] = unserialize_stylesheets(raw_stylesheets)
    if not stylesheets:
        stylesheets = default_stylesheets
    elif stylesheets_add:
        stylesheets = default_stylesheets + stylesheets

    image_path = src_metadata.pop("image", "")

    keywords = [k.strip() for k in src_metadata.pop("tags", "").split(",") if k]

    icon = src_metadata.pop("icon", "")
    icon = icon or mkpagerel(site_config.DEFAULT_PAGE_ICON, url_path)

    authors = src_metadata.pop("authors", "").split(",")
    authors = authors if authors[0] else []

    date_created = src_metadata.pop("date-created", None)
    if date_created:
        date_created = datetime.datetime.fromisoformat(date_created)
    date_modified = src_metadata.pop("date-modified", None)
    if date_modified:
        date_modified = datetime.datetime.fromisoformat(date_modified)

    metadata = PageMetadata(
        authors=authors,
        keywords=keywords,
        language=src_metadata.pop("language", "en"),
        icon=icon,
        title=src_metadata.pop("title", title),
        type=src_metadata.pop("type", "website"),
        image=image_path,
        image_alt=src_metadata.pop("image-alt", ""),
        description=src_metadata.pop("description", ""),
        date_created=date_created,
        date_modified=date_modified,
        extras=src_metadata,
    )

    status = raw_metadata.pop("status", "")
    if status:
        status = getattr(PageStatus, status, PageStatus.published)
    else:
        status = PageStatus.published

    return PageResource(
        title=title,
        metadata=metadata,
        status=status,
        url_path=url_path,
        html_content=content,
        html_template=template,
        stylesheets=stylesheets,
    )
