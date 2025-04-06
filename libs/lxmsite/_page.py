import dataclasses
import logging
from pathlib import Path
from typing import Generator

import docutils.core
import docutils.io
import docutils.nodes
import docutils.parsers.rst
import docutils.readers.standalone
import docutils.writers.html4css1

from lxmsite import SiteConfig
from lxmsite import ShelfLabel

LOGGER = logging.getLogger(__name__)


def parse_metadata(document: docutils.nodes.document) -> dict[str, str]:
    """
    Extract metadata field from a parsed rst document.

    References:
        - [1] https://github.com/getpelican/pelican/blob/main/pelican/readers.py#L211

    Returns:
        metadata as name:value pair
    """
    # https://docutils.sourceforge.io/docs/ref/doctree.html#docinfo
    docinfos: Generator = document.findall(docutils.nodes.docinfo)
    docinfos: list[docutils.nodes.docinfo] = list(docinfos)
    nodes = docinfos[0].children if docinfos else []

    # this is the type of node we can expect:
    # (https://docutils.sourceforge.io/docs/ref/doctree.html#bibliographic-elements)
    #   simple: <address>, <author>, <contact>, <copyright>, <date>, <organization>, <revision>, <status>, <version>
    #   compound: <authors>, <field>

    metadata = {}

    for node in nodes:
        tagname = node.tagname.lower()
        # if custom fields (non-rst standard)
        if tagname == "field":
            field_name, field_body = node.children
            key = field_name.astext()
            value = field_body.astext()

        # the only "compund" type element (with the above 'fields')
        elif tagname == "authors":  # author list
            key = tagname
            value = [author.astext() for author in node.children]

        # any other standard fields
        else:
            key = tagname
            value = node.astext()

        metadata[key] = value

    return metadata


def read_rst(
    file_path: Path,
    settings: dict,
    encoding: str = "utf-8",
) -> docutils.core.Publisher:
    """
    Parse a rst file as a docutils Publisher

    Args:
        file_path: fileysstem path to an existing rst file.
        settings: docutils settings overrides
        encoding: text encoding for reading and writing
    """
    parser = docutils.parsers.rst.Parser()
    reader = docutils.readers.standalone.Reader(parser=parser)
    writer = docutils.writers.html4css1.Writer()
    source = docutils.io.FileInput(
        source_path=str(file_path),
        encoding=encoding,
        # other option is 'ignore' to ignore encoding errors
        error_handler="strict",
    )
    destination = docutils.io.StringOutput(encoding=encoding)

    publisher = docutils.core.Publisher(
        reader=reader,
        parser=parser,
        writer=writer,
        source=source,
        destination=destination,
    )
    publisher.process_programmatic_settings(None, settings, None)
    publisher.publish()
    return publisher


@dataclasses.dataclass
class PageResource:
    """
    A page is a rst document that will be translated to a single web page.

    A page may or may not belong to a shelf.
    """

    title: str
    metadata: dict[str, str]
    labels: dict[ShelfLabel, str]
    file_path: Path
    html_content: str
    html_template: str | None


def read_page(
    file_path: Path,
    site_config: SiteConfig,
) -> PageResource:
    publisher = read_rst(file_path, settings=site_config.DEFAULT_DOCUTILS_SETTINGS)
    parts = publisher.writer.parts
    content = parts.get("body")
    title = parts.get("title")
    metadata = parse_metadata(publisher.document)

    page_labels = {}
    for label in site_config.SHELF_LABELS:
        page_label = metadata.pop(label.rst_key, None)
        if not page_label:
            continue
        page_labels[label] = page_label

    template = metadata.pop("template", None)

    return PageResource(
        title=title,
        metadata=metadata,
        file_path=file_path,
        html_content=content,
        labels=page_labels,
        html_template=template,
    )


def render_page(page: PageResource, site_config: SiteConfig) -> str:
    # TODO
    return page.html_content
