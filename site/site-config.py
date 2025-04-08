import io
from pathlib import Path

import lxmsite

THISDIR = Path(__file__).parent

SRC_ROOT: Path = THISDIR / "src"
DST_ROOT: Path | None = THISDIR / ".build"
TEMPLATES_ROOT: Path = SRC_ROOT

DEFAULT_PAGE_ICON: str = ".static/icons/logo-lixm.svg"
DEFAULT_STYLESHEETS: list[str] = [".static/main.css"]

# mapping of "nav pretty-name": "relative url path"
HEADER_NAV = {
    "Work": "work/index.html",
    "Blog": "blog/index.html",
    "Contact": "contact.html",
}

# determine which page metadata is collected to generate procedurals pages.
# those names become reserved in the shelf namespace and the root namespace.
# ex: 'categories' for the page './blog/hello.rst' will reserve './blog/categories' and './categories'
SHELF_LABELS = [
    lxmsite.ShelfLabel.from_name("authors"),
    lxmsite.ShelfLabel.from_name("categories"),
    lxmsite.ShelfLabel.from_name("tags"),
]


# TODO
REDIRECTS = {}

# used for making some relative urls absolute
SITE_URL = "https://mrlixm.github.io"
# affect how the site is built (mainly urls), i.e. local preview or final web publish.
PUBLISH_MODE = False


# from https://github.com/getpelican/pelican/blob/main/pelican/readers.py#L253
DEFAULT_DOCUTILS_SETTINGS = {
    "initial_header_level": "2",
    "syntax_highlight": "short",
    "language_code": "en",
    "halt_level": 2,
    "traceback": True,
    "warning_stream": io.StringIO(),
    "embed_stylesheet": False,
    "input_encoding": "utf-8",
}
