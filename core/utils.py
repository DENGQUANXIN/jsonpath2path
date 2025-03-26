import copy
from copy import deepcopy

from jsonpath_ng import parse, DatumInContext

from .constant import VIRTUAL_ROOT_EDGE
from .exceptions import *


def new_match(edge, node):
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

def add_virtual_root(data: dict | list, path: str) -> (dict | list, str):
    path = f"{path[0]}.{VIRTUAL_ROOT_EDGE}{path[1:]}"
    return {VIRTUAL_ROOT_EDGE: data}, path

def get_real_data(data: dict | list) -> dict | list | None:
    if VIRTUAL_ROOT_EDGE in data:
        return data[VIRTUAL_ROOT_EDGE]
    return None

def is_root(match: DatumInContext) -> bool:
    return match.context is None

def del_node(data: dict | list, match: DatumInContext) -> None:
    if is_root(match): # Root node can only be cleared.
        match.value = deepcopy(match.value)
        data.clear()
    else:
        edge = get_edge(match)
        match.context.value.pop(edge)
