from enum import Enum

class PickType(Enum):
    PLUCK = 1
    COPY = 2
    CREATE = 3

class AssignType(Enum):
    OCCUPY = 1
    MOUNT = 2

VIRTUAL_ROOT_EDGE = "__DATA__"

ROOT_JSON_PATH = "$"