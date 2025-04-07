import dataclasses
import logging
from pathlib import Path

from lxmsite import SiteConfig
from lxmsite import ShelfLabel
from . import rstlib

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PageResource:
    """
    A page is a rst document that will be translated to a single web page.

    A page may or may not belong to a shelf.
    """

    title: str
    metadata: dict[str, str]
    labels: dict[ShelfLabel, str]
    file_path: Path
    html_content: str
    html_template: str | None


def read_page(
    file_path: Path,
    site_config: SiteConfig,
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

    return PageResource(
        title=title,
        metadata=metadata,
        file_path=file_path,
        html_content=content,
        labels=page_labels,
        html_template=template,
    )


def render_page(page: PageResource, site_config: SiteConfig) -> str:
    # TODO
    return page.html_content
