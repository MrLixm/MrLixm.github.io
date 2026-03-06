import argparse
import contextlib
import logging
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import lxmsite

LOGGER = logging.getLogger(Path(__file__).stem)

THISDIR = Path(__file__).parent


def errexit(msg: str, exitcode: int = 1):
    print(f"❌ ERROR: {msg}", file=sys.stderr)
    # poor's man buffering to let the stream catchup in the terminal
    time.sleep(0.01)
    sys.exit(exitcode)


def gitget(command: list[str], cwd: Path) -> str:
    """
    Call git and get its output (which is not logged).
    """
    out = subprocess.check_output(["git"] + command, cwd=cwd, text=True)
    out = out.rstrip("\n").rstrip(" ")
    return out


def gitc(command: list[str], cwd: Path):
    """
    Call git. Output is logged in terminal.
    """
    subprocess.check_call(["git"] + command, cwd=cwd)


def find_git_root(source_path: Path) -> Path | None:
    """
    Recurse directory up until finding the root for the .git directory.
    """
    for parent in list(source_path.parents) + [source_path]:
        if Path(parent, ".git").is_dir():
            return parent
    return None


@contextlib.contextmanager
def publish_context(
    build_dir: Path,
    git_repo: Path,
    commit_msg: tuple[str, str],
    dry_run: bool = False,
):
    """
    Perform actions that will be published to the gh-page branch.

    Args:
        build_dir: filesystem path to a directory that may not exist yet.
        commit_msg: message for the gh-page branch commit.
        dry_run: If True do not affect the repository permanently.
        git_repo:
    """
    LOGGER.debug(f"git worktree add {build_dir} gh-pages")
    gitc(["worktree", "add", str(build_dir), "gh-pages"], cwd=git_repo)
    try:
        gitc(["pull"], cwd=build_dir)
        # ensure to clean the gh-pages content at each build
        gitc(["rm", "--quiet", "--ignore-unmatch", "-r", "*"], cwd=build_dir)

        yield

        gitc(["worktree", "prune"], cwd=git_repo)
        worktrees = gitget(["worktree", "list"], cwd=git_repo)
        LOGGER.debug(f"git worktree list\n{worktrees}")
        if build_dir.as_posix() not in worktrees:
            errexit(f"worktree '{build_dir}' was deleted at some point.")

        gitc(["add", "--all"], cwd=build_dir)

        changes = gitget(["status", "--porcelain"], cwd=build_dir)
        if not changes:
            LOGGER.warning("nothing to commit, skipping publishing ...")
            return

        LOGGER.info(f"git changes found:\n{changes}")

        if dry_run:
            LOGGER.warning("dry run specified; returning ...")
            return
        else:
            LOGGER.info(f"git commit -m '{commit_msg[0]}' -m '{commit_msg[1]}'")
            gitc(["commit", "-m", commit_msg[0], "-m", commit_msg[1]], cwd=build_dir)
            LOGGER.info("git push origin gh-pages")
            gitc(["push", "origin", "gh-pages"], cwd=build_dir)

    finally:
        # `git worktree remove` is supposed to delete it but fail, so we do it in python
        LOGGER.debug(f"shutil.rmtree({build_dir})")
        shutil.rmtree(build_dir, ignore_errors=True)
        LOGGER.debug(f"git worktree prune")
        gitc(["worktree", "prune"], cwd=git_repo)


def get_cli(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generates the static website.")
    parser.add_argument(
        "--site-config",
        type=Path,
        default=THISDIR.parent / "site" / "site-config.py",
        help="filesystem path to the site's python config file",
    )
    parser.add_argument(
        "--build-dir",
        type=Path,
        default=THISDIR.parent / "site" / ".deploy",
        help="filesystem path to write the final html site to.",
    )
    parsed = parser.parse_args(argv)
    return parsed


def main(argv: list[str] | None = None):
    argv = argv or sys.argv[1:]
    LOGGER.debug(f"started with argv={argv}")
    cli = get_cli(argv)
    site_config_path: Path = cli.site_config
    build_dir: Path = cli.build_dir
    git_dir: Path = find_git_root(site_config_path)
    site_config_path_rel = site_config_path.relative_to(git_dir)

    stime = time.time()

    LOGGER.debug(f"{git_dir=}")
    LOGGER.debug(f"{site_config_path=}")
    LOGGER.debug(f"{site_config_path_rel=}")
    LOGGER.debug(f"{build_dir=}")

    if not site_config_path.exists():
        errexit(
            f"given site config file '{site_config_path}' does not exist.",
        )
    if not git_dir:
        errexit(
            f"given site config file '{site_config_path}' is not part of any git repository"
        )

    # // git checks before build

    git_status = gitget(["status", "--porcelain"], cwd=git_dir)
    git_last_commit = gitget(["rev-parse", "HEAD"], cwd=git_dir)
    git_current_branch = gitget(["branch", "--show-current"], cwd=git_dir)
    git_remote_status = gitget(["status", "--short", "--b", "--porcelain"], cwd=git_dir)

    if git_current_branch != "main":
        errexit(f"expected current git branch to be 'main'; got '{git_current_branch}'")

    if git_status:
        try:
            errexit(f"Uncommited changes found:\n{git_status}")
        except SystemExit:
            print("(uncomitted changes will not be deployed)")
            answer = input("Do you still wish to continue [Y/n] ?")
            if answer.lower() in ["n", "no"]:
                raise

    if re.search(rf"## {git_current_branch}.+\[ahead", git_remote_status):
        errexit("current git branch is ahead of its remote (need push).")

    if re.search(rf"## {git_current_branch}.+\[behind", git_remote_status):
        errexit("current git branch is behind of its remote (need pull).")

    commit_msgs = (
        f"chore(doc): automatic build to gh-pages",
        f"from commit {git_last_commit} on branch {git_current_branch}",
    )

    # // clone repo in a temp dir to remove all uncommited changes so they are not deployed

    tmp_dir = Path(tempfile.mkdtemp(prefix="mrlixm.github.io-"))
    clone_dir = tmp_dir / "repo"
    # note: the clone preserve the currently active branch/commit
    gitc(["clone", "--local", str(git_dir), str(clone_dir)], cwd=tmp_dir)
    git_dir = clone_dir

    # // prepare site config

    site_config_path = git_dir / site_config_path_rel
    LOGGER.info(f"🧾 reading site config '{site_config_path}'")
    config = lxmsite.SiteConfig.from_path(site_config_path)
    config.sanitize()
    LOGGER.debug(config.debug())
    config.PUBLISH_MODE = True
    config.DST_ROOT = build_dir

    # // start the build and publish

    with publish_context(build_dir, git_dir, commit_msg=commit_msgs, dry_run=False):
        LOGGER.info(f"🔨 building site to '{build_dir}'")
        errors = lxmsite.build_site(
            config=config,
            symlink_stylesheets=False,
        )
        eicon = "⚠️" if errors else "✅"
        etime = time.time() - stime
        LOGGER.info(f"{eicon} site build finished in {etime:.1f}s.")
        if errors:
            errors_str = "\n - ".join(map(str, errors))
            errexit(f"{len(errors)} errors generated during build:\n - {errors_str}")

        answer = input(
            f"you are about to deploy the website to '{config.SITE_URL}'; "
            f"do you wish to continue [y/N] ?"
        )
        if answer.lower() not in ["y", "yes"]:
            errexit(f"deploy aborted by user")

    LOGGER.info(
        f"site deployed at '{config.SITE_URL}'; check it again in a few minutes."
    )
    shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    lxmsite.configure_logging(level=logging.WARNING)
    LOGGER.setLevel(logging.DEBUG)
    logging.getLogger(lxmsite.__name__).setLevel(logging.DEBUG)
    main()
