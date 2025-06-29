from xml.etree import ElementTree

import markdown
import pytest

from lxmsite.mdlib._extensions import directive as Directive


def test__BaseDirectiveBlock__mddoc2(resources_dir):

    class Test1Directive(Directive.BaseDirectiveBlock):
        name = "test1"
        expected_arguments = 2
        expected_content = True
        options_schema = {"option1": Directive.StrOption("defaultA")}

        def __init__(self, parser, result_storage: list):
            super().__init__(parser)
            self._storage: list = result_storage

        def run(self, parent: ElementTree.Element, blocks: list[str]):
            directive = self.parse_blocks(blocks)
            self._storage.append(directive)

    class Test2Directive(Test1Directive):
        name = "test2"
        expected_arguments = 0
        expected_content = False
        options_schema = {
            "option1": Directive.StrOption("defaultA"),
            "option2": Directive.StrOption("defaultB"),
        }

    class Test3Directive(Test1Directive):
        name = "test3"
        expected_arguments = 2
        expected_content = False
        options_schema = {}

    reader = markdown.Markdown()
    directive_test1_results: list[Directive.ParsedDirective] = []
    directive_test1 = Test1Directive(reader.parser, directive_test1_results)
    directive_test2_results: list[Directive.ParsedDirective] = []
    directive_test2 = Test2Directive(reader.parser, directive_test2_results)
    directive_test3_results: list[Directive.ParsedDirective] = []
    directive_test3 = Test3Directive(reader.parser, directive_test3_results)
    reader.parser.blockprocessors.register(directive_test1, "test1", 20)
    reader.parser.blockprocessors.register(directive_test2, "test2", 19)
    reader.parser.blockprocessors.register(directive_test3, "test3", 18)

    doc2path = resources_dir / "mddoc2.md"
    doc2 = doc2path.read_text("utf-8")
    result = reader.convert(doc2)

    assert len(directive_test1_results) == 4
    assert len(directive_test2_results) == 3
    assert len(directive_test3_results) == 2

    # test1

    assert directive_test1_results[0].arguments == ["arg1", "arg2"]
    assert directive_test1_results[0].options == {"option1": "valueA"}
    assert directive_test1_results[0].content == "content line 1\ncontent line 3"

    assert directive_test1_results[1].arguments == ["arg3", "arg4"]
    assert directive_test1_results[1].options == {"option1": "defaultA"}
    assert directive_test1_results[1].content == "content line 1\ncontent line 3"

    assert directive_test1_results[2].arguments == ["arg5", "arg6"]
    assert directive_test1_results[2].options == {"option1": "defaultA"}
    assert directive_test1_results[2].content == "content line 1\ncontent line 3"

    assert directive_test1_results[3].arguments == ["arg7", "arg8"]
    assert directive_test1_results[3].options == {"option1": "defaultA"}
    assert directive_test1_results[3].content == (
        "    content line 1\ncontent line 3\n    content line4\ncontent line5"
    )

    # test2

    assert directive_test2_results[0].arguments == []
    assert directive_test2_results[0].options == {
        "option1": "value1",
        "option2": "value2",
    }
    assert directive_test2_results[0].content is None

    assert directive_test2_results[1].arguments == []
    assert directive_test2_results[1].options == {
        "option1": "valueE",
        "option2": "valueF",
    }
    assert directive_test2_results[1].content is None

    assert directive_test2_results[2].arguments == []
    assert directive_test2_results[2].options == {
        "option1": "this is some very long text that wraps multiple line\nto test the multiline feature.",
        "option2": "valueG",
    }
    assert directive_test2_results[2].content is None

    # test3

    assert directive_test3_results[0].arguments == ["argA", "argB"]
    assert directive_test3_results[0].options == {}
    assert directive_test3_results[0].content is None

    assert directive_test3_results[1].arguments == ["argC", "argD"]
    assert directive_test3_results[1].options == {}
    assert directive_test3_results[1].content is None

    # make sure parsed directives are not included in the ouput

    assert result == (
        "<h1>hello world 2</h1>\n"
        "<p>Time to test directives.</p>\n"
        "<ul>\n"
        "<li>because I can</li>\n"
        "<li>yes !</li>\n"
        "</ul>\n"
        "<p>intermediate text before test2</p>\n"
        "<p>text without line break</p>\n"
        "<p>start of another paragraph</p>"
    )


def test__BaseDirectiveBlock__options():

    class AlphaDirective(Directive.BaseDirectiveBlock):
        name = "alpha"
        expected_arguments = 0
        expected_content = False
        options_schema = {
            "option-str": Directive.StrOption("defaultA"),
            "option-int": Directive.IntOption(666),
            "option-bool": Directive.BoolOption(True),
            "option-strlist": Directive.StrArrayOption(["a", "b"]),
        }

        def __init__(self, parser, result_storage: list):
            super().__init__(parser)
            self._storage: list = result_storage

        def run(self, parent: ElementTree.Element, blocks: list[str]):
            directive = self.parse_blocks(blocks)
            self._storage.append(directive)

    text1 = """
# hello

some subheading

.. alpha::
    :option-str: @ UWU @ ! 
    :option-int: 32
    :option-bool: 1
    :option-strlist: mango,coco,banana

some paragraph

.. alpha::
    :option-str: hellow world !
    :option-bool: False

    """

    reader = markdown.Markdown()
    directive_alpha_results: list[Directive.ParsedDirective] = []
    directive_alpha = AlphaDirective(reader.parser, directive_alpha_results)
    reader.parser.blockprocessors.register(directive_alpha, "alpha", 20)

    reader.convert(text1)

    assert len(directive_alpha_results) == 2

    assert directive_alpha_results[0].options == {
        "option-str": "@ UWU @ !",
        "option-int": 32,
        "option-bool": True,
        "option-strlist": ["mango", "coco", "banana"],
    }
    assert directive_alpha_results[1].options == {
        "option-str": "hellow world !",
        "option-int": 666,
        "option-bool": False,
        "option-strlist": ["a", "b"],
    }

    text2 = """
# hello

some subheading

.. alpha::
    :option-str: @ UWU @ ! 
    :option-NOTEXIST: oops

    """

    with pytest.raises(Directive.DirectiveOptionError) as error:
        reader.convert(text2)

    print(error.value)
    assert "NOTEXIST" in str(error.value)

    text3 = """
# hello

some subheading

.. alpha::
    :option-int: UWU

    """

    with pytest.raises(Directive.DirectiveOptionError) as error:
        reader.convert(text3)

    print(error.value)
    assert "invalid literal for int" in str(error.value)
