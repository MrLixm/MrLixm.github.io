import io
from pathlib import Path

import lxmsite

THISDIR = Path(__file__).parent

SRC_ROOT: Path = THISDIR / "src"
TEMPLATES_ROOT: Path = THISDIR / "templates"


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
