import dataclasses
import datetime
import logging

import jinja2

from lxmsite import SiteConfig
from lxmsite import PageResource
from lxmsite import ShelfResource
from lxmsite import ShelfLibrary
from ._utils import slugify
from ._utils import mkpagerel
from ._utils import mksiterel

LOGGER = logging.getLogger(__name__)


def get_jinja_env(
    site_config: SiteConfig,
    page_rel_url: str,
) -> jinja2.Environment:

    def _mksiteabs_(_path_: str) -> str:
        """
        Convert the given site-relative url to absolute.
        """
        if _path_.startswith("http"):
            # already absolute path
            return _path_
        return f"{site_config.SITE_URL}/{_path_.lstrip('/')}"

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
        if site_config.PUBLISH_MODE:
            if _link_.endswith("index.html"):
                formatted = _link_.removesuffix("index.html")
                return formatted if formatted else "."
            return _link_.removesuffix(".html")
        return _link_

    jinja_env = jinja2.Environment(
        undefined=jinja2.StrictUndefined,
        loader=jinja2.FileSystemLoader(site_config.TEMPLATES_ROOT),
    )
    jinja_env.filters["slugify"] = slugify
    jinja_env.filters["mksiteabs"] = _mksiteabs_
    jinja_env.filters["mksiterel"] = _mksiterel_
    jinja_env.filters["mkpagerel"] = _mkpagerel_
    jinja_env.filters["prettylink"] = _format_link_
    return jinja_env


@dataclasses.dataclass
class SiteGlobalContext:
    build_time: datetime.datetime
    last_commit: str


def render_page(
    page: PageResource,
    template_name: str,
    site_config: SiteConfig,
    context: SiteGlobalContext,
    shelf: ShelfResource | None,
    shelf_library: ShelfLibrary,
) -> str:
    jinja_env = get_jinja_env(
        site_config=site_config,
        page_rel_url=page.url_path,
    )
    template = jinja_env.get_template(template_name)
    attributes = {
        "Page": page,
        "Config": site_config,
        "Context": context,
        "Shelf": shelf,
        "ShelfLibrary": shelf_library,
    }
    content = template.render(**attributes)
    return content
