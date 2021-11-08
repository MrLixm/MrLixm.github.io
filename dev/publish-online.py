"""

"""
from datetime import datetime
import json
import msvcrt
import subprocess
from pathlib import Path


OUTPUT_TARGET = "master"  # branch name


class InfoFile:

    path = Path("../info.json").resolve()

    def __init__(self):
        self.data = json.load(self.path.open())
        if not self.data:
            raise TypeError(f"The file {self.path} is empty !")

    @property
    def version(self):
        return self.data["VERSION"]

    @version.setter
    def version(self, version_value):
        new = self.data
        new["VERSION"] = version_value
        self.path.write_text(json.dumps(new, indent=4), encoding='utf-8')
        return

    @property
    def last_modified(self):
        return self.data["LAST_PUBLISHED"]

    @last_modified.setter
    def last_modified(self, last_modified_value):
        new = self.data
        new["LAST_PUBLISHED"] = last_modified_value
        self.path.write_text(json.dumps(new, indent=4), encoding='utf-8')
        return

    def increment_version(self):
        old = self.version
        new = old + 1
        self.version = new
        print(f"[InfoFile] info.json VERSION incremented from <{old}> to <{new}>")
        return

    def write_last_published(self):
        date = datetime.now()
        self.last_modified = str(date)
        print(f"[InfoFile] info.json LAST_PUBLISHED changed to <{date}>")
        return


def run():

    commit_name = get_commit_name()
    publish(commit_name=commit_name)

    return


def get_commit_name():

    u_continue = input(
        f"Website will be push to {OUTPUT_TARGET} and become accesible online.\n"
        "Are you sure ton continue ? ( y to continue)"
    )  # type: str
    if u_continue != "y":
        raise InterruptedError("User doesn't want to continue.")

    commit_name = input(
        "Give a name to this commit (change made):"
    )

    # we ask if the commit name is ok, the user can retype it if not.
    while True:

        print(f"[commit name]:\n{commit_name}\n")

        if input("Is the name ok ? (y for yes)") == "y":
            break

        # if escape key is pressed
        if msvcrt.kbhit() and msvcrt.getch().decode() == chr(27):
            raise InterruptedError("User pressed escape key")

        commit_name = input(
            "Give a name to this commit (change made):"
        )

        continue

    return commit_name


def publish(commit_name: str):

    infofile = InfoFile()

    args = [
        r"C:\Program Files\Git\bin\sh.exe",
        "_git-publish-noprompt.sh",
        f"{commit_name}",
        f"{infofile.version}"
    ]

    # update the info.json before any commits (not good if error happen)
    infofile.write_last_published()
    infofile.increment_version()

    process = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    print(f"[publish][_git-publish-noprompt.sh] stdout:\n    {process.stdout.decode('utf-8')}")

    if process.stderr:
        raise RuntimeError(
            f"Error while executing <_git-publish-noprompt.sh>:\n{process.stderr.decode('utf-8')}"
        )

    return


if __name__ == '__main__':
    run()