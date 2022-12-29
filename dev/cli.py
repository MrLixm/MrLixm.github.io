import os
import logging

import click
from . import c

logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.version_option("{}".format(c.__version__))
@click.option(
    "--debug",
    is_flag=True,
    envvar=c.Env.logs_debug.value,
    help="This will enable the debug mode which display more informations and disable some features.",
    # --debug is used via sys.argv across the app, do not remove.
)
def cli(debug: bool):
    """
    Developer tools for working and editing this blog.
    """
    logger.debug(f"[cli] Started.(cwd={os.getcwd()})[{debug=}]")
    return


@cli.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Do not write anything anywhere == non-destructive",
)
def publish(dry_run: bool):
    """
    Make the blog available online by building and pushing it to the remote.
    """
    # TODO
    pass
