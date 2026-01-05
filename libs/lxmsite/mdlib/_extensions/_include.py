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
        "target": Directive.StrOption(""),
        "encoding": Directive.StrOption("utf-8"),
        "literal": Directive.StrOption(""),
    }

    md: LxmMarkdown

    def parse_directive(self, directive: Directive.ParsedDirective):
        u_file = Path(directive.arguments[0])
        u_code: str = directive.options["code"]
        u_lines: str = directive.options["lines"].strip(" ")
        u_encoding: str = directive.options["encoding"]
        u_literal: bool = directive.options["literal"]
        u_target: str = directive.options["target"]

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
            if u_target:
                new_lines = (
                    [f'<a href="{u_target}" class="included">'] + new_lines + [f"</a>"]
                )

        elif u_literal:
            if u_target:
                new_lines = (
                    [f'<a href="{u_target}" class="included">'] + new_lines + [f"</a>"]
                )
            new_lines = [f"<div {u_literal}>"] + new_lines + ["</div>"]

        return new_lines

    def run(self, lines: list[str]) -> list[str]:
        blocks = "\n".join(lines).split("\n\n")
        new_blocks = []
        while blocks:
            block = blocks.pop(0)
            if not self.is_block_directive_start(block):
                new_blocks.append(block)
                continue

            blocks.insert(0, block)
            directive = self.parse_blocks(blocks)
            directive_new_lines = self.parse_directive(directive)
            indent = " " * directive.indent
            directive_new_blocks: str = indent + f"\n{indent}".join(directive_new_lines)
            directive_new_blocks: list[str] = directive_new_blocks.split("\n\n")
            blocks[:] = directive_new_blocks + blocks

        new_lines = "\n\n".join(new_blocks).split("\n")
        return new_lines

    def register(self, priority: int):
        self.md.preprocessors.register(self, self.name, priority)
