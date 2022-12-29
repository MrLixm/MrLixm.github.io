"""

"""
import json
import logging
import msvcrt
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

TARGET_BRANCH_NAME = "master"
INFO_FILE_PATH = Path("../info.json").resolve()


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

    u_continue = input(
        f'Website will be published and pushed to "{TARGET_BRANCH_NAME}" to make it '
        "accessible online.\n Are you sure to continue ? ( y to continue)"
    )  # type: str
    if u_continue != "y":
        raise InterruptedError("User doesn't want to continue.")

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

    publish_command = [
        r"C:\Program Files\Git\bin\sh.exe",
        "_git-publish-noprompt.sh",
        f"{commit_name}",
        f"{infofile.version}",
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

    process = subprocess.run(
        publish_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    logger.info(
        f"[publish][_git-publish-noprompt.sh] stdout:\n    {process.stdout.decode('utf-8')}"
    )

    if process.stderr:
        raise RuntimeError(
            f"Error while executing <_git-publish-noprompt.sh>:\n{process.stderr.decode('utf-8')}"
        )

    return


def run():

    dryrun = "--dryrun" in sys.argv[1:]
    if dryrun:
        logger.info(f"[run] Started with {dryrun=}")

    commit_name = get_commit_name()
    infofile = InfoFile(path=INFO_FILE_PATH)

    publish(infofile=infofile, commit_name=commit_name, dry_run=dryrun)

    logger.info("[run] Finished.")
    return


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format="{levelname: <7} | {asctime} [{name: >30}]{message}",
        style="{",
    )

    run()
