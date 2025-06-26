from pathlib import Path

import markdown


class LxmMarkdown(markdown.Markdown):
    def __init__(self, paths_root: Path, **kwargs):
        super().__init__(**kwargs)
        self._paths_root: Path = paths_root

    @property
    def paths_root(self) -> Path:
        return self._paths_root

    def mk_path_abs(self, rel_path: Path) -> Path:
        if self._paths_root:
            return self._paths_root.joinpath(rel_path).resolve()
        return rel_path
