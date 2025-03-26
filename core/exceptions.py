class InvalidDataError(ValueError):
    """Invalid data exception."""
    pass

class InvalidJsonDataError(InvalidDataError):
    """JSON data exception."""
    pass

class InvalidMatchError(InvalidDataError):
    """Match exception."""
    pass

class InvalidEdgeError(InvalidDataError):
    """Edge exception."""
    pass

class InvalidNodeError(InvalidDataError):
    """Invalid node data exception."""
    pass

class InvalidJsonPathError(ValueError):
    """Invalid JSON path exception."""
    pass

class InvalidAssignTypeError(ValueError):
    """Invalid assignment type exception."""
    pass

class NodeToSlotError(ValueError):
    """Node to slot match exception."""
    pass

class ConvertFuncNotFoundError(NotImplementedError):
    """Convert function not found exception."""
    pass

class ConvertFuncExistedError(ValueError):
    """Convert function existed exception."""
    pass