import lxmsite.mdlib


def test__read__mddoc1(resources_dir):
    doc1 = resources_dir / "mddoc1.md"
    document = lxmsite.mdlib.read_markdown(doc1, settings={})
    assert document.title == "hello world ! (and mom)"
    assert document.metadata == {
        "image": "somepath.jpg",
        "description": "this is some very long text that wraps multiple line to test the multiline feature.",
        "reminder": "drink water !",
    }
    assert document.html.startswith("<h1>hello")
    assert document.html.endswith("great</p>")
    print(document.html)
