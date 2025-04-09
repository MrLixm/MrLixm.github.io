import logging
from pathlib import Path
from typing import Generator

import docutils.core
import docutils.frontend
import docutils.io
import docutils.nodes
import docutils.parsers.rst
import docutils.readers.standalone
import docutils.writers.html5_polyglot as docutils_writers

import pygments
import pygments.lexers
import pygments.formatters

LOGGER = logging.getLogger(__name__)

DocumentType = docutils.nodes.document


def parse_metadata(document: DocumentType) -> dict[str, str]:
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


class LxmHTMLTranslator(docutils_writers.HTMLTranslator):
    def visit_abbreviation(self, node):
        attrs = {}
        if title := node["explanation"]:
            attrs["title"] = title
        self.body.append(self.starttag(node, "abbr", "", **attrs))

    def depart_abbreviation(self, node):
        self.body.append("</abbr>")

    def visit_doctest_block(self, node):
        """
        Highlight doctest python code using pygments.
        """
        new_children = []
        for child in node.children:
            lexer = pygments.lexers.get_lexer_by_name("python-console")
            formatter = pygments.formatters.HtmlFormatter(
                noclasses=False,
                cssclass="highlight doctest",
            )
            content = child.astext()
            parsed = pygments.highlight(content, lexer, formatter)
            new_children.append(docutils.nodes.raw("", parsed, format="html"))
        node.children = new_children

    def depart_doctest_block(self, node):
        pass


class LxmHtmlWriter(docutils_writers.Writer):
    def __init__(self):
        super().__init__()
        self.translator_class = LxmHTMLTranslator

    def get_transforms(self):
        transforms = super().get_transforms()
        return transforms + []


def read_rst(
    file_path: Path,
    settings: dict,
) -> docutils.core.Publisher:
    """
    Parse a rst file as a docutils Publisher

    Args:
        file_path: fileysstem path to an existing rst file.
        settings: docutils settings overrides
    """
    parser = docutils.parsers.rst.Parser()
    reader = docutils.readers.standalone.Reader(parser=parser)
    writer = LxmHtmlWriter()

    option_parser = docutils.frontend.OptionParser(
        components=(parser, writer, reader),
        defaults=settings,
        read_config_files=False,
        usage=None,
        description=None,
    )
    default_settings = option_parser.get_default_values()

    source = docutils.io.FileInput(
        source_path=str(file_path),
        encoding=default_settings.input_encoding,
        error_handler=default_settings.input_encoding_error_handler,
    )
    destination = docutils.io.StringOutput(
        encoding=default_settings.output_encoding,
        error_handler=default_settings.output_encoding_error_handler,
    )

    publisher = docutils.core.Publisher(
        reader=reader,
        parser=parser,
        writer=writer,
        source=source,
        destination=destination,
        settings=default_settings,
    )
    publisher.publish()
    return publisher
