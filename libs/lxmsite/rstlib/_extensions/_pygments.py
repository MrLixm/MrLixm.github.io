import docutils.nodes
import docutils.utils
import docutils.parsers.rst.roles
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives

import pygments
import pygments.lexers
import pygments.formatters


class Pygments(Directive):
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
        "nobackground": directives.flag,
        "nowrap": directives.flag,
        "tagsfile": directives.unchanged,
        "tagurlformat": directives.unchanged,
    }
    has_content = True

    def run(self):
        self.assert_has_content()
        content = "\n".join(self.content)

        try:
            if self.arguments:
                lexer_name = self.arguments[0]
                lexer = pygments.lexers.get_lexer_by_name(lexer_name)
            else:
                lexer = pygments.lexers.guess_lexer(content)
        except pygments.lexers.ClassNotFound:
            lexer = pygments.lexers.TextLexer()

        if "linenos" in self.options and self.options["linenos"] not in (
            "table",
            "inline",
        ):
            if self.options["linenos"] == "none":
                self.options.pop("linenos")
            else:
                self.options["linenos"] = "table"

        # flags get a None value assigned by docutils, pygments will need a boolean
        enabled_flags = [
            option
            for option, optiontype in self.option_spec.items()
            if optiontype is directives.flag and option in self.options
        ]
        for flag in enabled_flags:
            self.options[flag] = True

        formatter = pygments.formatters.HtmlFormatter(noclasses=False, **self.options)
        parsed = pygments.highlight(content, lexer, formatter)
        return [docutils.nodes.raw("", parsed, format="html")]
