import argparse
import logging
import shutil
import sys
import time
from pathlib import Path

import lxmsite

LOGGER = logging.getLogger(Path(__file__).stem)

THISDIR = Path(__file__).parent
BUILDIR = THISDIR / ".build"


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
        default=BUILDIR,
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
    build_dir: Path = cli.target_dir
    publish: bool = cli.publish
    site_config_path: Path = cli.site_config
    clear: bool = cli.clear

    stime = time.time()

    LOGGER.debug(f"{build_dir=}")
    LOGGER.debug(f"{publish=}")
    LOGGER.debug(f"{site_config_path=}")
    LOGGER.debug(f"{clear=}")

    if build_dir.exists() and clear:
        LOGGER.debug(f"🗑️ shutil.rmtree({build_dir})")
        shutil.rmtree(build_dir)
    if not build_dir.exists():
        LOGGER.debug(f"📁 mkdir({build_dir})")
        build_dir.mkdir()

    if not site_config_path.exists():
        errexit(
            f"❌ ERROR: given site config file '{site_config_path}' does not exist.",
        )

    LOGGER.info(f"🔨 building site to '{build_dir}'")
    lxmsite.build_site(
        build_dir=build_dir,
        config_path=site_config_path,
    )
    etime = time.time() - stime
    LOGGER.info(f"✅ site build finished in {round(etime)}s.")
    LOGGER.info(f"🌐 check 'file:///{build_dir.as_posix()}/index.html'")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="{levelname: <7} | {asctime} [{name}] {message}",
        style="{",
        stream=sys.stdout,
    )
    main()
