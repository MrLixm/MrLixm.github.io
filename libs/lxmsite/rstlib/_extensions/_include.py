import docutils.parsers.rst.directives.misc
from docutils.parsers.rst.directives.misc import Include as _Include

from ._pygments import PygmentsCode


class Include(_Include):
    def run(self):
        # monkey-patch seems the most simple, to avoid having to rewrite a lot of code
        backup = docutils.parsers.rst.directives.misc.CodeBlock
        setattr(docutils.parsers.rst.directives.misc, "CodeBlock", PygmentsCode)
        try:
            node = super().run()
        finally:
            setattr(docutils.parsers.rst.directives.misc, "CodeBlock", backup)
        return node
