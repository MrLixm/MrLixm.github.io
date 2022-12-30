import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

THIS_DIR = Path(__file__).parent

SH_EXE = Path(r"C:\Program Files\Git\bin\sh.exe")
assert SH_EXE.exists(), SH_EXE


def get(shell_script_name: str) -> Path:
    """
    Retrieve the path for the given shell script name.

    Args:
        shell_script_name: name of the shell script with OR without the extension

    Returns:
        existing path to a .sh script
    """

    shell_script_name = shell_script_name.removesuffix(".sh")
    path = THIS_DIR / f"{shell_script_name}.sh"
    if not path.exists():
        raise FileNotFoundError(
            f"Can't find shell script <{shell_script_name}> in {THIS_DIR}: {path}"
        )

    return path


def execute(shell_script_path: Path, *args) -> str:
    """
    Execute the given shell script with the given args and return the output from it.

    Args:
        shell_script_path: existing path of the shell script to excecute
        *args: list of argument to pass the shell script

    Returns:
        STDOUT of the shell script

    Raises:
        RuntimeError: if the shell script produce a non-zero returncode (=error)
    """

    shell_command = [
        str(SH_EXE),
        str(shell_script_path),
    ]
    shell_command += args

    process = subprocess.Popen(
        shell_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, error = process.communicate()
    out = out.decode("utf-8")
    logger.info(f"[execute]({shell_script_path.name})\n{out}")

    if error:
        error = error.decode("utf-8")
        logger.warning(f"[execute]({shell_script_path.name})\n{error}")

    if process.returncode != 0:
        raise RuntimeError(
            f"{shell_script_path.name} RETURNED WITH NON-ZERO STATUS {process.returncode}"
        )

    return out
