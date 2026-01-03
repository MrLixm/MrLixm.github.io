from lxmsite.mdlib import LxmMarkdown
from lxmsite.mdlib._extensions import IncludeDirectivePreprocessor


def test__IncludeDirectivePreprocessor__superfences(tmp_path):

    file1path = tmp_path / "file1.py"
    file1path.write_text(
        (
            "from pathlib import Path\n"
            "import OpenImageIO as oiio\n"
            "\n"
            "def read_image(path: Path) -> oiio.ImageBuf:\n"
            "    return oiio.ImageBuf(str(path))\n"
            "# invisible comment"
        )
    )

    text1 = """
some heading

.. include:: file1.py
    :code: python {title="file1.py"}
    :lines: 1:-1

some paragraph

    """

    reader = LxmMarkdown(paths_root=tmp_path, extensions=["pymdownx.superfences"])
    directive = IncludeDirectivePreprocessor(reader)
    directive.register(200)

    result = reader.convert(text1)

    print(result)
    assert result == (
        "<p>some heading</p>\n"
        '<div class="highlight"><span class="filename">file1.py</span>'
        '<pre><span></span><code><span class="kn">import</span>'
        '<span class="w"> </span><span class="nn">OpenImageIO</span>'
        '<span class="w"> </span><span class="k">as</span>'
        '<span class="w"> </span><span class="nn">oiio</span>\n'
        "\n"
        '<span class="k">def</span><span class="w"> </span><span '
        'class="nf">read_image</span><span class="p">(</span><span '
        'class="n">path</span><span class="p">:</span> <span '
        'class="n">Path</span><span class="p">)</span> <span class="o">-&gt;</span> '
        '<span class="n">oiio</span><span class="o">.</span><span '
        'class="n">ImageBuf</span><span class="p">:</span>\n'
        '    <span class="k">return</span> <span class="n">oiio</span><span '
        'class="o">.</span><span class="n">ImageBuf</span><span '
        'class="p">(</span><span class="nb">str</span><span class="p">(</span><span '
        'class="n">path</span><span class="p">))</span>\n'
        "</code></pre></div>\n"
        "<p>some paragraph</p>"
    )

    text2 = """
some heading

.. include:: file1.py
    :code: python {title="file1.py"}
    :lines: 4

some paragraph

    """

    result = reader.convert(text2)
    assert result == (
        "<p>some heading</p>\n"
        '<div class="highlight"><span '
        'class="filename">file1.py</span><pre><span></span><code><span '
        'class="k">def</span><span class="w"> </span><span '
        'class="nf">read_image</span><span class="p">(</span><span '
        'class="n">path</span><span class="p">:</span> <span '
        'class="n">Path</span><span class="p">)</span> <span class="o">-&gt;</span> '
        '<span class="n">oiio</span><span class="o">.</span><span '
        'class="n">ImageBuf</span><span class="p">:</span>\n'
        "</code></pre></div>\n"
        "<p>some paragraph</p>"
    )


def test__IncludeDirectivePreprocessor__nested_markdown(tmp_path):

    file1path = tmp_path / "file1.md"
    file1path.write_text(
        """
**hello** from file1

## other title

and some footer
this line MUST BE ommitted
"""
    )

    text1 = """
some heading

.. include:: file1.md
    :lines: 0:-1

some paragraph

    """

    reader = LxmMarkdown(paths_root=tmp_path)
    directive = IncludeDirectivePreprocessor(reader)
    directive.register(200)

    result = reader.convert(text1)

    print(result)
    assert result == (
        "<p>some heading</p>\n"
        "<p><strong>hello</strong> from file1</p>\n"
        "<h2>other title</h2>\n"
        "<p>and some footer</p>\n"
        "<p>some paragraph</p>"
    )


def test__IncludeDirectivePreprocessor__literal(tmp_path):

    file1path = tmp_path / "file1.md"
    file1path.write_text(
        """
**hello** from file1

## other title

and some footer
this line MUST BE ommitted
"""
    )

    text1 = """
some heading

.. include:: file1.md
    :literal: class="somestuff"
    :lines: 0:-1

some paragraph

    """

    reader = LxmMarkdown(paths_root=tmp_path)
    directive = IncludeDirectivePreprocessor(reader)
    directive.register(200)

    result = reader.convert(text1)

    print(result)
    assert result == (
        "<p>some heading</p>\n"
        '<div class="somestuff">\n'
        "\n"
        "**hello** from file1\n"
        "\n"
        "## other title\n"
        "\n"
        "and some footer\n"
        "</div>\n"
        "\n"
        "<p>some paragraph</p>"
    )


def test__IncludeDirectivePreprocessor__indented(tmp_path):

    file1path = tmp_path / "file1.svg"
    file1path.write_text("""<svg width="64" height="64"></svg>""")

    text1 = """
some heading

!!! hint "indented block"

    first admonition line

    .. include:: file1.svg
        :literal: class="center-block"
    
    will this work ?

some paragraph
    """

    reader = LxmMarkdown(paths_root=tmp_path, extensions=["admonition"])
    directive = IncludeDirectivePreprocessor(reader)
    directive.register(900)

    result = reader.convert(text1)

    print(result)
    assert result == (
        "<p>some heading</p>\n"
        '<div class="admonition hint">\n'
        '<p class="admonition-title">indented block</p>\n'
        "<p>first admonition line</p>\n"
        '<p><div class="center-block">\n'
        '<svg width="64" height="64"></svg>\n'
        "</div></p>\n"
        "<p>will this work ?</p>\n"
        "</div>\n"
        "<p>some paragraph</p>"
    )
