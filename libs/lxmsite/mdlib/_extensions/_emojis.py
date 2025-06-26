import os
from pathlib import Path
from xml.etree import ElementTree

from markdown.inlinepatterns import InlineProcessor


class EmojiInlineProcessor(InlineProcessor):
    """
    Args:
        emojis_dir: filesystem path to an existing directory with emoji image insides.
        relative_root:
            fileystem path to an existing directory with the same root as the emojis_dir
            and that will be used to create relative image uris.
        md: markdown parser instance
    """

    PATTERN = r":emoji:\(([+\-\w]+)\)"

    def __init__(
        self,
        emojis_dir: Path,
        relative_root: Path,
        md=None,
    ):

        super().__init__(self.PATTERN, md=md)
        self._emojis_dir = emojis_dir
        self._relative_root = relative_root

    def _get_emoji_path(self, name: str) -> Path:
        if not self._emojis_dir.exists():
            raise FileNotFoundError(
                f"Provided emojis_dir '{self._emojis_dir}' does not exist.'"
            )

        emoji_path: list[Path] = list(self._emojis_dir.glob(f"{name}.*"))
        if not emoji_path:
            raise ValueError(
                f"No emoji with name '{name}' found in '{self._emojis_dir}'"
            )
        emoji_path: Path = emoji_path[0]
        return emoji_path

    def handleMatch(self, m, data):
        emoji_name = m.group(1)
        emoji_path = self._get_emoji_path(emoji_name)

        alt_text_path: Path = emoji_path.with_suffix(".alt.txt")
        alt_text: str = alt_text_path.read_text() if alt_text_path.exists() else ""

        # make path relative
        emoji_path = Path(os.path.relpath(emoji_path, self._relative_root))

        node = ElementTree.Element("img")
        node.set("src", emoji_path.as_posix())
        node.set("alt", alt_text)
        node.set("title", emoji_path.stem)
        node.set("class", "emoji-role inline")

        return node, m.start(0), m.end(0)

    def register(self, priority: int):
        self.md.inlinePatterns.register(self, "emoji", priority)
