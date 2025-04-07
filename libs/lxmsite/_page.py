import dataclasses
import logging
from pathlib import Path

from lxmsite import SiteConfig
from lxmsite import ShelfLabel
from lxmsite import ShelfResource
from . import rstlib

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PageResource:
    """
    A page is a rst document that will be translated to a single web page.

    A page may be child of zero or one shelf.
    """

    title: str
    metadata: dict[str, str]
    labels: dict[ShelfLabel, str]
    shelf: ShelfResource | None
    url_path: str
    html_content: str
    html_template: str | None

    def __str__(self):
        return f"<{self.url_path} ({self.title})>"


def read_page(
    file_path: Path,
    site_config: SiteConfig,
    parent_shelf: ShelfResource | None,
) -> PageResource:
    publisher = rstlib.read_rst(
        file_path,
        settings=site_config.DEFAULT_DOCUTILS_SETTINGS,
    )
    parts = publisher.writer.parts
    content = parts.get("body")
    title = parts.get("title")
    metadata = rstlib.parse_metadata(publisher.document)

    page_labels = {}
    for label in site_config.SHELF_LABELS:
        page_label = metadata.pop(label.rst_key, None)
        if not page_label:
            continue
        page_labels[label] = page_label

    template = metadata.pop("template", None)
    if parent_shelf and not template:
        template = parent_shelf.config.default_template

    url_path: Path = file_path.relative_to(site_config.SRC_ROOT)
    url_path: Path = url_path.with_suffix(".html")
    url_path: str = url_path.as_posix()

    return PageResource(
        title=title,
        metadata=metadata,
        labels=page_labels,
        shelf=parent_shelf,
        url_path=url_path,
        html_content=content,
        html_template=template,
    )
