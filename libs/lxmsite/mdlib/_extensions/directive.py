import abc
import copy
import dataclasses
import re
from typing import TypeVar, Generic, Any

import markdown.blockprocessors
from xml.etree import ElementTree

from lxmsite.mdlib._md import LxmMarkdown

T = TypeVar("T")


class BaseOption(abc.ABC, Generic[T]):
    """
    Abstract class for the developer to configure its directive options.
    """

    def __init__(self, default: T):
        self.default = default

    @abc.abstractmethod
    def unserialize(self, value: str) -> T:
        pass


class StrOption(BaseOption[str]):
    def unserialize(self, value: str) -> str:
        return value


class StrArrayOption(BaseOption[list[str]]):
    def unserialize(self, value: str) -> list[str]:
        return value.split(",")


class IntOption(BaseOption[int]):
    def unserialize(self, value: str) -> int:
        return int(value)


class FloatOption(BaseOption[float]):
    def unserialize(self, value: str) -> float:
        return float(value)


class FloatArrayOption(BaseOption[list[float]]):
    def unserialize(self, value: str) -> list[float]:
        return [float(v) for v in value.split(",")]


class BoolOption(BaseOption[bool]):
    def unserialize(self, value: str) -> bool:
        return True if value in ["true", "1"] else False


class BaseDirectiveError(Exception):
    def __init__(self, directive: "BaseDirective", message: str):
        self.directive = directive
        super().__init__(message)

    def __str__(self):
        base = super().__str__()
        return f"[directive={self.directive.name}] " + base


class DirectiveArgumentError(BaseDirectiveError):
    pass


class DirectiveOptionError(BaseDirectiveError):
    pass


class DirectiveContentError(BaseDirectiveError):
    pass


@dataclasses.dataclass
class ParsedDirective:
    """
    The result of a directive parsed from a markdow document.
    """

    arguments: list[str]
    """
    mandatory position arguments 
    """

    options: dict[str, Any]
    """
    optional named arguments
    """

    content: str | None
    """
    optional arbitrary multi-line text that can contain additional markdown to be parsed.
    """

    indent: int
    """
    the number of indent characters the directive was started with
    """


class BaseDirective:
    """
    A block processor to parse rst-like directives from a Markdown document.

    The directive must match the configuration given as class variables.

    A directive is structured in a document as follows::

        .. directive-name:: argument1 argument2 ...
            :option1: option's value
            :option2: option's value
                that can span multiple lines
                if indented.

            "content": with an arbitrary
            bumber of lines that can be

            split as needed.

    """

    name: str = NotImplemented
    expected_arguments: int = NotImplemented
    expected_content: bool = NotImplemented
    options_schema: dict[str, BaseOption] = NotImplemented

    def __new__(cls, *args, **kwargs):
        for var in ["name", "expected_arguments", "expected_content", "options_schema"]:
            if getattr(cls, var) is NotImplemented:
                raise NotImplementedError(
                    f"Developer missed implementation of class variable '{var}'"
                )
        return super().__new__(cls)

    @property
    def _tab_length(self):
        return 4

    def is_block_directive_start(self, block: str) -> bool:
        pattern = re.compile(rf" *\.\. {self.name}::")
        return True if pattern.match(block) else False

    def parse_blocks(self, blocks: list[str]) -> ParsedDirective:
        """
        Iterate and mutate the given blocks to extract the first directive it finds.
        """
        blocks[:] = "\n\n".join(blocks).split("\n")
        directive = self.parse_lines(lines=blocks)
        blocks[:] = "\n".join(blocks).split("\n\n")
        return directive

    def parse_lines(self, lines: list[str]) -> ParsedDirective:
        """
        Iterate and mutate the given lines to extract the first directive it finds.
        """
        first_line = lines.pop(0)
        global_indent = len(first_line) - len(first_line.lstrip())
        arguments: list[str] = first_line.split("::")[-1].strip(" ").split(" ")
        arguments = [] if arguments[0] == "" else arguments
        if not len(arguments) == self.expected_arguments:
            raise DirectiveArgumentError(
                directive=self,
                message=f"Expected {self.expected_arguments} arguments, "
                f"got {len(arguments)}: '{arguments}'",
            )

        options: dict[str, Any] = {}
        content: str = ""
        previous_line = None
        previous_option: str | None = None
        lvl1_indent = " " * (self._tab_length + global_indent)
        lvl2_indent = lvl1_indent * 2

        while lines:

            if previous_line is not None:
                previous_line = line
            line = lines.pop(0)
            if previous_line is None:
                previous_line = line

            if not line:
                if content:
                    content += "\n"
                continue

            # check if the directive has ended (we are not in the indent)
            if not line.startswith(lvl1_indent):
                lines.insert(0, line)
                if previous_line.strip() == "":
                    lines.insert(0, previous_line)
                break

            if content:
                content += line + "\n"
                continue

            sline = line.strip(" ")
            line_split = sline.split(":", 2)
            if sline.startswith(":") and len(line_split) == 3:
                _, name, value = line_split
                if name not in self.options_schema:
                    raise DirectiveOptionError(
                        directive=self,
                        message=f"Specified unknown option '{name}' from '{sline}'",
                    )
                options[name] = value.strip(" ")
                previous_option = name
                continue

            # check if the line is part of a multi-line option
            if line.startswith(lvl2_indent):
                if not previous_option:
                    content += lvl1_indent + sline + "\n"
                    continue

                newline = "\n" if previous_line.strip() else "\n\n"
                options[previous_option] = options[previous_option] + newline + sline
                continue

            previous_option = None
            content += line + "\n"
            continue

        content = content.rstrip("\n")
        if not content and self.expected_content:
            raise DirectiveContentError(
                directive=self,
                message=f"Expected content got none for directive '{first_line}'",
            )
        content = "\n".join([line[self._tab_length :] for line in content.split("\n")])

        for option_name, option in self.options_schema.items():
            if option_name in options:
                option_value = options[option_name]
                try:
                    options[option_name] = option.unserialize(option_value)
                except Exception as error:
                    raise DirectiveOptionError(
                        directive=self,
                        message=f"Could not unserialize option '{option_name}' with value "
                        f"'{option_value}' as '{type(option).__name__}': {error}",
                    ) from error
            else:
                options[option_name] = copy.copy(option.default)

        return ParsedDirective(
            arguments=arguments,
            options=options,
            content=content or None,
            indent=global_indent,
        )


class BaseDirectiveBlock(
    markdown.blockprocessors.BlockProcessor,
    BaseDirective,
    abc.ABC,
):
    @property
    def md(self) -> LxmMarkdown:
        # noinspection PyTypeChecker
        return self.parser.md

    @property
    def _tab_length(self):
        return self.tab_length

    def test(self, parent: ElementTree.Element, block: str):
        return self.is_block_directive_start(block)

    def register(self, priority):
        self.parser.blockprocessors.register(self, self.name, priority)
