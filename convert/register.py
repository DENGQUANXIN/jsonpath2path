from typing import Callable

INTERNAL_CONVERT_MAP = {}
USER_DEFINED_CONVERT_MAP = {}


def register_internal_convert(func: Callable) -> Callable:
    name = func.__name__
    INTERNAL_CONVERT_MAP[name] = func
    return func


def register_user_defined_convert(name: str = None) -> Callable:
    """Annotations for user defined conversion methods."""

    def decorator(func: Callable) -> Callable:
        nonlocal name
        if name is None:
            name = func.__name__
        USER_DEFINED_CONVERT_MAP[name] = func
        return func

    return decorator


def get_convert_func(name: str) -> Callable:
    return USER_DEFINED_CONVERT_MAP.get(name, INTERNAL_CONVERT_MAP.get(name))
