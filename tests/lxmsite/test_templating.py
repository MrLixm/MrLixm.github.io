from lxmsite._templating import mkpagerel
from lxmsite._templating import mksiterel


def test__mkpagerel():
    result = mkpagerel("image.jpg", "blog/test/index.html")
    expected = "../../image.jpg"
    assert result == expected

    result = mkpagerel(".static/main.css", "index.html")
    expected = ".static/main.css"
    assert result == expected

    result = mkpagerel("../.static/main.css", "blog/test")
    expected = "../../.static/main.css"
    assert result == expected

    result = mkpagerel(".", "blog/test.html")
    expected = ".."
    assert result == expected


def test__mksiteabs():
    result = mksiterel("image.jpg", "blog/test/index.html")
    expected = "blog/test/image.jpg"
    assert result == expected

    result = mksiterel(".static/main.css", "index.html")
    expected = ".static/main.css"
    assert result == expected

    result = mksiterel("../.static/main.css", "blog/test")
    expected = ".static/main.css"
    assert result == expected
