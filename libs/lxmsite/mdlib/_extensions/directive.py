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


class DirectiveArgumentError(Exception):
    pass


class DirectiveOptionError(Exception):
    pass


class DirectiveContentError(Exception):
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
        pattern = re.compile(rf"\.\. {self.name}::")
        return True if pattern.match(block) else False

    def parse_blocks(self, blocks: list[str]) -> ParsedDirective:
        """
        Iterate and mutate the given blocks to extract the first directive it finds.
        """
        first_line = blocks[0].splitlines()[0]
        arguments: list[str] = first_line.split("::")[-1].strip(" ").split(" ")
        arguments = [] if arguments[0] == "" else arguments
        if not len(arguments) == self.expected_arguments:
            raise DirectiveArgumentError(
                f"Expected {self.expected_arguments} arguments, "
                f"got {len(arguments)}: '{arguments}'"
            )
        blocks[0] = blocks[0].removeprefix(first_line).removeprefix("\n")

        options: dict[str, Any] = {}
        content: str = ""

        previous_option: str | None = None

        while blocks:
            block = blocks.pop(0)

            if not block:
                continue

            # check if the directive has ended (we are not in the indent)
            if not block.startswith(" " * self._tab_length):
                blocks.insert(0, block)
                break

            for line in block.splitlines():

                sline = line.strip(" ")
                line_split = sline.split(":", 2)
                if len(line_split) == 3:
                    _, name, value = line_split
                    if name not in self.options_schema:
                        raise DirectiveOptionError(
                            f"Specified unknown option '{sline}'"
                        )
                    options[name] = value.strip(" ")
                    previous_option = name
                    continue

                # check if the line is part of a multi-line option
                if line.startswith(" " * self._tab_length * 2):
                    if not previous_option:
                        content += sline + "\n"
                        continue
                    newline = "\n" if block.startswith(line) else " "
                    options[previous_option] = (
                        options[previous_option] + newline + sline
                    )
                    continue

                content += sline + "\n"
                continue

        content = content.rstrip("\n")
        if not content and self.expected_content:
            raise DirectiveContentError(
                f"Expected content got none for directive '{first_line}'"
            )

        for option_name, option in self.options_schema.items():
            if option_name in options:
                option_value = options[option_name]
                try:
                    options[option_name] = option.unserialize(option_value)
                except Exception as error:
                    raise DirectiveOptionError(
                        f"Could not unserialize option '{option_name}' with value "
                        f"'{option_value}' as '{type(option).__name__}': {error}"
                    ) from error
            else:
                options[option_name] = copy.copy(option.default)

        return ParsedDirective(
            arguments=arguments,
            options=options,
            content=content or None,
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
