# jsonpath2path - JSON Data Transformation Tool

## Overview

jsonpath2path is a powerful JSON data transformation tool that allows you to manipulate JSON structures using a simple yet expressive syntax. Inspired by JSONPath expressions, this tool provides advanced capabilities for modifying JSON data through path-based operations.

Refer to the document for the principle: [JSON Path to Path](./docs/JSON%20Path%20to%20Path.pdf)

## Key Features

- Intuitive path-based syntax for JSON manipulation
- Support for both value replacement and structural mounting
- Built-in conversion functions for common transformations
- Flexible source-target mapping (`1:1`, `N:N`, `1:N`, `N:1`)
- List operations with automatic appending for out-of-bound indices

## Core Concepts

### JSON as a Tree Structure

JSON data is treated as a tree where:
- Nodes represent values (dict, list, str, number, bool, or null)
- Edges represent dictionary keys or list indices
- "Slots" are positions in the tree that can hold either edges or nodes

### Operation Types

1. **Occupy (`->`)**: Replace the value at the target path
2. **Mount (`=>`)**: Attach edges and nodes to the target path

### Mapping Relationships

1. `1:1`: Direct mapping without transformation
2. `N:N`: Index-to-index mapping between source and target lists
3. `1:N`: Source node is duplicated to match multiple targets
4. `N:1`: Multiple sources are appended/mounted to a single target

## Command Syntax

```
( @jsonpath / jsonpath / `list` ) [ | convert_func [ param ]... ]... ( -> / => ) jsonpath
```

### Components:

1. **Source Specification** (choose one):
   - `@jsonpath`: JSONPath with node values
   - `jsonpath`: Regular JSONPath
   - `` `list` ``: Backtick-wrapped 2D list in format `[[k1,v1],[k2,v2],...]`

2. **Conversion Pipeline** (optional, repeatable):
   - `| convert_func [param]...`: Apply conversion functions with parameters

3. **Operation Specification** (choose one):
   - `->`: Occupy (replace value)
   - `=>`: Mount (attach structure)

4. **Target JSONPath**: Destination path for the operation

## Built-in Converters

See the document: [JSON Converter Functions Documentation](./docs/converter.md)

### Usage Notes:
1. All converters operate on the current node set
2. Parameters can be:
   - Literal values (numbers, strings, booleans)
   - JSONPath expressions (for targeting sub-nodes)
3. Multiple converters can be chained with `|`
Here's the updated Examples section that includes both the command syntax and functional API examples:

## Examples

### Example Data
```json
{
  "character": {
    "name": "WarriorX",
    "race": "Human",
    "class": "Warrior",
    "level": 25,
    "skills": [
      {
        "name": "Sword Slash",
        "damage": 50,
        "cooldown": 3
      },
      {
        "name": "Shield Bash",
        "damage": 30,
        "cooldown": 5
      }
    ],
    "equipment": {
      "weapon": "Great Sword",
      "armor": "Heavy Plate Armor"
    },
    "attributes": {
      "health": 500,
      "mana": 100,
      "strength": 80,
      "defense": 70
    }
  }
}
```

### Addition Operations

1. **Add new attributes**
   - Command syntax:
     ```python
     `[["agility", 50], ["lucky", 20]]` => $.character.attributes
     ```
   - Functional API:
     ```python
     (transformer.source([["agility", 50], ["lucky", 20]])
                  .pick(pick_type=PickType.CREATE)
                  .assign("$.character.attributes", AssignType.MOUNT)
                  .to(data))
     ```

### Deletion Operations

2. **Remove skills with long cooldowns**
   - Command syntax:
     ```python
     $.character.skills[?(@.cooldown > 4)] ->
     ```
   - Functional API:
     ```python
     (transformer.source(data)
                  .pick("$.character.skills[?(@.cooldown > 4)]", PickType.PLUCK))
     ```

3. **Clear equipment**
   - Command syntax:
     ```python
     $.character.equipment.* ->
     ```
   - Functional API:
     ```python
     (transformer.source(data)
                  .pick("$.character.equipment.*", PickType.PLUCK))
     ```

### Modification Operations

4. **Adjust skill cooldowns**
   - Command syntax:
     ```python
     $.character.skills[*].cooldown | v_map "lambda v: v+5" => $.character.skills[*]
     ```
   - Functional API:
     ```python
     (transformer.source(data)
                  .pick("$.character.skills[*].cooldown", PickType.PLUCK)
                  .v_map(lambda v: v+5)
                  .assign("$.character.skills[*]", AssignType.MOUNT)
                  .to(data))
     ```

5. **Change character properties**
   - Command syntax:
     ```python
     `[["race", "Elf"]]` -> $.character.race
     `[["strength", 70], ["mana", 200]]` => $.character.attributes
     ```
   - Functional API:
     ```python
     (transformer.source([["race", "Elf"]])
                  .pick(pick_type=PickType.CREATE)
                  .assign("$.character.race", AssignType.OCCUPY)
                  .to(data))
     (transformer.source([["strength", 70], ["mana", 200]])
                  .pick(pick_type=PickType.CREATE)
                  .assign("$.character.attributes", AssignType.MOUNT)
                  .to(data))
     ```

### Data Movement Operations

6. **Move skills to new document**
   - Command syntax:
     ```python
     $.character.skills => $
     ```
   - Functional API:
     ```python
     (transformer.source(data)
                  .pick("$.character.skills", PickType.PLUCK)
                  .assign("$", AssignType.MOUNT)
                  .to(to_data))
     ```

7. **Copy attributes to new document**
   - Command syntax:
     ```python
     @$.character.attributes => $
     ```
   - Functional API:
     ```python
     (transformer.source(data)
                  .pick("$.character.attributes", PickType.COPY)
                  .assign("$", AssignType.MOUNT)
                  .to(to_data))
     ```

### Key Features Demonstrated:
- Both **command syntax** and **functional API** styles
- **Mounting** (`=>`/`AssignType.MOUNT`) vs **Occupying** (`->`/`AssignType.OCCUPY`) operations
- Different **pick types** (`PLUCK`, `COPY`, `CREATE`)
- **Value modification** using converters (`v_add`, `v_set`)
- **Data movement** between documents

The functional API provides more explicit control over each step of the transformation process, while the command syntax offers a more concise way to express common operations. Both styles can be used interchangeably depending on your preference and use case requirements.
## Getting Started

1. Install the package (installation method TBD)
2. Import the module in your code
3. Use the `transform_json` function with your JSON data and transformation commands

## Contribution

Contributions are welcome! Please submit issues or pull requests through GitHub.

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

