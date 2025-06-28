import dataclasses
import logging

import pytest

from lxmsite import ShelfConfig, read_page, ShelfResource

LOGGER = logging.getLogger(__name__)


def test__ShelfConfig__from_path(tmp_path):
    content = (
        "\nignored_pages : ['foo.html', 'hello/world.html']\ndisable_rss: True\n\n"
    )
    config_path = tmp_path / "1.shelf"
    config_path.write_text(content)

    config = ShelfConfig.from_path(config_path)
    assert config.ignored_pages == ["foo.html", "hello/world.html"]
    assert config.disable_rss is True

    content = "ignored_pages = ['foo.html', 'hello/world.html']"
    config_path = tmp_path / "2.shelf"
    config_path.write_text(content)
    with pytest.raises(ValueError):
        ShelfConfig.from_path(config_path)

    content = "ignored_pages: 'foo.html'"
    config_path = tmp_path / "3.shelf"
    config_path.write_text(content)
    with pytest.raises(TypeError):
        ShelfConfig.from_path(config_path)


def test__Shelf__repo1(resources_dir, default_site_config):
    root_dir = resources_dir / "repo1"
    config_path = root_dir / ".shelf"
    config = ShelfConfig.from_path(config_path)
    default_site_config.SRC_ROOT = resources_dir

    pages = [
        read_page(file_path=page, site_config=default_site_config, default_metadata={})
        for page in root_dir.glob("**/*.md")
    ]
    assert len(pages) == 5
    shelf_url = root_dir.name
    shelf = ShelfResource(shelf_url, config, pages)

    index_page = shelf.get_index_page()
    assert index_page
    assert index_page.url_path == "repo1/index.html"
    assert index_page.title == "Home"
    assert index_page.html_content == (
        '<div class="src-md">\n<p>lorem ipsum something ...</p>\n</div>'
    )

    assert len(list(shelf.iterate())) == 4
    assert len(list(shelf.iterate(ignore_index=True))) == 3

    ignored = [p for p in shelf.children if shelf.is_ignored(p)]
    assert len(ignored) == 1
    assert ignored[0].title == "aside"

    by_date = list(shelf.iterate_children_by_last_created())
    assert len(by_date) == 4
    assert by_date[0].title == "Home"
    assert by_date[1].title == "post1"
    assert by_date[2].title == "post2"
    assert by_date[3].title == "post3"
