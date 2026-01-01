import datetime
import logging
from pathlib import Path

from lxmsite import SiteConfig
from lxmsite import mdlib
from lxmsite import PageResource
from lxmsite import PageMetadata
from lxmsite import PageStatus
from ._utils import mkpagerel


LOGGER = logging.getLogger(__name__)


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

    md_doc = file_path.read_text(encoding="utf-8")
    parsed = mdlib.read_markdown(
        source=md_doc,
        paths_root=file_path.parent,
        extension_settings=site_config.DEFAULT_MARKDOWN_SETTINGS,
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
