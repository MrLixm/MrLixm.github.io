import re

from docutils import nodes, utils
import docutils.parsers.rst.roles


# intentional lowercase name because used to call method in the Translator
# noinspection PyPep8Naming
class abbreviation(nodes.Inline, nodes.TextElement):
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
    text = utils.unescape(text)
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
