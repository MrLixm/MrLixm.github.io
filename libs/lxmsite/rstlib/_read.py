import logging
import os
from pathlib import Path
from typing import Generator, Callable

import docutils.core
import docutils.frontend
import docutils.io
import docutils.nodes
import docutils.parsers.rst
import docutils.readers.standalone
import docutils.writers.html5_polyglot as docutils_writers

from ._extensions import AdmonitionsTransform
from ._extensions import LinksTransform
from ._extensions import ContentsTransform
from ._extensions import parse_code_to_node
from .._utils import slugify

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
            value = ",".join(value)

        # any other standard fields
        else:
            key = tagname
            value = node.astext()

        metadata[key] = value

    return metadata


class LxmHTMLTranslator(docutils_writers.HTMLTranslator):

    def visit_title(self, node: docutils.nodes.title) -> None:
        if (
            node.has_key("refid")
            and node["refid"].startswith("toc-entry")
            and node.parent.hasattr("ids")
            and node.parent["ids"]
        ):
            new_id = node.parent["ids"][0]
            node["refid"] = new_id
        super().visit_title(node)

    def visit_caption(self, node):
        # we override to convert 'caption' to <label> because docutils is already using
        # 'label' for some footnote reference stuff I don't want to touch.

        if isinstance(node.parent, docutils.nodes.figure):
            self.body.append("<figcaption>\n")
            self.body.append(self.starttag(node, "p", ""))
            return

        options = {}
        if "for" in node:
            options["for"] = node["for"]
        self.body.append(self.starttag(node, "label", "", CLASS="caption", **options))

    def depart_caption(self, node):
        if isinstance(node.parent, docutils.nodes.figure):
            self.body.append("</p>\n")
            # <figcaption> is closed in depart_figure()
            return
        self.body.append("</label>\n")

    def starttag(self, node, tagname, suffix="\n", empty=False, **attributes):
        title = node.get("title", "")
        if "title" not in attributes and title:
            attributes["title"] = title
        style = node.get("style", "")
        if "style" not in attributes and style:
            attributes["style"] = style
        return super().starttag(node, tagname, suffix=suffix, empty=empty, **attributes)

    def visit_abbreviation(self, node):
        attrs = {}
        if title := node["explanation"]:
            attrs["title"] = title
        self.body.append(self.starttag(node, "abbr", "", **attrs))

    def visit_image(self, node):
        # default docutils behavior is to set the alt with the URL which is worse than no alt
        node["alt"] = node.get("alt", "")
        node["classes"] += ["inline"]
        return super().visit_image(node)

    def visit_figure(self, node):
        node["classes"] += ["inline"]
        return super().visit_figure(node)

    def visit_doctest_block(self, node):
        """
        Highlight doctest python code using pygments.
        """
        new_children = []
        for child in node.children:
            content = child.astext()
            newnode = parse_code_to_node(code=content, lexer_name="python-console")
            newnode["classes"].append("doctest")
            new_children.append(newnode)
        node.children = new_children


class LxmHtmlWriter(docutils_writers.Writer):
    """
    Args:
        uri_callback: arbitrary function that receive the original uri and must return the new desired uri.
    """

    def __init__(self, uri_callback: Callable[[str], str] = None):
        super().__init__()
        # also add our custom translator
        self.translator_class = LxmHTMLTranslator
        self.uri_callback = uri_callback

    def get_transforms(self):
        transforms = super().get_transforms()

        # remove the builtin transform responsible on adding the title to admonitions so we can add our
        builtin_adm_transform = docutils.transforms.writer_aux.Admonitions
        if builtin_adm_transform in transforms:
            transforms.remove(builtin_adm_transform)
        transforms.append(AdmonitionsTransform)

        if self.uri_callback:
            transforms.append(LinksTransform)

        transforms.append(ContentsTransform)

        return transforms

    def translate(self):
        super().translate()
        if self.uri_callback:
            self.body = self._resolve_uris(self.body)

    def _resolve_uris(self, readen_rst: str) -> str:
        """
        Resolve the tokens applied by the LinksTransform transform.
        """
        for match in LinksTransform.token_pattern.finditer(readen_rst):
            original_uri = match.group(1)
            new_uri = self.uri_callback(original_uri)
            readen_rst = readen_rst.replace(match.group(0), new_uri)

        return readen_rst


def read_rst(
    file_path: Path,
    settings: dict,
    uri_callback: Callable[[str], str] = None,
) -> docutils.core.Publisher:
    """
    Parse a rst file as a docutils Publisher

    Args:
        file_path: fileysstem path to an existing rst file.
        settings: docutils settings overrides
        uri_callback:
            arbitrary function that is run on all the document uris.
            It receives the original uri and must return the new desired uri.
    """
    cwd = os.getcwd()
    # needed by some directives to compute paths expressed in documents
    # TODO this prevent threading ! fixing it is complex and require refactoring multiple directives
    os.chdir(file_path.parent)

    try:
        parser = docutils.parsers.rst.Parser()
        reader = docutils.readers.standalone.Reader(parser=parser)
        writer = LxmHtmlWriter(uri_callback=uri_callback)

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

    finally:
        os.chdir(cwd)

    return publisher
