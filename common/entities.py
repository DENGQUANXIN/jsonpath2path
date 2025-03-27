from __future__ import annotations

from dataclasses import dataclass

from jsonpath_ng import DatumInContext

from jsonpath2path.common.exceptions import InvalidDataError
from jsonpath2path.common.utils import get_node, get_edge


class JsonPathMatchIndex:
    """Read-Only wrapper for JSONPath matching results."""
    def __init__(self, matches: list[DatumInContext]):
        if matches is None or len(matches) == 0:
            raise InvalidDataError("No matches to convert")
        self._match_index = matches

    def get_value(self, idx: int) -> dict | list | None:
        if idx < len(self._match_index):
            return get_node(self._match_index[idx])

    def get_context_value(self, idx: int):
        if idx < len(self._match_index):
            return get_node(self._match_index[idx].context)

    def get_context_edge(self, idx: int):
        if idx < len(self._match_index):
            return get_edge(self._match_index[idx].context)


@dataclass
class ConverterData:
    """
    Essential data required for the converter.
    """
    # Picked JSON nodes and its associated edges.
    edges: list = None
    nodes: list = None
    # Raw JSONPath matched data, read-only.
    _match_index: JsonPathMatchIndex = None
