import re
from typing import List

from jsonpath2path.common.entities import ConverterData
from .register import register_internal_convert


@register_internal_convert
def k_rename(data: ConverterData, *args, **kwargs):
    """
    Convert edge names between different naming conventions.

    Args:
        data: ConverterData object to modify
        args[0]: Target naming convention (required):
            - 'camel': camelCase
            - 'pascal': PascalCase
            - 'snake': snake_case
            - 'kebab': kebab-case
            - 'upper': UPPER_CASE
            - 'lower': lower_case
            - 'title': Title Case
        args[1]: Source naming convention (optional):
            - If not provided, will auto-detect
            - Same options as target convention
    """
    if len(args) < 1:
        raise ValueError("Target naming convention argument required")

    # Supported conventions mapping
    CONVENTIONS = {
        'camel': 'camelCase',
        'pascal': 'PascalCase',
        'snake': 'snake_case',
        'kebab': 'kebab-case',
        'upper': 'UPPER_CASE',
        'lower': 'lower_case',
        'title': 'Title Case'
    }

    target_conv = args[0].lower()
    if target_conv not in CONVENTIONS:
        raise ValueError(f"Invalid target convention. Choose from: {list(CONVENTIONS.keys())}")

    source_conv = args[1].lower() if len(args) > 1 else None

    def detect_convention(name: str) -> str:
        """Auto-detect the naming convention of a string."""
        if '_' in name:
            return 'snake'
        elif '-' in name:
            return 'kebab'
        elif name.isupper():
            return 'upper'
        elif name.istitle():
            return 'title'
        elif name.islower():
            if any(c.isupper() for c in name):
                return 'camel' if name[0].islower() else 'pascal'
            return 'lower'
        return 'unknown'

    def split_words(name: str, convention: str) -> List[str]:
        """Split a name into words based on its convention."""
        if convention == 'snake':
            return [w for w in name.split('_') if w]
        elif convention == 'kebab':
            return [w for w in name.split('-') if w]
        elif convention == 'camel':
            return re.findall('[a-z]+|[A-Z][a-z]*', name)
        elif convention == 'pascal':
            words = re.findall('[A-Z][a-z]*', name)
            return [w.lower() for w in words]
        elif convention == 'upper':
            return [w.lower() for w in name.split('_') if w]
        elif convention == 'title':
            return [w.lower() for w in name.split() if w]
        else:  # lower or unknown
            return [name]

    def convert_name(name: str) -> str:
        """Convert a single name to target convention."""
        if not name:
            return name

        src_conv = source_conv or detect_convention(name)
        words = split_words(name, src_conv)

        if not words:
            return name

        if target_conv == 'camel':
            return words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        elif target_conv == 'pascal':
            return ''.join(w.capitalize() for w in words)
        elif target_conv == 'snake':
            return '_'.join(w.lower() for w in words)
        elif target_conv == 'kebab':
            return '-'.join(w.lower() for w in words)
        elif target_conv == 'upper':
            return '_'.join(w.upper() for w in words)
        elif target_conv == 'lower':
            return '_'.join(w.lower() for w in words)
        elif target_conv == 'title':
            return ' '.join(w.capitalize() for w in words)
        return name

    if data.edges:
        data.edges = [convert_name(edge) for edge in data.edges]


@register_internal_convert
def k_reformat(data: ConverterData, *args, **kwargs):
    """
    Rename edges in-place.

    Args:
        data: ConverterData to modify
        args[0]: pattern string
        args[1]: Dict {old:new} (optional)
    """
    if len(args) < 1:
        raise ValueError("Renaming pattern required")

    lookup = args[1] if len(args) > 1 else {}
    data.edges = [lookup.get(edge, args[0].format(key=edge)) for edge in data.edges]