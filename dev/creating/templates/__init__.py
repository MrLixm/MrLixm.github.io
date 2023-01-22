from pathlib import Path

TEMPLATES_DIRECTORY = Path(__file__).parent


def get_template(name: str, extension: str = ".rst") -> Path:
    """

    Args:
        name: file name of the template, without the extension.
        extension: extension of the template, with the dot delimiter.

    Returns:
        absolute file path to the template, might not exist.
    """
    return TEMPLATES_DIRECTORY / (name + extension)


article_rst = get_template("article")
assert article_rst.exists(), article_rst
