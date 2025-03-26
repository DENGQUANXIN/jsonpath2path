from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Callable

from jsonpath_ng import DatumInContext
from jsonpath_ng.ext import parse

from .assigner import SlotAssigner
from .exceptions import *
from .utils import get_edge, get_node, get_path


class JsonPathMatchIndex:
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

def internal_convert_func(func):
    func._is_internal_convert_func = True  # 添加标记
    return func


class InternalNodeConverter:
    def __init__(self):
        self._internal_convert_map: dict[str, Callable[[ConverterData, any], None]] = {}
        # Collect @internal_convert_func methods into a dict.
        for name, method in inspect.getmembers(self, predicate=inspect.isfunction):
            if hasattr(method, '_is_internal_convert_func'):
                self._internal_convert_map[name] = method

    @staticmethod
    @internal_convert_func
    def v_set(data: ConverterData, *args, **kwargs):
        if args is None or len(args) == 0:
            return

        nodes = data.nodes
        for i in range(len(nodes)):
            nodes[i] = args[0]

    @staticmethod
    @internal_convert_func
    def v_sort(data: ConverterData, *args, **kwargs):
        edges, nodes = data.edges, data.nodes
        if args is None or len(args) == 0:
            nodes.sort()
        elif len(args) == 1:
            nodes.sort(reverse=args[0])
        elif len(args) == 2:
            jsonpath = args[1]
            parser = parse(jsonpath)
            nodes.sort(key=lambda node: parser.find(node)[0].value, reverse=args[0])

    @staticmethod
    @internal_convert_func
    def v_add(data: ConverterData, *args, **kwargs):
        edges, nodes = data.edges, data.nodes
        if args is None or len(args) == 0:
            return

        v = args[0]
        jsonpath = "$" if len(args) == 1 else args[1]
        parser = parse(jsonpath)
        for i in range(len(nodes)):
            node = nodes[i]
            if isinstance(node, list) or isinstance(node, dict):
                matches = parser.find(node)
                if matches is None:
                    continue
                for match in matches:
                    match.value += v
            else:
                nodes[i] += v

    @staticmethod
    @internal_convert_func
    def v_wrap_in_list(data: ConverterData, *args, **kwargs):
        edges, nodes = data.edges, data.nodes
        for i in range(len(nodes)):
            node = nodes[i]
            if isinstance(node, list):
                nodes[i] = [nodes[i]]


class NodeConverter(InternalNodeConverter, ConverterData):
    def __init__(self):
        super().__init__()
        self._user_defined_convert_map: dict[str, Callable[[ConverterData, any], None]] = {}

    def source(self, matches: list[DatumInContext]):
        # Read-only in principle, used to retrieve original json node information.
        self._match_index = JsonPathMatchIndex(matches)

        self.edges = [get_edge(match) for match in matches]
        self.nodes = [get_node(match) for match in matches]
        return self

    def to(self, assigner: SlotAssigner):
        assigner.source(self.edges, self.nodes)

    def convert(self, convert_func: str, *args, **kwargs) -> NodeConverter:
        if convert_func in self._internal_convert_map:
            self._internal_convert_map[convert_func](self, *args, **kwargs)
        elif convert_func in self._user_defined_convert_map:
            self._user_defined_convert_map[convert_func](self, *args, **kwargs)
        else:
            raise AttributeError(f"Invalid convert function {convert_func}")

        return self

    def register(self, func_name: str, convert_func: Callable[[ConverterData, any], None]) -> None:
        if func_name in self._user_defined_convert_map or func_name in self._internal_convert_map:
            raise AttributeError(f"convert function {func_name} already existed")
        self._user_defined_convert_map[func_name] = convert_func

    def has(self, func_name: str) -> bool:
        if func_name in self._internal_convert_map:
            return True
        if func_name in self._user_defined_convert_map:
            return True
        return False

    def __str__(self):
        return str(zip(self.edges, self.nodes))
