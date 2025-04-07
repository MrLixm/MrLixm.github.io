import datetime
import logging
import shutil
from pathlib import Path

import lxmsite
from lxmsite import ShelfResource

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


def get_context() -> lxmsite.SiteGlobalContext:
    return lxmsite.SiteGlobalContext(
        build_time=datetime.datetime.now(),
        last_commit="TODO",
    )


def fmterr(ctx: str, error: Exception):
    return f"❌ ERROR while building {ctx}: {type(error).__name__}: {error}"


def build_site(config: lxmsite.SiteConfig) -> list[Exception]:
    """

    Args:
        config: config driving the build process.

    Returns:
        collection of errors if any.
    """
    errors: list[Exception] = []

    src_root = config.SRC_ROOT
    dst_root = config.DST_ROOT
    build_context = get_context()

    site_files = lxmsite.collect_site_files(src_root)
    LOGGER.debug(f"collected {len(site_files):0>3} site files")

    # /// collect shelves ///
    # -----------------------
    shelf_files = lxmsite.collect_shelves(site_files)
    # filter out shelf files we already collected
    site_files = [path for path in site_files if path not in shelf_files]
    shelves: list[ShelfResource] = []
    site_file_by_shelves: dict[Path, ShelfResource] = {}
    for shelf_file, children in shelf_files.items():
        LOGGER.debug(f"reading shelf config '{shelf_file}'")
        try:
            shelf_config = lxmsite.ShelfConfig.from_path(shelf_file)
        except Exception as error:
            LOGGER.error(fmterr(str(shelf_file), error))
            errors.append(error)
            continue

        shelf = ShelfResource(
            config=shelf_config,
            children=children,
        )
        shelves.append(shelf)
        # create a cache that indicate which shelf each site file belongs to.
        #   - a path may only belong to one shelf at a time, so order of iteration matters
        #   - not all site files may belong to a shelf so some might be missing from `site_file_by_shelves`
        for child in children:
            site_file_by_shelves[child] = shelf

    # /// build pages ///
    # -------------------
    for src_path in site_files:

        # TODO verify nested shelves support and add it or not
        parent_shelf: ShelfResource | None = site_file_by_shelves.get(src_path)

        if src_path.suffix == ".rst":
            LOGGER.debug(f"┌ reading page '{src_path}'")
            try:
                page = lxmsite.read_page(
                    src_path,
                    site_config=config,
                    parent_shelf=parent_shelf,
                )
            except Exception as error:
                LOGGER.error(f"{fmterr(str(src_path), error)}")
                errors.append(error)
                continue

            if len(page.labels) != len(config.SHELF_LABELS):
                expected = [label.rst_key for label in config.SHELF_LABELS]
                actual = [label.rst_key for label in page.labels.keys()]
                LOGGER.warning(
                    f"| page '{page.url_path}' have missing labels in its metadata: "
                    f"expected {expected}; got {actual}."
                )

            template = page.html_template
            if not template:
                error = ValueError(f"No template specified on page '{page.url_path}'.")
                LOGGER.error(fmterr(str(page), error))
                errors.append(error)
                continue

            LOGGER.debug(f"| rendering page with template '{template}'")
            try:
                page_html = lxmsite.render_page(
                    page=page,
                    template_name=template,
                    site_config=config,
                    context=build_context,
                )
            except Exception as error:
                LOGGER.error(f"└ {fmterr(str(page), error)}")
                errors.append(error)
                continue

            dst_path = Path(dst_root, page.url_path).resolve()
            mkdir(dst_path.parent)
            LOGGER.debug(f"└ writing page '{dst_path}'")
            dst_path.write_text(page_html)

        else:
            # this is a static resource
            dst_path = Path(dst_root, src_path.relative_to(src_root)).resolve()
            mkdir(dst_path.parent)
            LOGGER.debug(f"shutil.copy({src_path}, {dst_path})")
            shutil.copy(src_path, dst_path)

    return errors
