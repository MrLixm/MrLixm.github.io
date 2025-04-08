import dataclasses
import datetime
import logging
import os
from pathlib import Path

import jinja2

from lxmsite import SiteConfig
from lxmsite import PageResource
from ._utils import slugify

LOGGER = logging.getLogger(__name__)


def mkpagerel(path: str, page_path: str) -> str:
    """
    Convert a site-root-relative path, to a path relative to the given page.
    """
    root_path: Path = Path("placeholder")
    pageabs = root_path.joinpath(page_path).resolve()
    pathabs = root_path.joinpath(path).resolve()
    return Path(os.path.relpath(pathabs, start=pageabs.parent)).as_posix()


def mksiterel(path: str, page_path: str) -> str:
    """
    Convert a page-relative path to a path relative to the site root.
    """
    root_path: Path = Path("placeholder")
    pageabs = root_path.joinpath(page_path).resolve()
    pathabs = pageabs.parent.joinpath(path).resolve()
    return Path(os.path.relpath(pathabs, start=root_path)).as_posix()


def get_jinja_env(
    site_config: SiteConfig,
    page_rel_url: str,
) -> jinja2.Environment:

    def _mksiteabs_(_path_: str) -> str:
        """
        Convert the given site-relative url to absolute.
        """
        return f"{site_config.SITE_URL}/{_path_}"

    def _mksiterel_(_path_: str) -> str:
        return mksiterel(_path_, page_rel_url)

    def _mkpagerel_(_path_: str) -> str:
        return mkpagerel(_path_, page_rel_url)

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
    }
    content = template.render(**attributes)
    return content
