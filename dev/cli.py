import os
import logging

import click
import pelican

import dev.c
import dev.publish

logger = logging.getLogger(__name__)


@click.group()
@click.version_option("{}".format(dev.c.__version__))
@click.option(
    "--debug",
    is_flag=True,
    envvar=dev.c.Env.logs_debug.value,
    help="This will enable the debug mode which display more informations and disable some features.",
    # --debug is used via sys.argv across the app, do not remove.
)
@click.pass_context
def cli(ctx: click.Context, debug: bool):
    """
    Developer tools for working and editing this blog.
    """
    logger.debug(f"[cli] Started.(cwd={os.getcwd()})[{debug=}]")
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
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
    dev.publish.interactive_publish(dry_run=dry_run)


@cli.command()
@click.pass_context
def preview(ctx: click.Context):
    """
    Build the website and create a local server to preview it.
    The build is auto-refreshed for changes.
    """
    if ctx.obj.get("debug"):
        pelican.main(["--verbose"])

    pelican.main(["--delete-output-directory"])
    pelican.main(["content"])
    pelican.main(["--autoreload", "--listen"])
