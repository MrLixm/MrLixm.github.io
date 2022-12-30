"""

"""
__all__ = ("interactive_publish",)

import json
import logging
import msvcrt
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

TARGET_BRANCH_NAME = "master"

SH_EXE = Path(r"C:\Program Files\Git\bin\sh.exe")
assert SH_EXE.exists(), SH_EXE

INFO_FILE_PATH = Path(__file__).parent / "../info.json"
INFO_FILE_PATH = INFO_FILE_PATH.absolute().resolve()
assert INFO_FILE_PATH.exists(), INFO_FILE_PATH

PUBLISH_SHELL_SCRIPT = Path(__file__).parent / "shell" / "build-n-publish.sh"
assert PUBLISH_SHELL_SCRIPT.exists(), PUBLISH_SHELL_SCRIPT


class InfoFile:
    """
    Simple json used to store version and last published date.
    """

    def __init__(self, path: Path):
        self.path: Path = path
        self._data: dict = {}
        self.read()

    def __str__(self) -> str:
        return json.dumps(self._data, indent=4)

    @property
    def version(self) -> int:
        return self._data["VERSION"]

    @version.setter
    def version(self, version_value: int):
        self._data["VERSION"] = version_value

    @property
    def last_modified(self) -> str:
        return self._data["LAST_PUBLISHED"]

    @last_modified.setter
    def last_modified(self, last_modified_value: str):
        self._data["LAST_PUBLISHED"] = last_modified_value

    def read(self):
        """
        Ovewrite teh inetrnal data with the content from the file on disk.
        """
        self._data = json.load(self.path.open())
        if not self._data:
            raise TypeError(f"The file {self.path} is empty !")

    def write(self):
        """
        Overwrite the content of the file on disk with the internal one.
        """
        self.path.write_text(json.dumps(self._data, indent=4), encoding="utf-8")

    def increment_version(self):

        old = self.version
        new = old + 1
        self.version = new

        logger.info(
            f"[{self.__class__.__name__}][increment_version] "
            f"VERSION incremented from <{old}> to <{new}>"
        )
        return

    def update_last_published(self, date: Optional[str] = None):

        date = date or datetime.now()
        self.last_modified = str(date)

        logger.info(
            f"[{self.__class__.__name__}][write_last_published] "
            f"LAST_PUBLISHED changed to <{date}>"
        )
        return


def get_commit_name() -> str:
    """
    Ask the user to give a name to the commit used for publishing.
    """

    commit_name = input("Give a name to this commit (summary of changes made):")

    # we ask if the commit name is ok, the user can retype it if not.
    while True:

        print(f"[commit name]:\n{commit_name}\n")

        if input("Is the name ok ? (y for yes)") == "y":
            break

        # if escape key is pressed
        if msvcrt.kbhit() and msvcrt.getch().decode() == chr(27):
            raise InterruptedError("User pressed escape key")

        commit_name = input("Give a name to this commit (change made):")

        continue

    return commit_name


def publish(infofile: InfoFile, commit_name: str, dry_run: bool = False):
    """

    Args:
        infofile: infofile to update before publish
        commit_name: name to use for the publish commit.
        dry_run: True to not write anything on disk.
    """

    if not Path(".git").exists():
        raise ValueError(
            f"Current working directory is not the root of the Blog repo: {os.getcwd()}"
        )

    publish_command = [
        str(SH_EXE),
        str(PUBLISH_SHELL_SCRIPT),
        f"{commit_name}",
        f"{infofile.version}",
        TARGET_BRANCH_NAME,
    ]

    logger.info(f"[publish] {publish_command=}")
    logger.info(f"[publish] {infofile=}")

    # update the info.json before any commits (not good if error happen)
    infofile.update_last_published()
    infofile.increment_version()

    if dry_run:
        logger.info(f"[publish] Returned earlier: {dry_run=}")
        return

    infofile.write()

    logger.info(f"[publish] calling {PUBLISH_SHELL_SCRIPT.name} ...")

    process = subprocess.Popen(
        publish_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, error = process.communicate()
    logger.info(
        f"[publish][{PUBLISH_SHELL_SCRIPT.name}] result = {out.decode('utf-8')}"
    )
    if error:
        logger.warning(error.decode("utf-8"))

    if process.returncode != 0:
        logger.error(
            f"[publish][{PUBLISH_SHELL_SCRIPT.name}] RETURNED WITH NON ZERO STATUS {process.returncode}"
        )

    return


def interactive_publish(dry_run: bool = False):
    """
    Start the publish process by prompting the user from the command line.
    """

    logger.info(
        f"[interactive_publish] Started with {dry_run=}. "
        f"Target branch is <{TARGET_BRANCH_NAME}>"
    )

    commit_name = get_commit_name()
    infofile = InfoFile(path=INFO_FILE_PATH)

    publish(infofile=infofile, commit_name=commit_name, dry_run=dry_run)

    logger.info("[interactive_publish] Finished.")
    return


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format="{levelname: <7} | {asctime} [{name}]{message}",
        style="{",
    )

    interactive_publish()
