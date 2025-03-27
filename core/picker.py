from __future__ import annotations

from copy import deepcopy

from jsonpath_ng.ext import parse

from .converter import NodeConverter
from jsonpath2path.common.exceptions import InvalidNodesError, NodeEdgeNotMatchedError, InvalidJsonPathError
from jsonpath2path.common.utils import get_edge, new_match, is_root, unlink


class NodePicker:
    def __init__(self):
        self._matches = None

    def create(self, edges: list[str|int], nodes: list):
        if nodes is None or len(nodes) == 0:
            raise InvalidNodesError("Create mode requires non-empty `[[edge, value],...]` as source data")
        if edges is None or len(edges) != len(nodes):
            raise NodeEdgeNotMatchedError("Edges and nodes must have same length.")

        # Create JSONPath matches (list of `DatumInContext`)
        matches = [new_match(edge, node) for edge, node in zip(edges, nodes)]
        self._matches = matches

    def pluck(self, data: dict|list, path: str):
        matches = self._match_jsonpath(data, path)[::-1]

        if len(matches) == 1 and is_root(matches[0]): # Root node can only be cleared.
            matches[0].value = deepcopy(matches[0].value)
            data.clear()
        else:
            for match in matches:
                unlink(match)

        self._matches = matches[::-1]

    def copy(self, data: dict|list, path:str):
        self._matches = self._match_jsonpath(data, path)

    def to(self, converter: NodeConverter):
        converter.source(self._matches)

    @staticmethod
    def _match_jsonpath(json_data: dict | list, jsonpath: str):
        try:
            parser = parse(jsonpath)
        except:
            raise InvalidJsonPathError(f"Invalid jsonpath: {jsonpath}")

        # Reversing is to prevent list out-of-bounds.
        matches = parser.find(json_data)
        if matches is None or len(matches) == 0:
            raise InvalidJsonPathError(f"No matches found for `{jsonpath}` of {json_data}")

        return matches

    def __str__(self):
        return f"NodePicker(matches={str([(get_edge(match), match.value) for match in self._matches])})"
