# ========== Data Error ==========
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

class InvalidNodesError(InvalidDataError):
    """Invalid node data exception."""
    pass

class NodeEdgeNotMatchedError(InvalidDataError):
    """Node and edge not matched exception."""
    pass


# ========== Parameter Error ==========
class InvalidParamError(ValueError):
    """Invalid parameter exception."""
    pass

class InvalidJsonPathError(InvalidParamError):
    """Invalid JSON path exception."""
    pass

class InvalidAssignTypeError(InvalidParamError):
    """Invalid assignment type exception."""
    pass


# ========== Execute Operator Error ==========
class OperatorError(RuntimeError):
    """Operator exception."""
    pass

class NodeToSlotError(OperatorError):
    """Node to slot match exception."""
    pass

class ConvertFuncNotFoundError(NotImplementedError):
    """Convert function not found exception."""
    pass

class ConvertFuncExistedError(OperatorError):
    """Convert function existed exception."""
    pass

class InvalidAssigner(RuntimeError):
    """Invalid assigner exception."""
    pass