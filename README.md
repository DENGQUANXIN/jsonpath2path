# jsonpath2path - JSON Data Transformation Tool

## Overview

jsonpath2path is a powerful JSON data transformation tool that allows you to manipulate JSON structures using a simple yet expressive syntax. Inspired by JSONPath expressions, this tool provides advanced capabilities for modifying JSON data through path-based operations.

## Key Features

- Intuitive path-based syntax for JSON manipulation
- Support for both value replacement and structural mounting
- Built-in conversion functions for common transformations
- Flexible source-target mapping (1:1, N:N, 1:N, N:1)
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

1. **1:1**: Direct mapping without transformation
2. **N:N**: Index-to-index mapping between source and target lists
3. **1:N**: Source node is duplicated to match multiple targets
4. **N:1**: Multiple sources are appended/mounted to a single target

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

- `v_add`: Add operation
  - `param1`: Value to add (required)
  - `param2`: JSONPath for sub-node to add to (optional)

- `sort`: Sorting
  - `param1`: Boolean for reverse sort
  - `param2`: JSONPath for sort key sub-node

- `reverse`: Reverse order of elements

## Examples

### Example Data
```json
{
  "store": {
    "book": [
      {"title": "Book1", "price": 10},
      {"title": "Book2", "price": 20}
    ],
    "bicycle": {
      "color": "red",
      "price": 100
    }
  }
}
```

### Example 1: Add author information
**Requirement**: Add "Anonymous" as author to all books

**Command**:
`` `[["author", "Anonymous"]]` => $.store.book[*] ``

### Example 2: Create author names from titles
**Requirement**: Set author as "title_author" for each book

**Command**:
`@$.store.book[*].title | v_add "_author" -> $.store.book[*].author`

### Example 3: Remove the second book
**Command**:
`$.store.book[1]->`

### Example 4: Remove expensive books
**Command**:
`$.store.book[?(@.price>20)]->`

### Example 5: Sort books by price (descending)
**Command**:
`@$.store.book[*] | sort true $.price => $.store.book`

### Example 6: Flatten the store structure
**Commands**:
1. `$.store.* => $`
2. `$.store ->`

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

