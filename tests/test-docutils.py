import json
import logging
from io import StringIO
from pathlib import Path

import docutils.writers.html5_polyglot

import docutils.core
import docutils.io
import docutils.nodes
import docutils.utils
import docutils.frontend
import docutils.readers.standalone
import docutils.parsers.rst
import docutils.writers.html4css1

from lxmsite._resources._page import parse_metadata

LOGGER = logging.getLogger(__name__)

SOURCE_PATH = Path(__file__).parent / "test.rst"

EXTRA_PARAMS = {
    "initial_header_level": "2",
    "syntax_highlight": "short",
    "input_encoding": "utf-8",
    # "language_code": self._language_code,
    "halt_level": 2,
    "traceback": True,
    "warning_stream": StringIO(),
    "embed_stylesheet": False,
}


def read1():

    # from https://github.com/getpelican/pelican/blob/main/pelican/readers.py#L253

    pub = docutils.core.Publisher(
        writer=docutils.writers.html5_polyglot.Writer(),
        destination_class=docutils.io.StringOutput,
    )
    pub.set_components(
        reader_name="standalone",
        parser_name="restructuredtext",
        writer_name="html",
    )
    pub.process_programmatic_settings(None, EXTRA_PARAMS, None)
    pub.set_source(source_path=str(SOURCE_PATH))
    pub.publish()


def read2():

    source = docutils.io.FileInput(
        source_path=str(SOURCE_PATH),
        encoding="utf-8",
        error_handler="strict",
    )
    destination = docutils.io.StringOutput(encoding="utf-8")
    parser = docutils.parsers.rst.Parser()
    reader = docutils.readers.standalone.Reader(parser=parser)
    writer = docutils.writers.html4css1.Writer()
    components = (source, reader, parser, writer, destination)

    option_parser = docutils.frontend.OptionParser(
        components=(parser, reader, writer, None),
        defaults={},
        read_config_files=True,
        usage=None,
        description=None,
    )
    settings = option_parser.get_default_values()
    print(json.dumps(settings.__dict__, indent=2, default=str))

    document = reader.read(source=source, parser=parser, settings=settings)
    document.transformer.populate_from_components(components)
    document.transformer.apply_transforms()

    output = writer.write(document, destination)
    print(output)


def read3():
    source = docutils.io.FileInput(
        source_path=str(SOURCE_PATH),
        encoding="utf-8",
        error_handler="strict",
    )
    destination = docutils.io.StringOutput(encoding="utf-8")
    parser = docutils.parsers.rst.Parser()
    writer = docutils.writers.html4css1.Writer()
    option_parser = docutils.frontend.OptionParser(
        # components=(parser, writer, None),
        defaults={},
        read_config_files=False,
        usage=None,
        description=None,
    )
    settings = option_parser.get_default_values()

    # extracted from reader.read():
    source_content = SOURCE_PATH.read_text(encoding="utf-8")
    document = docutils.utils.new_document(str(SOURCE_PATH), settings)
    parser.parse(source_content, document)
    document.current_source = document.current_line = None
    components = (source, parser, writer, destination)
    document.transformer.populate_from_components(components)
    document.transformer.apply_transforms()

    output = writer.write(document, destination)
    print(output)


def read4():

    # from https://github.com/getpelican/pelican/blob/main/pelican/readers.py#L253

    pub = docutils.core.Publisher(
        writer=docutils.writers.html5_polyglot.Writer(),
        destination_class=docutils.io.StringOutput,
    )
    pub.set_components(
        reader_name="standalone",
        parser_name="restructuredtext",
        writer_name="html",
    )
    pub.process_programmatic_settings(None, EXTRA_PARAMS, None)
    pub.set_source(source_path=str(SOURCE_PATH))
    pub.publish()

    parts = pub.writer.parts
    content = parts.get("body")
    title = parts.get("title")
    print(repr(content))
    print(repr(title))

    document = pub.document
    metadata = parse_metadata(document)
    print(metadata)


if __name__ == "__main__":
    read4()
