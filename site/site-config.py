import io
from pathlib import Path

import lxmsite

THISDIR = Path(__file__).parent

SRC_ROOT: Path = THISDIR / "src"
DST_ROOT: Path | None = THISDIR / ".build"
TEMPLATES_ROOT: Path = SRC_ROOT

DEFAULT_PAGE_ICON: str = ".static/icons/logo-lixm.svg"
DEFAULT_STYLESHEETS: list[str] = [
    ".static/main.css",
    ".static/pygments.onedark.css",
]

# mapping of "nav pretty-name": "relative url path"
HEADER_NAV = {
    "Work": "work/index.html",
    "Blog": "blog/index.html",
    "Resources": "resources/index.html",
    "Contact": "contact.html",
}


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
    "table_style": "inline",
}
