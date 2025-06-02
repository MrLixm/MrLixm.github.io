from pathlib import Path

import pytest

from lxmsite import SiteConfig

THISDIR = Path(__file__).parent


@pytest.fixture
def resources_dir() -> Path:
    return THISDIR / "resources"


@pytest.fixture
def default_site_config(tmp_path: Path) -> SiteConfig:
    return SiteConfig(
        SRC_ROOT=tmp_path / "src",
        DST_ROOT=tmp_path / "dst",
        TEMPLATES_ROOT=tmp_path / "templates",
        DEFAULT_DOCUTILS_SETTINGS={},
        SITE_URL="www.site.fr",
        PUBLISH_MODE=False,
        DEFAULT_PAGE_ICON="",
        DEFAULT_STYLESHEETS=[],
        HEADER_NAV={},
        REDIRECTIONS={},
        REDIRECTIONS_TEMPLATE="",
        RSS_FEED_TEMPLATE="",
    )
