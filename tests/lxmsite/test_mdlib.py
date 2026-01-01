import lxmsite.mdlib


def test__read__mddoc1(resources_dir):
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
        '<h2 id="conclusion"><a href="#conclusion">conclusion</a></h2>\n'
        "<p>this was not great</p>"
    )
