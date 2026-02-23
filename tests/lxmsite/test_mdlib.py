import lxmsite.mdlib


def test__read_markdown__mddoc1(resources_dir):
    doc1 = resources_dir / "mddoc1.md"
    doc1_txt = doc1.read_text("utf-8")
    document = lxmsite.mdlib.read_markdown(doc1_txt, doc1.parent, extension_settings={})
    assert document.title == "hello world ! (and mom)"
    assert document.metadata == {
        "image": "somepath.jpg",
        "description": "this is some very long text that wraps multiple line to test the multiline feature.",
        "reminder": "drink water !",
        "multi-line2": "but now we start on the next line ! what do you think ?",
    }
    assert document.html == (
        "<p>What could we learn today ?</p>\n"
        '<h2 id="introduction"><a href="#introduction">introduction</a></h2>\n'
        "<p>probably some interesting stuff</p>\n"
        '<h2 id="examples"><a href="#examples">examples</a></h2>\n'
        "<p>SOme examples to scrumble</p>\n"
        '<div class="highlight"><pre><span></span><code><span class="nb">print</span><span class="p">(</span><span class="s2">&quot;hello world&quot;</span><span class="p">)</span>\n'
        "</code></pre></div>\n"
        '<h3 id="making-smoothies"><a href="#making-smoothies">making smoothies</a></h3>\n'
        "<p>blending the latent smoothness of the fruits</p>\n"
        '<div id="smoothies">\n'
        "idk\n"
        "</div>\n"
        "\n"
        '<h2 id="conclusion"><a href="#conclusion">conclusion</a></h2>\n'
        "<p>this was not great</p>"
    )
    assert len(document.blocks) == 5
    assert (
        document.blocks["introduction"]
        == '<h2 id="introduction"><a href="#introduction">introduction</a></h2>'
    )
    assert document.blocks["smoothies"] == '<div id="smoothies">\nidk\n</div>'


TEST_DOC = """
# welcome to unittesting

this is some general description

<div id="first-block" markdown="1">

Welcome to *unittesting*, the place to test ! We got:

- `tests`
- more `tests`
- acually nothing else than `tests`

!!! warning

    tests, tests are important, don't forget tests

crazy right ?
</div>

<section id="second-block" markdown="1">
<div id="some-stuff">
doesn't really matter
</div>
<strong>fuck the system</strong>
</section>

some footer because who doesn't like foots ?
"""


def test__read_markdown__blocks(tmp_path):
    document = lxmsite.mdlib.read_markdown(TEST_DOC, tmp_path, extension_settings={})
    assert len(document.blocks) == 2
    assert "first-block" in document.blocks
    assert "second-block" in document.blocks
    assert document.blocks["second-block"] == (
        '<section id="second-block">\n'
        '<div id="some-stuff">\n'
        "doesn't really matter\n"
        "</div>\n"
        "<p><strong>fuck the system</strong></p>\n"
        "</section>"
    )

    document = lxmsite.mdlib.read_markdown(
        "# hello world\n", tmp_path, extension_settings={}
    )
    assert not document.blocks
