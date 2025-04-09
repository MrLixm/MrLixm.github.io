import re

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


directives.register_directive("code", Pygments)
directives.register_directive("code-block", Pygments)


# intentional lowercase name because used to call method in the Translator
# noinspection PyPep8Naming
class abbreviation(docutils.nodes.Inline, docutils.nodes.TextElement):
    pass


# see https://docutils.sourceforge.io/docs/howto/rst-roles.html


_abbr_re = re.compile(r"(?P<title>.*) <(?P<explanation>.+)>")


def abbr_role(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner,
    options: dict | None = None,
    content: list[str] | None = None,
) -> tuple[list, list]:
    """

    References:
        - [1] https://github.com/sphinx-doc/sphinx/blob/a6d7ae16739bf92a032a7c4df0297db7cf120ec9/sphinx/roles.py#L464
        - [2] https://github.com/getpelican/pelican/blob/5338f4fac29cbd12174244c38993bbfd70448dfb/pelican/rstdirectives.py#L81

    Args:
        name:
            The local name of the interpreted role, the role name actually used in the document.
        rawtext:
            A string containing the entire interpreted text input,
            including the role and markup. Return it as a problematic node
            linked to a system message if a problem is encountered.
        text:
            The interpreted text content.
        lineno:
            The line number where the text block containing the interpreted text begins.
        inliner:
            The docutils.parsers.rst.states.Inliner object that called role_fn.
            It contains the several attributes useful for error reporting and document tree access.
        options:
            A dictionary of directive options for customization (from the "role" directive),
            to be interpreted by the role function. Used for additional attributes for
            the generated elements and other functionality.
        content:
            A list of strings, the directive content for customization
            (from the "role" directive). To be interpreted by the role function.

    Returns:
        - A list of nodes which will be inserted into the document tree at the point
          where the interpreted role was encountered (can be an empty list).
        - A list of system messages, which will be inserted into the document tree
          immediately after the end of the current block (can also be empty).
    """
    text = docutils.utils.unescape(text)
    matched = _abbr_re.search(text)
    if matched:
        title = matched.group("title")
        explanation = matched.group("explanation")
    else:
        title = text
        explanation = None

    # 'explanation' is a custom attribute retrieved in the HTMLTranslator
    return [abbreviation(rawtext, title, explanation=explanation)], []


def _register_extensions():

    docutils.parsers.rst.roles.register_local_role("abbr", abbr_role)
