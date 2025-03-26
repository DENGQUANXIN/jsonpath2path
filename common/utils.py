from __future__ import annotations

import copy

from jsonpath_ng import parse, DatumInContext

from jsonpath2path.common.constants import VIRTUAL_ROOT_EDGE
from jsonpath2path.common.exceptions import *


def new_match(edge: int|str, node: any) -> DatumInContext:
    if isinstance(edge, str):
        return parse(f"$.{edge}").find({edge: node})[0]
    tmp_list = [None for _ in range(edge)] + [node]
    return parse(f"$[{edge}]").find(tmp_list)[0]


def get_edge(match: DatumInContext) -> str | int | None:
    if match.context is None:
        return None

    if isinstance(match.context.value, dict):
        return match.path.fields[0]

    if isinstance(match.context.value, list):
        return match.path.index

    raise InvalidMatchError(f"Unexpected match type: {match.context.type}")


def get_node(match: DatumInContext) -> dict | list | None:
    if match is not None:
        return copy.deepcopy(match.value)

def get_path(match: DatumInContext) -> str:
    return match.full_path

def add_virtual_root(data: dict | list=None, jsonpath: str | None=None):
    if data is not None and jsonpath is not None:
        return {VIRTUAL_ROOT_EDGE: data}, f"{jsonpath[0]}.{VIRTUAL_ROOT_EDGE}{jsonpath[1:]}"
    if data is not None:
        return {VIRTUAL_ROOT_EDGE: data}
    if jsonpath is not None:
        return f"{jsonpath[0]}.{VIRTUAL_ROOT_EDGE}{jsonpath[1:]}"

def get_real_data(data: dict | list) -> dict | list | None:
    if VIRTUAL_ROOT_EDGE in data:
        return data[VIRTUAL_ROOT_EDGE]
    return None

def is_root(match: DatumInContext) -> bool:
    return match.context is None

def unlink(match: DatumInContext) -> None:
    edge = get_edge(match)
    match.context.value.pop(edge)
