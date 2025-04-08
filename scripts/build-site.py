import argparse
import logging
import shutil
import sys
import time
from pathlib import Path

import lxmsite

LOGGER = logging.getLogger(Path(__file__).stem)

THISDIR = Path(__file__).parent


def errexit(msg: str, exitcode: int = 1):
    print(msg, file=sys.stderr)
    sys.exit(exitcode)


def get_cli(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generates the static website.")
    parser.add_argument(
        "--site-config",
        type=Path,
        default=THISDIR.parent / "site" / "site-config.py",
        help="filesystem path to the site's python config file.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="If specified configure the site build for web publishing instead of local.",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=None,
        help="filesystem path to write the final html site to.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="If specified, remove first any preivous build that might already exist.",
    )
    parsed = parser.parse_args(argv)
    return parsed


def main(argv: list[str] | None = None):
    argv = argv or sys.argv[1:]
    LOGGER.debug(f"started with argv={argv}")
    cli = get_cli(argv)
    build_dir: Path | None = cli.target_dir
    publish: bool = cli.publish
    site_config_path: Path = cli.site_config
    clear: bool = cli.clear

    stime = time.time()

    LOGGER.debug(f"{build_dir=}")
    LOGGER.debug(f"{publish=}")
    LOGGER.debug(f"{site_config_path=}")
    LOGGER.debug(f"{clear=}")

    if not site_config_path.exists():
        errexit(
            f"❌ ERROR: given site config file '{site_config_path}' does not exist.",
        )

    LOGGER.info(f"🧾 reading site config '{site_config_path}'")
    config = lxmsite.SiteConfig.from_path(site_config_path)
    config.sanitize()
    LOGGER.debug(config.debug())
    if not config.PUBLISH_MODE:
        config.PUBLISH_MODE = publish
    if build_dir:
        config.DST_ROOT = build_dir
    else:
        build_dir = config.DST_ROOT

    if not build_dir:
        errexit(f"❌ ERROR: no build directory provided in config or from CLI.")
    if build_dir.exists() and clear:
        LOGGER.debug(f"🗑️ shutil.rmtree({build_dir})")
        shutil.rmtree(build_dir)
    if not build_dir.exists():
        LOGGER.debug(f"📁 mkdir({build_dir})")
        build_dir.mkdir()

    LOGGER.info(f"🔨 building site to '{build_dir}'")
    errors = lxmsite.build_site(
        config=config,
        symlink_stylesheets=not publish,
    )

    # post build checkups
    for link in config.HEADER_NAV.values():
        if not build_dir.joinpath(link).exists():
            LOGGER.warning(f"found non-existing link in header nav: {link}")

    exitcode = 1 if errors else 0
    eicon = "⚠️" if errors else "✅"
    etime = time.time() - stime
    LOGGER.info(f"{eicon} site build finished in {etime:.1f}s.")
    if errors:
        LOGGER.warning(f"└ {len(errors)} errors generated")
    LOGGER.info(f"🌐 check 'file:///{build_dir.as_posix()}/index.html'")
    sys.exit(exitcode)


if __name__ == "__main__":
    lxmsite.configure_logging()
    main()
