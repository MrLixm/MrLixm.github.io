import datetime
import logging
import os
import shutil
import traceback
from pathlib import Path

import lxmsite
from lxmsite import PageResource, MetaFileCollection
from lxmsite import ShelfResource
from lxmsite import SiteConfig

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


def is_file_newer(source: Path, target: Path):
    """
    Return true if 'source' exists and is more recently modified than
    'target', or if 'source' exists and 'target' doesn't.
    """
    if not source.exists():
        return False
    if not target.exists():
        return True

    from stat import ST_MTIME

    mtime_src = os.stat(source)[ST_MTIME]
    mtime_dst = os.stat(target)[ST_MTIME]
    return mtime_src > mtime_dst


def get_context() -> lxmsite.SiteGlobalContext:
    return lxmsite.SiteGlobalContext(
        build_time=datetime.datetime.now(),
        last_commit="TODO",
    )


def fmterr(ctx: str, error: Exception):
    # have shorter traceback by onling priting the 2 last frames
    last_frame = traceback.extract_tb(error.__traceback__, -2)
    frames_str = "\n".join(
        ["|  " + line for line in "".join(last_frame.format()).rstrip("\n").split("\n")]
    )
    return (
        f"❌ ERROR while building {ctx}: {type(error).__name__}: {error}\n{frames_str}"
    )


class ExceptionStack(Exception):
    def __init__(self, errors: list[Exception]):
        self.errors: list[Exception] = errors


def parse_pages(
    site_files: list[Path],
    site_config: SiteConfig,
    meta_collection: MetaFileCollection,
) -> tuple[dict[Path, PageResource], list[Path]]:
    """
    Convert site file structure to page objects and find additional static files.
    """
    errors: list[Exception] = []
    pages: dict[Path, PageResource] = {}
    static_paths: list[Path] = []

    for src_path in site_files:
        if src_path.suffix == ".rst":
            # retrieve default metadata for the page
            default_meta = meta_collection.get_path_meta(src_path)

            LOGGER.debug(f"reading page '{src_path}'")
            LOGGER.debug(f"└ default_meta={default_meta}")
            try:
                page = lxmsite.read_page(
                    file_path=src_path,
                    site_config=site_config,
                    default_metadata=default_meta,
                )
            except Exception as error:
                LOGGER.error(f"{fmterr(str(src_path), error)}")
                errors.append(error)
                continue
            pages[src_path] = page

        else:
            static_paths.append(src_path)

    if errors:
        raise ExceptionStack(errors)

    return pages, static_paths


def parse_shelves(
    src_root: Path,
    shelf_files: dict[Path, list[Path]],
    pages: dict[Path, PageResource],
) -> tuple[list[ShelfResource], dict[Path, ShelfResource]]:
    """
    Convert shelf file structure to Shelf objects.
    """
    errors: list[Exception] = []
    shelves: list[ShelfResource] = []
    page_by_shelves: dict[Path, ShelfResource] = {}

    for shelf_file, child_paths in shelf_files.items():
        LOGGER.debug(f"reading shelf config '{shelf_file}'")
        try:
            shelf_config = lxmsite.ShelfConfig.from_path(shelf_file)
        except Exception as error:
            LOGGER.error(fmterr(str(shelf_file), error))
            errors.append(error)
            continue

        children: list[PageResource] = [pages.get(path) for path in child_paths]
        children = list(filter(None, children))
        shelf = ShelfResource(
            config=shelf_config,
            children=children,
            url_path=shelf_file.parent.relative_to(src_root).as_posix(),
        )
        shelves.append(shelf)
        # create a cache that indicate which shelf each page belongs to.
        #   - a page may only belong to one shelf at a time, so order of iteration matters
        #   - not all page may belong to a shelf so some might be missing from `page_by_shelves`
        for page_path in child_paths:
            page_by_shelves[page_path] = shelf

    if errors:
        raise ExceptionStack(errors)

    return shelves, page_by_shelves


def build_page(
    page: PageResource,
    shelf: ShelfResource | None,
    dst_root: Path,
    site_config: SiteConfig,
    build_context: lxmsite.SiteGlobalContext,
) -> Path:
    """
    Build the html page on disk, out of the given page resource.

    Args:
        page: the page resource to build.
        shelf: optional parent shelf the page belongs to.
        dst_root: root directory where the file can be found.
        site_config: global site configuration.
        build_context: metadata for the build process.

    Returns:
        absolute path to the created html file
    """
    if (
        shelf
        and not shelf.is_index(page)
        and len(page.labels) != len(site_config.SHELF_LABELS)
    ):
        expected = [label.rst_key for label in site_config.SHELF_LABELS]
        actual = [label.rst_key for label in page.labels.keys()]
        LOGGER.warning(
            f"| page '{page.url_path}' have missing labels in its metadata: "
            f"expected {expected}; got {actual}."
        )

    template = page.html_template
    if not template:
        raise ValueError(f"No template specified on page '{page.url_path}'.")

    LOGGER.debug(f"| rendering page with template '{template}'")
    page_html = lxmsite.render_page(
        page=page,
        template_name=template,
        site_config=site_config,
        context=build_context,
    )

    dst_path = Path(dst_root, page.url_path).resolve()
    mkdir(dst_path.parent)
    LOGGER.debug(f"└ writing page '{dst_path}'")
    dst_path.write_text(page_html, encoding="utf-8")
    return dst_path


def build_site(
    config: lxmsite.SiteConfig,
    symlink_stylesheets: bool,
) -> list[Exception]:
    """

    Args:
        config: config driving the build process.
        symlink_stylesheets:
            True to create symlink for stylesheets files instead
            of a hard copy. Thus allowing live edit of the stylesheet.

    Returns:
        collection of errors if any (that are already logged).
    """
    errors: list[Exception] = []

    src_root = config.SRC_ROOT
    dst_root = config.DST_ROOT
    build_context = get_context()

    site_files = lxmsite.collect_site_files(src_root)
    LOGGER.debug(f"🗂️ collected {len(site_files)} site files")

    shelf_files: dict[Path, list[Path]] = lxmsite.collect_shelves(site_files)
    LOGGER.debug(f"📚 collected {len(shelf_files)} shelf files")

    meta_collection: lxmsite.MetaFileCollection = lxmsite.collect_meta_files(site_files)
    meta_paths = [meta_file.path for meta_file in meta_collection.meta_files]
    LOGGER.debug(f"📋 collected {len(meta_paths)} meta files")

    # remove shelf and meta files so they are not copied as static files
    site_files = [
        path
        for path in site_files
        if not (path in shelf_files) and not (path in meta_paths)
    ]

    # collect pages and static files
    pages: dict[Path, PageResource] = {}
    static_paths: list[Path] = []
    try:
        pages, static_paths = parse_pages(
            site_files=site_files,
            site_config=config,
            meta_collection=meta_collection,
        )
    except ExceptionStack as error:
        errors += error.errors

    # collect shelves and their associated pages
    shelves: list[ShelfResource] = []
    page_by_shelves: dict[Path, ShelfResource] = {}
    try:
        shelves, page_by_shelves = parse_shelves(
            src_root=src_root,
            shelf_files=shelf_files,
            pages=pages,
        )
    except ExceptionStack as error:
        errors += error.errors

    # write html pages to disk
    for page_path, page in pages.items():
        LOGGER.debug(f"┌ 📃 building page '{page.url_path}'")
        # TODO verify nested shelves support and add it or not
        parent_shelf: ShelfResource | None = page_by_shelves.get(page_path)
        try:
            build_page(
                page=page,
                shelf=parent_shelf,
                dst_root=dst_root,
                site_config=config,
                build_context=build_context,
            )
        except Exception as error:
            LOGGER.error(f"└ {fmterr(str(page), error)}")
            errors.append(error)
            continue

    for shelf in shelves:
        # TODO build shelves
        pass

    stylesheet_paths = [
        Path(src_root, page.url_path, p).resolve()
        for page in pages.values()
        for p in page.stylesheets
    ]
    stylesheet_paths += [
        Path(src_root, p).resolve() for p in config.DEFAULT_STYLESHEETS
    ]

    for static_path in static_paths:
        dst_path = Path(dst_root, static_path.relative_to(src_root))
        # we can't use Path.resolve because it resolves symlinks
        dst_path = Path(os.path.abspath(dst_path))
        mkdir(dst_path.parent)

        if symlink_stylesheets and static_path in stylesheet_paths:
            if dst_path.exists():
                LOGGER.debug(f"📦 unlink({dst_path})")
                dst_path.unlink()
            LOGGER.debug(f"📦 os.symlink({static_path}, {dst_path})")
            os.symlink(static_path, dst_path)
        else:
            if is_file_newer(static_path, dst_path):
                LOGGER.debug(f"📦 shutil.copy({static_path}, {dst_path})")
                shutil.copy(static_path, dst_path)
            else:
                LOGGER.debug(
                    f"📦⏭️ skipping copy of '{static_path}'; already up-to-date"
                )

    return errors
