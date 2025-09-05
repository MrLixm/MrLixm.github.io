import io
from pathlib import Path

import lxmsite

THISDIR = Path(__file__).parent

SRC_ROOT: Path = THISDIR / "src"
DST_ROOT: Path | None = THISDIR / ".build"
TEMPLATES_ROOT: Path = SRC_ROOT

DEFAULT_PAGE_ICON: str = ".static/icons/logo-lixm.svg"

# mapping of "nav pretty-name": "relative url path"
HEADER_NAV = {
    "Work": "work/index.html",
    "Blog": "blog/index.html",
    "Resources": "resources/index.html",
    "Contact": "contact.html",
}

# mapping of "relative page path": "target redirection url"
REDIRECTIONS = {
    "assets/chkpad1/index.html": "resources/chkpad1/index.html",
    "assets/chkpad2red/index.html": "resources/chkpad2red/index.html",
    "pages/contact/index.html": "contact.html",
}
# jinja template path to use to render redirections page (relative to TEMPLATES_ROOT)
REDIRECTIONS_TEMPLATE = ".redirect.html"

# jinja template path to use to render rss feeds generated from shelves
RSS_FEED_TEMPLATE = ".rss.xml.jinja2"

# used for making some relative urls absolute
SITE_URL = "https://liamcollod.xyz"
# affect how the site is built (mainly urls), i.e. local preview or final web publish.
PUBLISH_MODE = False


# from https://github.com/getpelican/pelican/blob/main/pelican/readers.py#L253
DEFAULT_MARKDOWN_SETTINGS = {
    "emojis": {
        "directory": SRC_ROOT / ".static" / "images" / "emojis",
    },
    "patcher": {
        "table_classes": ["inline"],
        "code_classes": ["inline"],
        "link_headings": True,
    },
    "pymdownx.highlight": {
        "linenums_style": "pymdownx-inline",
    },
    "image_gallery": {
        "default_template": SRC_ROOT / ".image-gallery.html.jinja2",
    },
}

PAGEFIND_CONFIG = {
    "element": "#search",
    "showSubResults": True,
    "showImages": False,
}
