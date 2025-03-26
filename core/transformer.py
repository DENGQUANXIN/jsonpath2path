from __future__ import annotations

import json
from typing import Callable

from lark import Lark, Transformer as LarkTransformer

from .assigner import SlotAssigner
from jsonpath2path.common.constants import AssignType, PickType
from .converter import NodeConverter, ConverterData
from jsonpath2path.common.exceptions import InvalidJsonDataError
from .picker import NodePicker

bnf = r"""
    start: command
    
    command: t_picker t_converter t_assigner
    
    t_picker: (PICKER_PLUCK | PICKER_COPY | PICKER_CREATE)
    t_converter: ("|" t_convert_cmd)*
    t_assigner: (ASSIGN_OCCUPY | ASSIGN_MOUNT) (JSONPATH)?
    
    PICKER_COPY: "@" JSONPATH
    PICKER_PLUCK: JSONPATH
    PICKER_CREATE: "`" JSON "`"
    
    t_convert_cmd: CONVERT_FUNC (t_param)*
    CONVERT_FUNC: CNAME
    t_param: JSONPATH | STRING | NUMBER | "`" JSON "`" | BOOL
    
    ASSIGN_OCCUPY: /->/
    ASSIGN_MOUNT: /=>/
    
    JSON: /[^`]+/
    JSONPATH: "$" (("." CNAME) | (".*") | ("[" JSONPATH_FILTER "]"))*
    JSONPATH_FILTER: (NUMBER | "*" | "?(" /[^)]+/ ")")
    BOOL: "true" | "false"
    
    %import common.ESCAPED_STRING -> STRING
    %import common.CNAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""


class JsonTransformer:
    """
    A pipeline integrating picker, converter, and assigner, using chaining calls to implement JSON transformation.
    """
    _data: dict | list = None
    _to_data: dict | list = None

    _picker: NodePicker = NodePicker()
    _converter: NodeConverter = NodeConverter()
    _assigner: SlotAssigner = SlotAssigner()

    def register(self, func_name: str, convert_func: Callable[[ConverterData, any], None]) -> None:
        """
        Register user-defined convert function.
        :param func_name: function name.
        :param convert_func: A function with three parameters: edges, nodes, and params; modify edges and nodes in place.
        """
        self._converter.register(func_name, convert_func)

    def source(self, data: dict | list = None) -> JsonTransformer:
        """
        Set source JSON data.
        :param data: JSON structure, as the source data for transformation.
        :return: JsonTransformer for chaining calls.
        """
        if data is None:
            raise InvalidJsonDataError("Source JSON data cannot be None")
        self._data = data
        return self

    def pick(self, jsonpath: str = None, pick_type: PickType = PickType.COPY) -> JsonTransformer:
        """
        Pick nodes from source JSON data.
        :param jsonpath: JSONPath for locating nodes to pick.
        :param pick_type: `copy` | `pluck` | `create` from source JSON data.
        :return: JsonTransformer for chaining calls.
        """
        if self._data is None:
            raise InvalidJsonDataError("Use `source()` to set the source JSON data first.")
        if pick_type == PickType.PLUCK:
            self._picker.pluck(self._data, jsonpath)
        elif pick_type == PickType.COPY:
            self._picker.copy(self._data, jsonpath)
        elif pick_type == PickType.CREATE:
            edges, nodes = [], []
            for [edge, node] in self._data:
                edges.append(edge)
                nodes.append(node)
            self._picker.create(edges, nodes)
        self._picker_to_converter()

        return self

    def convert(self, convert_func: str, *args) -> JsonTransformer:
        """
        Convert picked nodes using given function.
        :param convert_func: function name.
        :param args: function parameters.
        :return: JsonTransformer for chaining calls.
        """
        self._converter.convert(convert_func, *args)
        return self

    def assign(self, jsonpath: str, assign_type: AssignType = AssignType.OCCUPY) -> JsonTransformer:
        """
        Pass data to the assigner and set the assign mode.
        :param jsonpath: JSONPath for locating slots to be assigned.
        :param assign_type: `occupy` | `mount` to slots.
        """
        self._converter_to_assigner()
        self._assigner.assign(jsonpath, assign_type)
        return self

    def to(self, to_data: str | dict | list) -> dict | list:
        """
        Assign nodes to slots defined by the JSONPath in the target JSON data.
        :param to_data: JSON structure, as the target data for transformation.
        :return: JsonTransformer for chaining calls.
        """
        if isinstance(to_data, str):
            self._to_data = json.loads(to_data)
        else:
            self._to_data = to_data
        return self._assigner.to(self._to_data)

    def _picker_to_converter(self):
        self._picker.to(self._converter)

    def _converter_to_assigner(self):
        self._converter.to(self._assigner)

    def __getattr__(self, item):
        # Call all `convert_func` using convert.
        if self._converter.has(item):
            def wrapper(*args, **kwargs):
                self._converter.convert(item, *args, **kwargs)
                return self
            return wrapper
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")


class CommandTransformer(JsonTransformer, LarkTransformer):
    """
    Parse command and execute JSON transformation.
    """

    def __init__(self):
        super().__init__()
        self._parser = Lark(bnf, parser="lalr")

    def by(self, command: str):
        """
        Transform the nodes from the source JSON to the target JSON by the given command.

        :param command: JSONPathToPath command.
        """
        tree = self._parser.parse(command)
        self.transform(tree)
        return self

    def t_picker(self, items):
        picker = items[0].type
        jsonpath = None
        if picker == "PICKER_CREATE":
            data = json.loads(str(items[0]).strip('`'))
            self.source(data)
            pick_type = PickType.CREATE
        elif picker == "PICKER_PLUCK":
            jsonpath = items[0]
            pick_type = PickType.PLUCK
        elif picker == "PICKER_COPY":
            jsonpath = items[0].strip('@')
            pick_type = PickType.COPY
        else:
            raise ValueError("Unknown picker type")
        self.pick(jsonpath, pick_type)

    def t_assigner(self, items):
        if len(items) != 2:
            return
        if items[0].type == "ASSIGN_MOUNT":
            assign_type = AssignType.MOUNT
        elif items[0].type == "ASSIGN_OCCUPY":
            assign_type = AssignType.OCCUPY
        else:
            raise ValueError("Unknown assign type")
        self.assign(items[1].value, assign_type)

    def t_convert_cmd(self, items):
        self.convert(items[0], *items[1:])

    @staticmethod
    def t_param(items):
        item_type = items[0].type
        if item_type == 'JSONPATH':
            return str(items[0])
        if item_type == 'NUMBER':
            return json.loads(items[0])
        if item_type == 'JSON':
            return json.loads(items[0])
        if item_type == 'STRING':
            return str(items[0]).strip('"')
        if item_type == 'BOOL':
            return items[0] == 'true'
        return items[0].value

    def __getattr__(self, item):
        return JsonTransformer.__getattr__(self, item)


if __name__ == '__main__':
    json_data = {
        "store": {
            "book": [
                {"title": "abc", "price": 111},
                {"title": "cba", "price": 222}
            ],
            "bicycle": {
                "color": "blue",
                "price": 333
            }
        }
    }

    transformer = JsonTransformer().source(json_data).pick('$', PickType.PLUCK)
    print(json_data)
    transformer.v_sort().assign('$', AssignType.OCCUPY).to(json_data)
    print(json_data)

    # 为每本书增加作者信息，默认为Anonymous
    cmd = '`[["author", "Anonymous"]]` => $.store.book[*]'
    print(cmd)
    CommandTransformer().by(cmd).to(json_data)
    print(json_data)

    # 为书增加作者信息为"标题_author"
    cmd = '@$.store.book[*].title | v_add "_author" -> $.store.book[*].author'
    print(cmd)
    CommandTransformer().source(json_data).by(cmd).to(json_data)
    print(json_data)

    # 移除第二本书
    cmd = '$.store.book[1]->'
    print(cmd)
    CommandTransformer().source(json_data).by(cmd)
    print(json_data)

    # 移除价格大于20的书
    cmd = '$.store.book[?(@.price>20)]->'
    print(cmd)
    CommandTransformer().source(json_data).by(cmd)
    print(json_data)

    # 新增两本书
    cmd = '`[[3,{"title":"efg","price":333}], [4,{"title":"efg","price":444}]]` => $.store.book'
    print(cmd)
    CommandTransformer().source(json_data).by(cmd).to(json_data)
    print(json_data)

    # 将每本书的价格增加5
    cmd = '$.store.book[*].price | v_add 5 -> $.store.book[*].price'
    print(cmd)
    CommandTransformer().source(json_data).by(cmd).to(json_data)
    print(json_data)

    # 将书按照价格的倒序排列
    cmd = '@$.store.book[*] | v_sort true $.price => $.store.book'
    print(cmd)
    CommandTransformer().source(json_data).by(cmd).to(json_data)
    print(json_data)

    # 将自行车修改为列表
    cmd = '$.store.bicycle | v_wrap_in_list -> $.store.bicycle'
    print(cmd)
    CommandTransformer().source(json_data).by(cmd).to(json_data)
    print(json_data)

    # 将自行车设置为与商店平级
    cmd = '$.store.bicycle => $'
    print(cmd)
    CommandTransformer().source(json_data).by(cmd).to(json_data)
    print(json_data)

    # 去掉商店层级
    cmd = '$.store.* => $'
    print(cmd)
    CommandTransformer().source(json_data).by(cmd).to(json_data)
    print(json_data)
    cmd = '$.store ->'
    print(cmd)
    CommandTransformer().source(json_data).by(cmd)
    print(json_data)
