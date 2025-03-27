from __future__ import annotations

import re

from jsonpath_ng.ext import parse

from jsonpath2path.common.entities import ConverterData
from .register import register_internal_convert


# ========== Common value convert ==========
@register_internal_convert
def v_filter(data: ConverterData, *args, **kwargs):
    """
    Filter nodes based on a condition using only args.

    Args:
        data: ConverterData with edges and nodes
        args[0]: JSONPath for filtering
        args[1]: Value to compare (optional)
        args[2]: Operator as string ('==', '>', etc., default '==')
        args[3]: Keep if missing (bool, default False)
    """
    if len(args) < 1:
        raise ValueError("JSONPath argument required")

    jsonpath = args[0]
    compare_value = args[1] if len(args) > 1 else None
    operator = args[2] if len(args) > 2 else '=='
    keep_if_missing = args[3] if len(args) > 3 else False

    parser = parse(jsonpath)
    new_edges, new_nodes = [], []

    for edge, node in zip(data.edges, data.nodes):
        matches = parser.find(node)

        if not matches:
            if keep_if_missing:
                new_nodes.append(node)
                new_edges.append(edge)
            continue

        match_value = matches[0].value

        if compare_value is None:
            condition_met = True
        else:
            ops = {
                '==': lambda a, b: a == b,
                '!=': lambda a, b: a != b,
                '>': lambda a, b: a > b,
                '<': lambda a, b: a < b,
                '>=': lambda a, b: a >= b,
                '<=': lambda a, b: a <= b,
                'in': lambda a, b: a in b,
                'contains': lambda a, b: b in a
            }
            condition_met = ops.get(operator, ops['=='])(match_value, compare_value)

        if condition_met:
            new_nodes.append(node)
            new_edges.append(edge)

    data.nodes = new_nodes
    data.edges = new_edges


@register_internal_convert
def v_map(data: ConverterData, *args):
    """
    Transform node values using only args.

    Args:
        data: ConverterData with edges and nodes
        args[1]: JSONPath or lambda function (string)
    """
    if len(args) < 1:
        raise ValueError("Mapping argument required")

    try:
        if callable(args[0]):
            map_func = args[0]
        elif str.startswith(args[0], 'lambda'):
            map_func = eval(args[0])
        else:
            parser = parse(args[0])
            map_func = lambda node: parser.find(node)[0].value if parser.find(node) else None
    except:
        raise ValueError("Mapping argument must be a JSONPath or lambda function string.")

    data.nodes = [map_func(node) for node in data.nodes]


@register_internal_convert
def v_sort(data: ConverterData, *args, **kwargs):
    """
        Sort all nodes using only args.

        Args:
            data: ConverterData with edges and nodes
            args[0]: Reverse (bool, default False)
            args[1]: JSONPath or lambda function string
        """
    reverse = args[0] if len(args) > 0 else False
    key_func = lambda node: node
    if len(args) > 1:
        if str.startswith(args[1], 'lambda'):
            key_func = eval(args[1])
        else:
            parser = parse(args[1])
            key_func = lambda node: parser.find(node)[0].value

    data.nodes.sort(key=key_func, reverse=reverse)


# ========== String value convert ==========
@register_internal_convert
def v_string_trim(data: ConverterData, *args, **kwargs):
    """
    Trim whitespace from string values.
    Usage: v_string_trim(data, jsonpath)
    """
    try:
        if len(args) == 0:
            data.nodes = [node.strip() for node in data.nodes]
        else:
            parser = parse(args[0])
            for node in data.nodes:
                for match in parser.find(node):
                    match.context.value[match.path.fields[-1]] = match.value.strip()
    except:
        raise ValueError("Trimmed whitespace from string values!")


@register_internal_convert
def v_string_replace(data: ConverterData, *args, **kwargs):
    """
    Replace substring using regex.
    Usage: v_string_replace(data, jsonpath, pattern, replacement)
    """
    if len(args) < 3:
        raise ValueError("Requires jsonpath, pattern and replacement arguments")

    pattern, replacement = args[1], args[2]
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, str):
                match.context.value[match.path.fields[-1]] = re.sub(
                    pattern, replacement, match.value
                )


@register_internal_convert
def v_string_truncate(data: ConverterData, *args, **kwargs):
    """
    Truncate string to specified length.
    Usage: v_string_truncate(data, jsonpath, max_length)
    """
    if len(args) < 2:
        raise ValueError("Requires jsonpath and max_length arguments")

    max_len = int(args[1])
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, str) and len(match.value) > max_len:
                match.context.value[match.path.fields[-1]] = match.value[:max_len]


# ========== Number value convert ==========
@register_internal_convert
def v_number_round(data: ConverterData, *args, **kwargs):
    """
    Round numeric values.
    Usage: v_number_round(data, jsonpath, decimals=0)
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    decimals = int(args[1]) if len(args) > 1 else 0
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, (int, float)):
                match.context.value[match.path.fields[-1]] = round(match.value, decimals)


@register_internal_convert
def v_number_convert_units(data: ConverterData, *args, **kwargs):
    """
    Convert units using linear transformation (x * factor + offset).
    Usage: v_number_convert_units(data, jsonpath, factor, offset=0)
    """
    if len(args) < 2:
        raise ValueError("Requires jsonpath and factor arguments")

    factor = float(args[1])
    offset = float(args[2]) if len(args) > 2 else 0.0
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, (int, float)):
                match.context.value[match.path.fields[-1]] = match.value * factor + offset


# ========== Null value convert ==========
@register_internal_convert
def v_null_to_default(data: ConverterData, *args, **kwargs):
    """
    Replace null values with default value.
    Usage: v_null_to_default(data, jsonpath, default_value)
    """
    if len(args) < 2:
        raise ValueError("Requires jsonpath and default_value arguments")

    default_value = args[1]
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if match.value is None:
                match.context.value[match.path.fields[-1]] = default_value


@register_internal_convert
def v_null_drop(data: ConverterData, *args, **kwargs):
    """
    Remove fields with null values.
    Usage: v_null_drop(data, jsonpath)
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if match.value is None:
                match.context.value.pop(match.path.fields[-1], None)


# ========== List value convert ==========
@register_internal_convert
def v_list_unique(data: ConverterData, *args, **kwargs):
    """
    Remove duplicate values from list.
    Usage: v_list_unique(data, jsonpath)
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    parser = parse(args[0])
    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, list):
                match.context.value[match.path.fields[-1]] = list(set(match.value))


@register_internal_convert
def v_list_sort(data: ConverterData, *args, **kwargs):
    """
    Sort list elements.
    Usage: v_list_sort(data, jsonpath, reverse=False, key=None)
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    reverse = args[1] if len(args) > 1 else False
    key = args[2] if len(args) > 2 else None
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, list):
                match.context.value[match.path.fields[-1]] = sorted(
                    match.value,
                    key=key,
                    reverse=reverse
                )


@register_internal_convert
def v_list_filter(data: ConverterData, *args, **kwargs):
    """
    Filter list elements by condition.
    Usage: v_list_filter(data, jsonpath, condition_func)
    """
    if len(args) < 2:
        raise ValueError("Requires jsonpath and condition_func arguments")

    parser = parse(args[0])
    condition = args[1]  # Can be function or lambda

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, list):
                match.context.value[match.path.fields[-1]] = [
                    x for x in match.value if condition(x)
                ]
