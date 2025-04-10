import re

import docutils.nodes
from docutils.transforms import Transform


class LinksTransform(Transform):
    """
    We tokenize all uris so they can be found more easily to be resolved by an upper process.
    """

    default_priority = 10
    token_start = "%URI%("
    token_end = ")%%"
    token_pattern = re.compile(f"{re.escape(token_start)}(.+){re.escape(token_end)}")

    def apply(self):
        node: docutils.nodes.reference

        def link_condition(n):
            return isinstance(
                n,
                (
                    docutils.nodes.reference,
                    docutils.nodes.citation_reference,
                    docutils.nodes.footnote_reference,
                ),
            )

        for node in self.document.findall(condition=link_condition):
            uri = node.get("refuri")
            if uri:
                node["refuri"] = f"{self.token_start}{uri}{self.token_end}"
