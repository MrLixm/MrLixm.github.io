import dataclasses
import logging
from pathlib import Path

from lxmsite import ShelfLabel
from lxmsite import SiteConfig
from . import rstlib
from ._utils import mkpagerel

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PageMetadata:
    """
    Additional metadata about the page, bringing extra context to its content.

    This is mostly use in the htlm site head. See https://ogp.me/
    """

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta/name
    authors: list[str]
    keywords: list[str]

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/lang
    # https://www.w3.org/International/articles/language-tags/
    language: str

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel#icon
    icon: str
    """
    link to an icon file, relative to the page it was extracted from.
    """

    title: str  # https://ogp.me/#metadata
    type: str  # https://ogp.me/#types
    image: str  # https://ogp.me/#metadata
    """
    link to an image file, relative to the page it was extracted from.
    """

    description: str  # https://ogp.me/#optional

    # anything else that is non-standardized
    date_created: str  # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#http%3a%2f%2fpurl.org%2fdc%2felements%2f1.1%2fdate
    date_modified: str  # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#http%3a%2f%2fpurl.org%2fdc%2felements%2f1.1%2fdate
    extras: dict[str, str]


@dataclasses.dataclass
class PageResource:
    """
    A page is a rst document that will be translated to a single web page.

    A page may be child of zero or one shelf.
    """

    title: str
    metadata: PageMetadata
    labels: dict[ShelfLabel, str]
    url_path: str
    """
    relative to the site root
    """
    html_content: str
    html_template: str | None
    stylesheets: list[str]
    """
    collections of link to stylesheets file, relative to the page
    """

    def __str__(self):
        return f"<{self.url_path} ({self.title})>"

    @property
    def slug(self) -> str:
        """
        The last part of the url path (the page "url name")
        """
        return self.url_path.split("/")[-1]


def read_page(
    file_path: Path,
    site_config: SiteConfig,
) -> PageResource:
    publisher = rstlib.read_rst(
        file_path,
        settings=site_config.DEFAULT_DOCUTILS_SETTINGS,
    )
    parts = publisher.writer.parts
    content = str(parts.get("body"))
    title = str(parts.get("title"))

    src_root = site_config.SRC_ROOT
    url_path: Path = file_path.relative_to(src_root)
    url_path: Path = url_path.with_suffix(".html")
    url_path: str = url_path.as_posix()

    raw_metadata = rstlib.parse_metadata(publisher.document)

    page_labels: dict[ShelfLabel, str] = {}
    for label in site_config.SHELF_LABELS:
        page_label = raw_metadata.pop(label.rst_key, None)
        if not page_label:
            continue
        page_labels[label] = page_label

    template = raw_metadata.pop("template", None)

    stylesheets: list[str] = site_config.DEFAULT_STYLESHEETS
    stylesheets: list[str] = [mkpagerel(path, url_path) for path in stylesheets]
    meta_styles: str = raw_metadata.pop("stylesheets", "")
    if stylesheets_add := meta_styles.startswith("+"):
        meta_styles = meta_styles[1:]
    meta_styles: list[str] = [k.strip() for k in meta_styles.split(",") if k.strip()]
    if meta_styles and stylesheets_add:
        stylesheets = stylesheets + meta_styles
    elif meta_styles:
        stylesheets = meta_styles

    image_path = raw_metadata.pop("image", "")

    keywords = [k.strip() for k in raw_metadata.pop("tags", "").split(",") if k]

    icon = raw_metadata.pop("icon", "")
    icon = icon or mkpagerel(site_config.DEFAULT_PAGE_ICON, url_path)

    metadata = PageMetadata(
        authors=raw_metadata.pop("authors", []),
        keywords=keywords,
        language=raw_metadata.pop("language", "en"),
        icon=icon,
        title=raw_metadata.pop("title", title),
        type=raw_metadata.pop("type", "website"),
        image=image_path,
        description=raw_metadata.pop("description", ""),
        date_created=raw_metadata.pop("date-created", ""),
        date_modified=raw_metadata.pop("date-modified", ""),
        extras=raw_metadata,
    )

    return PageResource(
        title=title,
        metadata=metadata,
        labels=page_labels,
        url_path=url_path,
        html_content=content,
        html_template=template,
        stylesheets=stylesheets,
    )
