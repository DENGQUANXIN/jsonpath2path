from jsonpath_ng.ext import parse
from jsonpath_ng import DatumInContext

from .constant import AssignType
from .exceptions import *
from .utils import add_virtual_root, get_real_data


class SlotAssigner:
    def __init__(self):
        self._assign_type = None
        self._jsonpath = None

        self._nodes = None
        self._edges = None
        self._new_edges = None

    def assign(self, jsonpath: str, assign_type: AssignType=AssignType.OCCUPY):
        self._jsonpath = jsonpath
        self._assign_type = assign_type

    def source(self, edges: list[str|int], nodes: list[any]):
        if edges is None or nodes is None or len(edges) != len(nodes):
            raise InvalidNodeError("Edges and nodes must have same length")
        if len(nodes) == 0:
            raise InvalidNodeError("Nodes must not be empty")
        self._nodes = nodes
        self._edges = edges
        return self

    def to(self, data: dict | list, path: str=None, assign_type=None) -> any:
        if data is None:
            raise InvalidJsonDataError("Parameter `data` is required.")
        if path is None and self._jsonpath is None:
            raise InvalidJsonPathError("Use `set_pattern()` or `path` to set JSONPath.")
        if assign_type is None and self._assign_type is None:
            raise InvalidAssignTypeError("Use `set_pattern()` or `assign_type` to set assign type.")

        path = self._jsonpath if path is None else path
        assign_type = self._assign_type if assign_type is None else assign_type

        assign_data, path = add_virtual_root(data, path)

        if assign_type == AssignType.OCCUPY:
            # Replace occupy mode to mount mode with specified edge name.
            path, edge = path.rsplit('.', 1)
            self._new_edges = [edge for _ in range(len(self._edges))]
        elif assign_type == AssignType.MOUNT:
            self._new_edges = self._edges
        else:
            raise InvalidAssignTypeError(f"Unknown assign type {assign_type}")

        matches = parse(path).find(assign_data)
        if matches is None or len(matches) == 0:
            raise InvalidJsonPathError(f"No match found for {path}")

        if len(self._nodes) == 1 and len(matches) == 1:
            self._one_to_one(matches[0])
        elif len(self._nodes) > 1 and len(matches) == 1:
            self._n_to_one(matches[0])
        elif len(self._nodes) == 1 and len(matches) > 1:
            self._one_to_n(matches)
        elif len(self._nodes) == len(matches):
            self._n_to_n(matches)
        else:
            raise NodeToSlotError(f"Invalid number of nodes({len(self._nodes)}) or slots({len(matches)})")

        data.update(get_real_data(assign_data))

    @staticmethod
    def _node_to_slot(edge: list[str|int], node: any, slot: DatumInContext):
        if slot is None:
            raise NodeToSlotError(f"Parameter `slot` is required.")
        if isinstance(slot.value, list):
            if not isinstance(edge, int):
                raise NodeToSlotError(f"Parameter `edge` must be of type `int` for list slot")
            if 0 <= edge < len(slot.value):
                slot.value[edge] = node
            else:
                # Append if index out of bounds.
                slot.value.append(node)
        elif isinstance(slot.value, dict):
            if not isinstance(edge, str):
                raise NodeToSlotError(f"Parameter `edge` must be of type `str` for dict slot")
            slot.value[edge] = node
        else:
            raise NodeToSlotError(f"Unexpected slot type {None if slot.value is None else slot.value.type}")

    def _one_to_one(self, slot: DatumInContext):
        edge, node = self._new_edges[0], self._nodes[0]
        self._node_to_slot(edge, node, slot)

    def _one_to_n(self, slots: list[DatumInContext]):
        edge, node = self._new_edges[0], self._nodes[0]
        for slot in slots:
            self._node_to_slot(edge, node, slot)

    def _n_to_one(self, slot: DatumInContext):
        for edge, node in zip(self._new_edges, self._nodes):
            self._node_to_slot(edge, node, slot)

    def _n_to_n(self, slots: list[DatumInContext]):
        for edge, node, slot in zip(self._new_edges, self._nodes, slots):
            self._node_to_slot(edge, node, slot)
