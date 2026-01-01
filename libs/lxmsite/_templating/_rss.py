from lxmsite import ShelfResource
from lxmsite import SiteConfig
from lxmsite._templating import get_jinja_env


def render_rss_feed(
    shelf: ShelfResource,
    template_name: str,
    site_config: SiteConfig,
) -> str:
    """
    Generate a rss feed from a shelf.

    Args:
        shelf: shelf the feed is generated from
        template_name: jinja template path relative to template root
        site_config:

    Returns:
        rendered template which can be writen to disk
    """
    jinja_env = get_jinja_env(
        page_rel_url=shelf.rss_feed_url,
        site_url=site_config.SITE_URL,
        publish_mode=site_config.PUBLISH_MODE,
        templates_root=site_config.TEMPLATES_ROOT,
    )
    template = jinja_env.get_template(template_name)
    attributes = {
        "URL_PATH": shelf.rss_feed_url,
        "Config": site_config,
        "Shelf": shelf,
    }
    content = template.render(**attributes)
    return content
