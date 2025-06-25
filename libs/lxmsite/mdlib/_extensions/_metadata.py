import markdown.preprocessors


class MetadataPreprocessor(markdown.preprocessors.Preprocessor):
    """
    Extract the metadata from the document.

    Metadata can only be defined at one arbitrary place in the document (usually the top).

    Each line is either a new key with the syntax ``:key: value`` either the continuation
    of a previous line with a minimum of 2 indents.

    The first blank line after defining at least one metadata will stop the parsing.
    """

    metadata: dict[str, str] = {}

    def run(self, lines: list[str]) -> list[str]:
        meta: dict[str, str] = {}
        last_key: str | None = None
        lines_buffer = []

        while lines:
            line = lines.pop(0)
            # stop parsing metadata on the first blank line after metadata has been found
            if last_key and line.strip() == "":
                break

            # check if the line is a continuation of the previous line
            if last_key and line.startswith("  "):
                meta[last_key] = meta[last_key] + " " + line.strip(" ")
                continue

            line_split = line.split(":", 2)
            # check if the line is a metadata line
            if not len(line_split) == 3:
                lines_buffer.append(line)
                if last_key:
                    break
                else:
                    continue

            _, key, value = line_split
            last_key = key
            meta[last_key] = value.strip(" ")

        self.metadata = meta
        return lines_buffer + lines

    def register(self) -> None:
        self.md.preprocessors.register(self, "meta", priority=27)
