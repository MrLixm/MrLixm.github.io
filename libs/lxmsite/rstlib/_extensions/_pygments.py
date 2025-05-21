import docutils.nodes
import docutils.utils
import docutils.parsers.rst.roles
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives

import pygments
import pygments.lexers
import pygments.formatters


class PygmentsHTMLFormatter(pygments.formatters.HtmlFormatter):

    # subclassed to bypass all wrapper blocks; we create thos eourselves with docutils API

    def wrap(self, source):
        yield from source

    def _wrap_div(self, inner):
        yield from inner


def parse_code_to_node(
    code: str,
    lexer_name: str | None = None,
    options: dict = None,
) -> docutils.nodes.literal_block:
    """
    Parse a piece of arbitrary code to a docutils node using Pygments.

    Args:
        code: the code to parse
        lexer_name: name of the lnaguage, as supported by pygments.
        options: pygments html formatter options.
    """
    try:
        if lexer_name:
            lexer = pygments.lexers.get_lexer_by_name(lexer_name)
        else:
            lexer = pygments.lexers.guess_lexer(code)
    except pygments.lexers.ClassNotFound:
        lexer = pygments.lexers.TextLexer()
        lexer_name = "unknown"

    options = options or {}
    formatter = PygmentsHTMLFormatter(
        noclasses=False,
        nowrap=False,
        **options,
    )
    parsed = pygments.highlight(code, lexer, formatter)
    parsed = docutils.nodes.raw(code, parsed, format="html")
    node = docutils.nodes.literal_block(
        rawsource="",
        text="",
        classes=["highlight"],
        title=f"Block of code in {lexer_name} language.",
    )
    node += parsed
    return node


class PygmentsCode(Directive):
    """Source code syntax highlighting."""

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    # see https://pygments.org/docs/formatters/#HtmlFormatter
    option_spec = {
        "anchorlinenos": directives.flag,
        "classprefix": directives.unchanged,
        "hl_lines": directives.unchanged,
        "lineanchors": directives.unchanged,
        "linenos": directives.unchanged,
        "linenospecial": directives.nonnegative_int,
        "linenostart": directives.nonnegative_int,
        "linenostep": directives.nonnegative_int,
        "lineseparator": directives.unchanged,
        "linespans": directives.unchanged,
        "tagsfile": directives.unchanged,
        "tagurlformat": directives.unchanged,
    }
    has_content = True

    def run(self):
        self.assert_has_content()
        content = "\n".join(self.content)

        if "linenos" in self.options:
            if self.options["linenos"] not in ("table", "inline"):
                self.options.pop("linenos")

        # flags get a None value assigned by docutils, pygments will need a boolean
        enabled_flags = [
            option
            for option, optiontype in self.option_spec.items()
            if optiontype is directives.flag and option in self.options
        ]
        for flag in enabled_flags:
            self.options[flag] = True

        lexer_name = self.arguments[0] if self.arguments else None
        node = parse_code_to_node(
            code=content,
            lexer_name=lexer_name,
            options=self.options,
        )
        return [node]
