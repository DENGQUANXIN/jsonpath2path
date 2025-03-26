import re
from datetime import datetime
from typing import Union

from jsonpath_ng.ext import parse

from .register import register_internal_convert
from jsonpath2path.common.entities import ConverterData


@register_internal_convert
def t_string_to_number(data: ConverterData, *args, **kwargs):
    """
    Convert string to number (int or float).
    Usage: t_string_to_number(data, jsonpath[, strict=True])
    - strict=True (default): raises ValueError if conversion fails
    - strict=False: leaves original value on failure
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    strict = args[1] if len(args) > 1 else True
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, str):
                try:
                    # Try int first, then float
                    num = int(match.value) if match.value.isdigit() else float(match.value)
                    match.context.value[match.path.fields[-1]] = num
                except ValueError:
                    if strict:
                        raise ValueError(f"Cannot convert '{match.value}' to number")


@register_internal_convert
def t_number_to_string(data: ConverterData, *args, **kwargs):
    """
    Convert number to string with optional formatting.
    Usage: t_number_to_string(data, jsonpath[, format_spec='g'])
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    format_spec = args[1] if len(args) > 1 else 'g'
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, (int, float)):
                match.context.value[match.path.fields[-1]] = format(match.value, format_spec)


@register_internal_convert
def t_number_to_bool(data: ConverterData, *args, **kwargs):
    """
    Convert number to boolean (0=False, non-zero=True).
    Usage: t_number_to_bool(data, jsonpath)
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, (int, float)):
                match.context.value[match.path.fields[-1]] = bool(match.value)


@register_internal_convert
def t_bool_to_number(data: ConverterData, *args, **kwargs):
    """
    Convert boolean to number (True=1, False=0).
    Usage: t_bool_to_number(data, jsonpath)
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, bool):
                match.context.value[match.path.fields[-1]] = int(match.value)


@register_internal_convert
def t_datetime_to_timestamp(data: ConverterData, *args, **kwargs):
    """
    Convert datetime string to timestamp.
    Usage: t_datetime_to_timestamp(data, jsonpath, format='%Y-%m-%d %H:%M:%S'[, timezone=None])
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    fmt = args[1] if len(args) > 1 else '%Y-%m-%d %H:%M:%S'
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, str):
                try:
                    dt = datetime.strptime(match.value, fmt)
                    if len(args) > 2:  # Handle timezone if provided
                        dt = dt.replace(tzinfo=args[2])
                    match.context.value[match.path.fields[-1]] = dt.timestamp()
                except ValueError as e:
                    if 'strict' not in kwargs or kwargs['strict']:
                        raise ValueError(f"Time format mismatch: {e}")


@register_internal_convert
def t_timestamp_to_datetime(data: ConverterData, *args, **kwargs):
    """
    Convert timestamp to datetime string.
    Usage: t_timestamp_to_datetime(data, jsonpath, format='%Y-%m-%d %H:%M:%S'[, timezone=None])
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    fmt = args[1] if len(args) > 1 else '%Y-%m-%d %H:%M:%S'
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, (int, float)):
                try:
                    dt = datetime.fromtimestamp(match.value)
                    if len(args) > 2:  # Handle timezone if provided
                        dt = dt.astimezone(args[2])
                    match.context.value[match.path.fields[-1]] = dt.strftime(fmt)
                except (ValueError, OSError) as e:
                    if 'strict' not in kwargs or kwargs['strict']:
                        raise ValueError(f"Invalid timestamp: {e}")


@register_internal_convert
def t_array_to_string(data: ConverterData, *args, **kwargs):
    """
    Convert array to string using join.
    Usage: t_array_to_string(data, jsonpath[, separator=', '[, filter_nulls=True]])
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    separator = args[1] if len(args) > 1 else ', '
    filter_nulls = args[2] if len(args) > 2 else True
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, list):
                items = [str(x) for x in match.value if not (filter_nulls and x is None)]
                match.context.value[match.path.fields[-1]] = separator.join(items)


@register_internal_convert
def t_string_to_array(data: ConverterData, *args, **kwargs):
    """
    Convert string to array using split.
    Usage: t_string_to_array(data, jsonpath[, separator=None[, strip_items=True]])
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    separator = args[1] if len(args) > 1 else None
    strip_items = args[2] if len(args) > 2 else True
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, str):
                items = match.value.split(separator) if separator else list(match.value)
                if strip_items:
                    items = [x.strip() for x in items]
                match.context.value[match.path.fields[-1]] = items


@register_internal_convert
def t_json_string_to_object(data: ConverterData, *args, **kwargs):
    """
    Convert JSON string to Python object.
    Usage: t_json_string_to_object(data, jsonpath[, strict=True])
    """
    import json
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    strict = args[1] if len(args) > 1 else True
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, str):
                try:
                    match.context.value[match.path.fields[-1]] = json.loads(match.value)
                except json.JSONDecodeError:
                    if strict:
                        raise ValueError("Invalid JSON string")


@register_internal_convert
def t_object_to_json_string(data: ConverterData, *args, **kwargs):
    """
    Convert Python object to JSON string.
    Usage: t_object_to_json_string(data, jsonpath[, indent=None])
    """
    import json
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    indent = args[1] if len(args) > 1 else None
    parser = parse(args[0])

    for node in data.nodes:
        for match in parser.find(node):
            try:
                match.context.value[match.path.fields[-1]] = json.dumps(
                    match.value,
                    indent=indent,
                    ensure_ascii=False
                )
            except TypeError:
                raise ValueError("Object not JSON serializable")


@register_internal_convert
def t_hex_to_rgb(data: ConverterData, *args, **kwargs):
    """
    Convert hex color string to RGB tuple.
    Usage: t_hex_to_rgb(data, jsonpath)
    """
    if len(args) < 1:
        raise ValueError("Requires jsonpath argument")

    parser = parse(args[0])
    hex_color_re = re.compile(r'^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')

    for node in data.nodes:
        for match in parser.find(node):
            if isinstance(match.value, str):
                hex_str = match.value.lstrip('#')
                if not hex_color_re.fullmatch(hex_str):
                    continue

                if len(hex_str) == 3:
                    hex_str = ''.join([c * 2 for c in hex_str])
                match.context.value[match.path.fields[-1]] = tuple(
                    int(hex_str[i:i + 2], 16) for i in (0, 2, 4)
                )