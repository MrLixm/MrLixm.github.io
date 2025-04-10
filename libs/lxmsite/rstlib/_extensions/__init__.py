from . import _abbreviation
from . import _pygments
from . import _admonitions
from ._admonitions import AdmonitionsTransform
from ._links import LinksTransform


def register_extensions():

    from docutils.parsers.rst.roles import register_local_role

    register_local_role("abbr", _abbreviation.abbr_role)

    from docutils.parsers.rst.directives import register_directive

    register_directive("code", _pygments.Pygments)
    register_directive("code-block", _pygments.Pygments)

    register_directive("attention", _admonitions.Attention)
    register_directive("caution", _admonitions.Caution)
    register_directive("danger", _admonitions.Danger)
    register_directive("error", _admonitions.Error)
    register_directive("hint", _admonitions.Hint)
    register_directive("important", _admonitions.Important)
    register_directive("note", _admonitions.Note)
    register_directive("tip", _admonitions.Tip)
    register_directive("warning", _admonitions.Warning)
    register_directive("admonition", _admonitions.Admonition)

    register_directive("highlight", _admonitions.HighlightBlock)
