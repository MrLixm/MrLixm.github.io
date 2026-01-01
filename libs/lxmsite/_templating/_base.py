import logging
from pathlib import Path

import jinja2

from lxmsite._utils import slugify
from lxmsite._utils import mkpagerel
from lxmsite._utils import mksiterel


LOGGER = logging.getLogger(__name__)


def get_jinja_env(
    page_rel_url: str,
    site_url: str,
    publish_mode: bool,
    templates_root: Path,
) -> jinja2.Environment:

    def _mksiteabs_(_path_: str) -> str:
        """
        Convert the given site-relative url to absolute.
        """
        if _path_.startswith("http"):
            # already absolute path
            return _path_
        return f"{site_url}/{_path_.lstrip('/')}"

    def _mksiterel_(_path_: str, _page_path_=page_rel_url) -> str:
        if _path_.startswith("/"):
            # already relative to site root
            return _path_
        if _path_.startswith("http"):
            # cannot make relative, absolute path
            return _path_
        return mksiterel(_path_, _page_path_)

    def _mkpagerel_(_path_: str, _page_path_=page_rel_url) -> str:
        if _path_.startswith("http"):
            # cannot make relative, absolute path
            return _path_
        return mkpagerel(_path_, _page_path_)

    def _format_link_(_link_: str) -> str:
        """
        Make site cross-linking prettier by removing file format suffix on publish.
        """
        # XXX: this works on GitHub pages !!! no guarantee for other host
        if publish_mode:
            if _link_.endswith("index.html"):
                formatted = _link_.removesuffix("index.html")
                return formatted if formatted else "."
            return _link_.removesuffix(".html")
        return _link_

    jinja_env = jinja2.Environment(
        undefined=jinja2.StrictUndefined,
        loader=jinja2.FileSystemLoader(templates_root),
    )
    jinja_env.filters["slugify"] = slugify
    jinja_env.filters["mksiteabs"] = _mksiteabs_
    jinja_env.filters["mksiterel"] = _mksiterel_
    jinja_env.filters["mkpagerel"] = _mkpagerel_
    jinja_env.filters["prettylink"] = _format_link_
    return jinja_env
