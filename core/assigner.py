from __future__ import annotations

from jsonpath_ng.ext import parse
from jsonpath_ng import DatumInContext

from jsonpath2path.common.constants import AssignType
from jsonpath2path.common.exceptions import *
from jsonpath2path.common.utils import add_virtual_root, get_real_data


class SlotAssigner:
    def __init__(self):
        # assign_type and jsonpath for slot matching.
        self._assign_type = None
        self._jsonpath = None
        self._parser = None

        # Nodes and edges to be assigned to slots.
        self._nodes = None
        self._edges = None
        # In Occupy mode, edges are supplied via jsonpath (replace original edges).
        self._new_edges = None

    def assign(self, jsonpath: str, assign_type: AssignType=AssignType.OCCUPY) -> SlotAssigner:
        self._jsonpath = jsonpath
        self._assign_type = assign_type
        self._build_parser()

        return self

    def source(self, edges: list[str|int], nodes: list[any]) -> SlotAssigner:
        # Check params.
        if nodes is None or len(nodes) == 0:
            raise InvalidNodesError("Nodes must not be empty.")
        if edges is None or len(edges) != len(nodes):
            raise NodeEdgeNotMatchedError("Edges and nodes must have same length.")

        self._nodes = nodes
        self._edges = edges

        return self

    def to(self, data: dict | list, jsonpath: str=None, assign_type=None) -> dict | list:
        if data is None:
            raise InvalidJsonDataError("Parameter `data` is required.")

        # Priority: args > assign()
        if jsonpath is not None:
            self._jsonpath = jsonpath
            self._parser = None
        if assign_type is not None:
            self._assign_type = assign_type
            self._parser = None

        if self._parser is None:
            self._build_parser()

        self._to(data)
        return data

    def _to(self, data):
        # Add virtual root node to handles whole-JSON replacement.
        assign_data = add_virtual_root(data=data)

        # JsonPath match.
        matches = self._parser.find(assign_data)
        if matches is None or len(matches) == 0:
            raise InvalidJsonPathError(f"No matches found for {self._jsonpath}")

        # Assign nodes to slots with 1:1, n:1, 1:n and n:n auto-mapping.
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

        # Update to target data.
        assign_data = get_real_data(assign_data)
        data.update(assign_data)

    def _build_parser(self):
        if self._jsonpath is None:
            raise InvalidJsonPathError("Use `assign()` or `path` to set JSONPath first.")
        if self._assign_type is None:
            raise InvalidAssignTypeError("Use `assign()` or `assign_type` to set assign type first.")

        # Add virtual root node to handles whole-JSON replacement.
        virtual_path = add_virtual_root(jsonpath=self._jsonpath)

        if self._assign_type == AssignType.OCCUPY:
            # Replace occupy mode to mount mode with specified edge name.
            virtual_path, edge = virtual_path.rsplit('.', 1)
            self._new_edges = [edge for _ in range(len(self._edges))]
        elif self._assign_type == AssignType.MOUNT:
            self._new_edges = self._edges
        else:
            raise InvalidAssignTypeError(f"Unknown assign type {self._assign_type}")

        # Create JSONPath parser
        try:
            self._parser = parse(virtual_path)
        except:
            raise InvalidJsonPathError(f"Invalid jsonpath: {self._jsonpath}")

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

    def __str__(self):
        return f"SlotAssigner(jsonpath={self._jsonpath}, assign_type={self._assign_type}, nodes={self._nodes}, edges={self._new_edges})"
