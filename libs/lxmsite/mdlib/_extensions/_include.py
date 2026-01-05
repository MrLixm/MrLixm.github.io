from pathlib import Path

from markdown.preprocessors import Preprocessor
from . import directive as Directive
from .. import LxmMarkdown


class IncludeDirectivePreprocessor(Preprocessor, Directive.BaseDirective):
    """
    Inject the content of a file in the Markdown document.

    If no option is provided, the content is assumed to be a Markdown document that need parsing.

    Available options are:

    * ``code``: the text will be wrapped in a superfence code blocks and the value will be appened to the header.
    * ``lines``:
      an expression that describe the lines to extract from the file.
      It can either be 2 integer seprated by a colon: that's a start-end range
      (you can use negative number, where -1 indicate the last line).
      Or it can be multiple integer separated by a comma, which correspond each to an individual line.
    * ``encoding``: the file encoding used for reading.
    * ``literal``:
      will import the content and wraps it in a <div>. the value
      are appened as attributes of the div tag.

    Here is the Markdown syntax:
    ::

        .. include:: myfile.py
            :code: python {linenums="1" title="myfile.py"}
            :lines: 5-10

    """

    name = "include"
    expected_arguments = 1
    expected_content = False
    options_schema = {
        "code": Directive.StrOption(""),
        "lines": Directive.StrOption(""),
        "encoding": Directive.StrOption("utf-8"),
    }

    md: LxmMarkdown

    def parse_directive(self, directive: Directive.ParsedDirective):
        u_file = Path(directive.arguments[0])
        u_code: str = directive.options["code"]
        u_lines: str = directive.options["lines"].strip(" ")
        u_encoding: str = directive.options["encoding"]

        file_path = self.md.mk_path_abs(u_file)
        if not file_path.exists():
            raise FileNotFoundError(
                f"Given argument '{u_file}' from directive '{self.name}' does not "
                f"resolve to an existing file: {file_path}"
            )
        file_content = file_path.read_text(encoding=u_encoding)

        file_lines = file_content.splitlines()
        new_lines = []
        if not u_lines:
            new_lines = file_lines
        elif len(u_lines.split(":")) == 2:
            line_start, line_end = u_lines.split(":")
            new_lines = file_lines[int(line_start) : int(line_end)]
        else:
            lines = list(map(int, u_lines.strip(",").split(",")))
            for index, line in enumerate(file_lines):
                if index + 1 in lines:
                    new_lines.append(line)

        if u_code:
            new_lines = [f"```{u_code}"] + new_lines + ["```"]

        return new_lines

    def run(self, lines: list[str]) -> list[str]:
        new_lines = []
        while lines:

            line = lines.pop(0)

            # XXX: '#' is used as escape mechanism because this is a preprocessor

            uncommented_line = line.lstrip("#")
            if not self.is_block_directive_start(uncommented_line):
                new_lines.append(line)
                continue

            if line.startswith("#"):
                new_lines.append(line.lstrip("#"))
                continue

            lines.insert(0, line)
            # parse_lines mutate the 'lines' list
            directive = self.parse_lines(lines)
            directive_new_lines = self.parse_directive(directive)
            indent = " " * directive.indent
            new_lines += [indent + line for line in directive_new_lines]

        return new_lines

    def register(self, priority: int):
        self.md.preprocessors.register(self, self.name, priority)
