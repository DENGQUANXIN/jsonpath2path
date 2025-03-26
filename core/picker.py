from jsonpath_ng.ext import parse

from .converter import NodeConverter
from .utils import get_edge, new_match, del_node


class NodePicker:
    def __init__(self):
        self._matches = None

    def create(self, edges: list[str|int], nodes: list):
        matches = [new_match(edge, node) for edge, node in zip(edges, nodes)]
        self._matches = matches

    def pluck(self, data: dict|list, path: str):
        # Reversing is to prevent list out-of-bounds.
        matches = parse(path).find(data)[::-1]

        for match in matches:
            del_node(data, match)

        self._matches = matches[::-1]

    def copy(self, data: dict|list, path:str):
        self._matches = parse(path).find(data)

    def to(self, converter: NodeConverter):
        converter.source(self._matches)

    def __str__(self):
        return str([(get_edge(match), match.value) for match in self._matches])
