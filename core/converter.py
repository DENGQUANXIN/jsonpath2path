from __future__ import annotations

from typing import Callable

from jsonpath_ng import DatumInContext

from .assigner import SlotAssigner
from jsonpath2path.common.exceptions import *
from jsonpath2path.common.utils import get_edge, get_node
from jsonpath2path import convert
from jsonpath2path.common.entities import ConverterData, JsonPathMatchIndex


class NodeConverter(ConverterData):
    def __init__(self):
        super().__init__()
        self._user_defined_convert_map: dict[str, Callable[[ConverterData, any], None]] = {}

    def source(self, matches: list[DatumInContext]) -> NodeConverter:
        if matches is None or len(matches) == 0:
            raise InvalidMatchError("No matches to convert")

        # Read-only in principle, used to retrieve original json node information.
        self._match_index = JsonPathMatchIndex(matches)

        self.edges = [get_edge(match) for match in matches]
        self.nodes = [get_node(match) for match in matches]
        return self

    def to(self, assigner: SlotAssigner) -> SlotAssigner:
        if assigner is None:
            raise InvalidAssigner("Assigner CANNOT be None")
        assigner.source(self.edges, self.nodes)
        return assigner

    def convert(self, convert_name: str, *args, **kwargs) -> NodeConverter:
        convert_func = self._user_defined_convert_map.get(convert_name)
        if convert_func is not None:
            convert_func(self, *args, **kwargs)
            return self

        convert_func = convert.get_convert_func(convert_name)
        if convert_func is not None:
            convert_func(self, *args, **kwargs)
            return self

        raise AttributeError(f"Invalid convert function {convert_name}")

    def register(self, func_name: str, convert_func: Callable[[ConverterData, any], None]) -> None:
        if func_name in self._user_defined_convert_map or func_name in self._internal_convert_map:
            raise AttributeError(f"convert function {func_name} already existed")
        self._user_defined_convert_map[func_name] = convert_func

    def has(self, func_name: str) -> bool:
        return (func_name in self._user_defined_convert_map) or (convert.get_convert_func(func_name) is not None)

    def __str__(self):
        return f"NodeConverter(data={str(zip(self.edges, self.nodes))})"
