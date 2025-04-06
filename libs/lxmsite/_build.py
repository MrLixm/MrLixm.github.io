import logging
import shutil
from pathlib import Path

import lxmsite

LOGGER = logging.getLogger(__name__)


def mkdir(dirpath: Path):
    """
    Recursively create the directories hierarchy for the given directory path.

    Used instead of mkdir(parent=true) just to get the LOGGER call for each directory created.
    """
    if dirpath.exists():
        return
    # make sure parents are created first
    if not dirpath.parent.exists():
        mkdir(dirpath.parent)
    LOGGER.debug(f"mkdir({dirpath})")
    dirpath.mkdir()


def build_site(
    build_dir: Path,
    config_path: Path,
):
    LOGGER.debug(f"reading site config '{config_path}'")
    config = lxmsite.SiteConfig.from_path(config_path)
    site_src_root = config.SRC_ROOT

    site_files = lxmsite.collect_site_files(site_src_root)
    shelf_files = lxmsite.collect_shelves(site_files)
    # filter out shelf files we already collected
    site_files = [path for path in site_files if path not in shelf_files]
    shelves = []
    for shelf_file, children in shelf_files.items():
        LOGGER.debug(f"reading shelf config '{shelf_file}'")
        shelf_config = lxmsite.ShelfConfig.from_path(shelf_file)
        shelf = lxmsite.ShelfResource(
            config=shelf_config,
            children=children,
        )
        shelves.append(shelf)
    # create a cache that indicate which shelf each site file belongs to.
    #   (not all site files may belong to a shelf so some might be missing)
    site_file_by_shelves = {path: shelf for shelf in shelves for path in shelf.children}

    for src_path in site_files:

        dst_path = Path(build_dir, src_path.relative_to(site_src_root)).resolve()
        # make sure the directory structure is created first
        mkdir(dst_path.parent)

        parent_shelf: lxmsite.ShelfResource | None = site_file_by_shelves.get(src_path)

        if src_path.suffix == ".rst":
            LOGGER.debug(f"┌ reading page '{src_path}'")
            page = lxmsite.read_page(src_path, site_config=config)

            if parent_shelf and not page.html_template:
                page.html_template = parent_shelf.config.default_template

            if len(page.labels) != len(config.SHELF_LABELS):
                expected = [label.rst_key for label in config.SHELF_LABELS]
                actual = [label.rst_key for label in page.labels.keys()]
                LOGGER.warning(
                    f"| page have missing labels in its metadata: "
                    f"expected {expected}; got {actual}."
                )

            LOGGER.debug("| rendering page ...")
            page_html = lxmsite.render_page(page, site_config=config)

            dst_path = dst_path.with_suffix(".html")
            LOGGER.debug(f"└ writing page '{dst_path}'")
            dst_path.write_text(page_html)

        else:
            # this is a static resource
            LOGGER.debug(f"shutil.copy({src_path}, {dst_path})")
            shutil.copy(src_path, dst_path)
