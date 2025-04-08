import dataclasses
import datetime
import logging

import jinja2

from lxmsite import SiteConfig
from lxmsite import PageResource
from ._utils import slugify

LOGGER = logging.getLogger(__name__)


def get_jinja_env(site_config: SiteConfig) -> jinja2.Environment:

    def expand_siteurl(path_: str) -> str:
        """
        Add the site url in front of the string
        """
        if site_config.PUBLISH_MODE:
            return f"{site_config.SITE_URL}/{path_}"
        return path_

    def mksiteabsurl(path_: str, page_url_: str) -> str:
        """
        Make a page-relative url, absolute to the site; only in publish mode.
        """
        if site_config.PUBLISH_MODE:
            page_abs = site_config.SRC_ROOT.joinpath(page_url_).parent
            path_abs = page_abs.joinpath(path_).resolve()
            path_abs = path_abs.relative_to(site_config.SRC_ROOT)
            return f"{site_config.SITE_URL}/{path_abs.as_posix()}"
        return path_

    def format_link(link_: str) -> str:
        """
        Make site cross-linking prettier by removing file format suffix on publish.
        """
        # XXX: this works on GitHub pages !!! no guarantee for other host
        if site_config.PUBLISH_MODE:
            if link_.endswith("index.html"):
                formatted = link_.removesuffix("index.html")
                return formatted if formatted else "."
            return link_.removesuffix(".html")
        return link_

    jinja_env = jinja2.Environment(
        undefined=jinja2.StrictUndefined,
        loader=jinja2.FileSystemLoader(site_config.TEMPLATES_ROOT),
    )
    jinja_env.filters["slugify"] = slugify
    jinja_env.filters["expand_siteurl"] = expand_siteurl
    jinja_env.filters["mksiteabsurl"] = mksiteabsurl
    jinja_env.filters["format_link"] = format_link
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
    jinja_env = get_jinja_env(site_config)
    template = jinja_env.get_template(template_name)
    attributes = {
        "Page": page,
        "Config": site_config,
        "Context": context,
        "URL_PATH": page.url_path,
    }
    content = template.render(**attributes)
    return content
