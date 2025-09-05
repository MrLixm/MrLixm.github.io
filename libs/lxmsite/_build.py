import datetime
import logging
import os
import runpy
import shutil
import time
import traceback
from pathlib import Path

import lxmsite
from lxmsite import PageResource
from lxmsite import PageMetadata
from lxmsite import MetaFileCollection
from lxmsite import ShelfResource
from lxmsite import ShelfLibrary
from lxmsite import SiteConfig
from lxmsite import get_image_weight_ratio
from lxmsite import read_image_opti_file
from lxmsite import ImageOptimizer
from ._utils import gitget
from ._utils import mksiterel

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


def get_context(site_root: Path, site_files: list[Path]) -> lxmsite.SiteGlobalContext:
    git_last_commit = gitget(["rev-parse", "--short", "HEAD"], cwd=site_root)
    return lxmsite.SiteGlobalContext(
        build_time=datetime.datetime.now(),
        last_commit=git_last_commit,
        site_files=site_files,
    )


def fmterr(ctx: str, error: Exception):
    # have shorter traceback by onling priting the 2 last frames
    last_frame = traceback.extract_tb(error.__traceback__)
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
    page_paths: list[Path],
    site_config: SiteConfig,
    meta_collection: MetaFileCollection,
) -> dict[Path, PageResource]:
    """
    Read from disk the given path files as pages objects.
    """
    errors: list[Exception] = []
    pages: dict[Path, PageResource] = {}

    for page_path in page_paths:
        # retrieve default metadata for the page
        default_meta = meta_collection.get_path_meta(page_path)

        LOGGER.debug(f"reading page '{page_path}'")
        LOGGER.debug(f"└ default_meta={default_meta}")
        try:
            page = lxmsite.read_page(
                file_path=page_path,
                site_config=site_config,
                default_metadata=default_meta,
            )
        except Exception as error:
            LOGGER.error(f"{fmterr(str(page_path), error)}")
            errors.append(error)
            continue
        pages[page_path] = page

    if errors:
        raise ExceptionStack(errors)

    return pages


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
    shelf_library: ShelfLibrary,
    dst_root: Path,
    site_config: SiteConfig,
    build_context: lxmsite.SiteGlobalContext,
) -> Path:
    """
    Build the html page on disk, out of the given page resource.

    Args:
        page: the page resource to build.
        shelf: optional parent shelf the page belongs to.
        shelf_library: the collection of all the shelves the site has.
        dst_root: root directory where the file can be found.
        site_config: global site configuration.
        build_context: metadata for the build process.

    Returns:
        absolute path to the created html file
    """
    template = page.html_template
    if not template:
        raise ValueError(f"No template specified on page '{page.url_path}'.")

    LOGGER.debug(f"| rendering page with template '{template}'")
    page_html = lxmsite.render_page(
        page=page,
        template_name=template,
        site_config=site_config,
        context=build_context,
        shelf=shelf,
        shelf_library=shelf_library,
    )

    dst_path = Path(dst_root, page.url_path).resolve()
    mkdir(dst_path.parent)
    LOGGER.debug(f"└ writing page '{dst_path}'")
    dst_path.write_text(page_html, encoding="utf-8")
    return dst_path


def build_redirection(
    redirection_path: Path,
    redirection_dst: str,
    shelf_library: ShelfLibrary,
    site_config: SiteConfig,
    build_context: lxmsite.SiteGlobalContext,
    built_pages: list[Path],
):
    """
    Create a page intended for redirecting to another page.
    """
    page_url = redirection_path.relative_to(site_config.SRC_ROOT).as_posix()
    page = PageResource(
        title=f"Redirecting to '{redirection_dst}'",
        metadata=PageMetadata(extras={"redirect": redirection_dst}),
        url_path=page_url,
        html_content="",
        html_template=site_config.REDIRECTIONS_TEMPLATE,
    )
    LOGGER.debug(f"┌ 📃>🔗 building redirection page '{page_url}'")
    LOGGER.debug(f"| rendering page with template '{page.html_template}'")
    page_html = lxmsite.render_page(
        page=page,
        template_name=page.html_template,
        site_config=site_config,
        context=build_context,
        shelf=None,
        shelf_library=shelf_library,
    )
    dst_path = Path(site_config.DST_ROOT, page.url_path).resolve()
    if dst_path in built_pages:
        raise FileExistsError(
            f"Cannot create redirection for '{page_url}': "
            f"a page already exists at the given url."
        )
    mkdir(dst_path.parent)
    LOGGER.debug(f"└ writing page '{dst_path}'")
    dst_path.write_text(page_html, encoding="utf-8")


def build_rss_feed(shelf: ShelfResource, site_config: SiteConfig) -> Path | None:
    """
    Create a rss feed file from a shelf.
    """
    if not site_config.RSS_FEED_TEMPLATE or shelf.config.disable_rss:
        return None

    LOGGER.debug(f"┌ 📋 building rss feed for shelf '{shelf.name}'")
    dst_path = site_config.DST_ROOT / shelf.rss_feed_url
    content = lxmsite.render_rss_feed(
        shelf=shelf,
        template_name=site_config.RSS_FEED_TEMPLATE,
        site_config=site_config,
    )
    LOGGER.debug(f"└ 📋 writing rss feed to '{dst_path}'")
    dst_path.write_text(content, encoding="utf-8")
    return dst_path


def build_search(dst_root: Path):
    env_backup = os.environ.copy()
    os.environ["PAGEFIND_SITE"] = str(dst_root)
    try:
        runpy.run_module("pagefind")
    except SystemExit as excp:
        if excp.code:
            LOGGER.error("error while running 'pagefind'")
    finally:
        os.environ.clear()
        os.environ.update(env_backup)


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

    site_files = lxmsite.collect_site_files(src_root)
    LOGGER.debug(f"🗂️ collected {len(site_files)} site files")

    shelf_files: dict[Path, list[Path]] = lxmsite.collect_shelves(site_files)
    LOGGER.debug(f"📚 collected {len(shelf_files)} shelf files")

    meta_collection: lxmsite.MetaFileCollection = lxmsite.collect_meta_files(site_files)
    meta_paths = [meta_file.path for meta_file in meta_collection.meta_files]
    LOGGER.debug(f"📋 collected {len(meta_paths)} meta files")

    build_context = get_context(site_root=src_root, site_files=site_files)

    # remove shelf and meta files so they are not copied as static files
    site_files = [
        path
        for path in site_files
        if not (path in shelf_files) and not (path in meta_paths)
    ]

    # collect pages and static files
    stime = time.time()
    page_paths: list[Path] = [path for path in site_files if path.suffix == ".md"]
    static_paths: list[Path] = [path for path in site_files if path not in page_paths]
    # mapping of "absolute path": "Page instance"
    pages: dict[Path, PageResource] = {}
    try:
        pages = parse_pages(
            page_paths=page_paths,
            site_config=config,
            meta_collection=meta_collection,
        )
    except ExceptionStack as error:
        errors += error.errors
    etime = time.time()
    LOGGER.debug(
        f"⌛ parsed pages from {len(site_files)} files in {etime - stime:.2f} seconds"
    )

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

    shelf_library = ShelfLibrary(shelves=shelves)

    # write html pages to disk
    stime = time.time()
    built_pages = []
    for page_path, page in pages.items():
        LOGGER.debug(f"┌ 📃 building page '{page.url_path}'")
        # TODO verify nested shelves support and add it or not
        parent_shelf: ShelfResource | None = page_by_shelves.get(page_path)
        try:
            built_page = build_page(
                page=page,
                shelf=parent_shelf,
                shelf_library=shelf_library,
                dst_root=dst_root,
                site_config=config,
                build_context=build_context,
            )
            built_pages.append(built_page)
        except Exception as error:
            LOGGER.error(f"└ {fmterr(str(page), error)}")
            errors.append(error)
            continue

    etime = time.time()
    LOGGER.debug(f"⌛ built {len(pages)} page in {etime - stime:.2f} seconds")

    # build redirections pages
    stime = time.time()
    for redirection_src, redirection_dst in config.REDIRECTIONS.items():
        redirection_src_path = src_root / redirection_src
        try:
            LOGGER.debug(
                f"📃>🔗 building redirection page '{redirection_src}' to '{redirection_dst}'"
            )
            build_redirection(
                redirection_path=redirection_src_path,
                redirection_dst=redirection_dst,
                site_config=config,
                shelf_library=shelf_library,
                build_context=build_context,
                built_pages=built_pages,
            )
        except Exception as error:
            LOGGER.error(f"└ {fmterr(redirection_src, error)}")
            errors.append(error)
            continue

    etime = time.time()
    LOGGER.debug(
        f"⌛ built {len(config.REDIRECTIONS)} redirection pages in {etime - stime:.2f} seconds"
    )

    LOGGER.debug(f"🔎 building search feature")
    build_search(dst_root=dst_root)

    for shelf in shelves:
        try:
            build_rss_feed(shelf=shelf, site_config=config)
        except Exception as error:
            LOGGER.exception(f"└ 📋⚠️ cannot render rss feed: {error}")
            errors.append(error)
            continue

    stylesheet_paths: dict[Path, list[str]] = {}
    for page in pages.values():
        for path in page.stylesheets:
            resolved_stylesheet_path = Path(
                src_root, mksiterel(path, page.url_path)
            ).resolve()
            stylesheet_paths.setdefault(resolved_stylesheet_path, []).append(
                page.url_path
            )

    image_to_optimize: dict[Path, ImageOptimizer] = {}
    for static_path in static_paths.copy():
        if static_path.suffix == ".opti":
            image_path = Path(str(static_path).removesuffix(".opti"))
            if not image_path.exists():
                continue
            static_paths.remove(static_path)
            LOGGER.debug(f"reading opti file '{static_path}'")
            opti_config = read_image_opti_file(static_path)
            image_to_optimize[image_path] = opti_config
    LOGGER.debug(f"🖼️ found {len(image_to_optimize)} image to optimize")

    stime = time.time()
    heavy_images = {}
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

        elif static_path in image_to_optimize:
            opti_config = image_to_optimize[static_path]
            if opti_config.target_file_suffix:
                dst_path = dst_path.with_suffix(opti_config.target_file_suffix)
            LOGGER.debug(f"┌ 🖼️ optimize({static_path}, {dst_path})")
            presize = static_path.stat().st_size / 1024 / 1024
            opti_config.optimize(src_path=static_path, dst_path=dst_path)
            postsize = dst_path.stat().st_size / 1024 / 1024
            LOGGER.debug(f"└ 🖼️ optimized from {presize:.1f}MiB to {postsize:.1f}MiB")

        else:
            if is_file_newer(static_path, dst_path):
                LOGGER.debug(f"📦 shutil.copy({static_path}, {dst_path})")
                shutil.copy(static_path, dst_path)
            else:
                LOGGER.debug(
                    f"📦⏭️ skipping copy of '{static_path}'; already up-to-date"
                )

        if dst_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
            try:
                ratio = round(get_image_weight_ratio(dst_path, threshold=1.9), 1)
            except Exception:
                continue
            if ratio > 1:
                heavy_images[dst_path] = ratio

    # sort by weight ratio
    heavy_images = {
        k: v for k, v in sorted(heavy_images.items(), key=lambda item: item[1])
    }
    heavy_images_msg = []
    for heavy_image, ratio in heavy_images.items():
        weight = heavy_image.stat().st_size / 1024 / 1024
        heavy_images_msg += [f"[{weight:0>4.1f}MiB|ratio={ratio}] '{heavy_image}'"]
    if heavy_images_msg:
        msg = "\n- ".join(heavy_images_msg)
        LOGGER.warning(f"🧱 found {len(heavy_images_msg)} heavy images:\n- {msg})")

    for path, sources in stylesheet_paths.items():
        if not path.exists():
            sources = "'" + "', '".join(sources) + "'"
            LOGGER.warning(
                f"🔍 found non-existing stylesheet path '{path}' referenced in {sources}."
            )

    etime = time.time()
    LOGGER.debug(
        f"⌛ built {len(static_paths)} static paths in {etime - stime:.2f} seconds"
    )

    return errors
