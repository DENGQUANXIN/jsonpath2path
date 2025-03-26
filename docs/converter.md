# JSON Converter Functions Documentation

## Key Converters (k_*)

### k_rename
**Description**: Convert edge names between different naming conventions  
**Python API**:  
```python
k_rename(data: ConverterData, target_conv: str, source_conv: str = None)
```
**Command Usage**:  
```
k_rename camel               # Auto-detect source, convert to camelCase
k_rename snake pascal        # Explicitly convert from PascalCase to snake_case
```

**Supported Conventions**:
- `camel`: camelCase
- `pascal`: PascalCase
- `snake`: snake_case
- `kebab`: kebab-case
- `upper`: UPPER_CASE
- `lower`: lower_case
- `title`: Title Case

### k_reformat
**Description**: Rename edges using pattern or mapping  
**Python API**:  
```python
k_reformat(data: ConverterData, pattern: str, mapping: dict = None)
```
**Command Usage**:  
```
k_reformat "prefix_{key}"
k_reformat "new_name" `{"old":"new"}`
```

---

## Type Converters (t_*)

### String/Numeric Conversions
#### t_string_to_number
**Description**: Convert string to number (int/float)  
**Python API**:  
```python
t_string_to_number(data: ConverterData, jsonpath: str, strict: bool = True)
```
**Command Usage**:  
```
t_string_to_number $.price         # Strict mode (default)
t_string_to_number $.quantity false # Non-strict mode
```

#### t_number_to_string
**Description**: Convert number to formatted string  
**Python API**:  
```python
t_number_to_string(data: ConverterData, jsonpath: str, format_spec: str = 'g')
```
**Command Usage**:  
```
t_number_to_string $.temperature    # Default format
t_number_to_string $.ratio ".2f"    # 2 decimal places
```

### Boolean Conversions
#### t_number_to_bool
**Description**: Convert number to boolean (0=False, non-zero=True)  
**Python API**:  
```python
t_number_to_bool(data: ConverterData, jsonpath: str)
```
**Command Usage**:  
```
t_number_to_bool $.is_active
```

#### t_bool_to_number
**Description**: Convert boolean to number (True=1, False=0)  
**Python API**:  
```python
t_bool_to_number(data: ConverterData, jsonpath: str)
```
**Command Usage**:  
```
t_bool_to_number $.flag
```

### Date/Time Conversions
#### t_datetime_to_timestamp
**Description**: Convert datetime string to timestamp  
**Python API**:  
```python
t_datetime_to_timestamp(data: ConverterData, jsonpath: str, format: str = '%Y-%m-%d %H:%M:%S')
```
**Command Usage**:  
```
t_datetime_to_timestamp $.created_at
t_datetime_to_timestamp $.event_date "%Y-%m-%d"
```

#### t_timestamp_to_datetime
**Description**: Convert timestamp to datetime string  
**Python API**:  
```python
t_timestamp_to_datetime(data: ConverterData, jsonpath: str, format: str = '%Y-%m-%d %H:%M:%S')
```
**Command Usage**:  
```
t_timestamp_to_datetime $.timestamp
t_timestamp_to_datetime $.epoch "%H:%M:%S"
```

### Array/String Conversions
#### t_array_to_string
**Description**: Convert array to joined string  
**Python API**:  
```python
t_array_to_string(data: ConverterData, jsonpath: str, separator: str = ', ', filter_nulls: bool = True)
```
**Command Usage**:  
```
t_array_to_string $.tags           # Default comma separator
t_array_to_string $.codes "|" false # Pipe separator, keep nulls
```

#### t_string_to_array
**Description**: Convert string to array  
**Python API**:  
```python
t_string_to_array(data: ConverterData, jsonpath: str, separator: str = None, strip_items: bool = True)
```
**Command Usage**:  
```
t_string_to_array $.csv_line ","    # CSV parsing
t_string_to_array $.chars           # Split into characters
```

### JSON Conversions
#### t_json_string_to_object
**Description**: Parse JSON string to object  
**Python API**:  
```python
t_json_string_to_object(data: ConverterData, jsonpath: str, strict: bool = True)
```
**Command Usage**:  
```
t_json_string_to_object $.config
```

#### t_object_to_json_string
**Description**: Serialize object to JSON string  
**Python API**:  
```python
t_object_to_json_string(data: ConverterData, jsonpath: str, indent: int = None)
```
**Command Usage**:  
```
t_object_to_json_string $.data
t_object_to_json_string $.payload 2  # Pretty-print with 2-space indent
```

### Specialized Conversions
#### t_hex_to_rgb
**Description**: Convert hex color to RGB tuple  
**Python API**:  
```python
t_hex_to_rgb(data: ConverterData, jsonpath: str)
```
**Command Usage**:  
```
t_hex_to_rgb $.color
```

---

## Value Converters (v_*)

### Core Operations
#### v_filter
**Description**: Filter nodes by condition  
**Python API**:  
```python
v_filter(data: ConverterData, jsonpath: str, value=None, operator: str = '==', keep_if_missing: bool = False)
```
**Command Usage**:  
```
v_filter $.price 100 ">"          # Price > 100
v_filter $.name "john" "contains" # Name contains "john"
```

#### v_map
**Description**: Transform values using lambda or JSONPath  
**Python API**:  
```python
v_map(data: ConverterData, transform: str)
```
**Command Usage**:  
```
v_map "lambda x: x*2"             # Multiply all values by 2
v_map $.subitem.price             # Extract subfield
```

#### v_sort
**Description**: Sort nodes by value  
**Python API**:  
```python
v_sort(data: ConverterData, reverse: bool = False, key: str = None)
```
**Command Usage**:  
```
v_sort true                       # Descending sort
v_sort false $.name               # Sort by name field
```

### String Operations
#### v_string_trim
**Description**: Trim whitespace from strings  
**Python API**:  
```python
v_string_trim(data: ConverterData, jsonpath: str = None)
```
**Command Usage**:  
```
v_string_trim           # Trim all strings
v_string_trim $.desc    # Trim specific field
```

#### v_string_replace
**Description**: Replace substrings using regex  
**Python API**:  
```python
v_string_replace(data: ConverterData, jsonpath: str, pattern: str, replacement: str)
```
**Command Usage**:  
```
v_string_replace $.text "\d+" "NUM"  # Replace numbers with "NUM"
```

#### v_string_truncate
**Description**: Truncate strings to max length  
**Python API**:  
```python
v_string_truncate(data: ConverterData, jsonpath: str, max_length: int)
```
**Command Usage**:  
```
v_string_truncate $.title 50  # Limit to 50 chars
```

### Numeric Operations
#### v_number_round
**Description**: Round numeric values  
**Python API**:  
```python
v_number_round(data: ConverterData, jsonpath: str, decimals: int = 0)
```
**Command Usage**:  
```
v_number_round $.amount     # Round to integer
v_number_round $.pi 4       # Round to 4 decimals
```

#### v_number_convert_units
**Description**: Linear unit conversion  
**Python API**:  
```python
v_number_convert_units(data: ConverterData, jsonpath: str, factor: float, offset: float = 0)
```
**Command Usage**:  
```
v_number_convert_units $.temp 1.8 32  # Celsius to Fahrenheit
```

### Null Handling
#### v_null_to_default
**Description**: Replace nulls with default value  
**Python API**:  
```python
v_null_to_default(data: ConverterData, jsonpath: str, default_value: Any)
```
**Command Usage**:  
```
v_null_to_default $.status "unknown"
```

#### v_null_drop
**Description**: Remove null fields  
**Python API**:  
```python
v_null_drop(data: ConverterData, jsonpath: str)
```
**Command Usage**:  
```
v_null_drop $.optional_field
```

### List Operations
#### v_list_unique
**Description**: Remove list duplicates  
**Python API**:  
```python
v_list_unique(data: ConverterData, jsonpath: str)
```
**Command Usage**:  
```
v_list_unique $.tags
```

#### v_list_sort
**Description**: Sort list elements  
**Python API**:  
```python
v_list_sort(data: ConverterData, jsonpath: str, reverse: bool = False, key: str = None)
```
**Command Usage**:  
```
v_list_sort $.numbers true     # Descending sort
v_list_sort $.people false $.age # Sort people by age
```

#### v_list_filter
**Description**: Filter list by condition  
**Python API**:  
```python
v_list_filter(data: ConverterData, jsonpath: str, condition: str)
```
**Command Usage**:  
```
v_list_filter $.scores "lambda x: x > 60"
```