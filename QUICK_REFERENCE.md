# Quick Reference: YAML AVP Configuration

## Common Tasks

### Add a Simple AVP

```yaml
My-New-AVP:
  code: 50001
  data_type: UTF8String
  mandatory: false
  protected: false
  vendor_id: null
  description: "Description here"
```

### Add an Enumerated AVP

```yaml
My-Status:
  code: 50002
  data_type: Enumerated
  mandatory: true
  protected: false
  vendor_id: null
  enumerated_values:
    SUCCESS: 0
    FAILURE: 1
    PENDING: 2
```

### Add a Grouped AVP

```yaml
My-Info:
  code: 50003
  data_type: Grouped
  mandatory: false
  protected: false
  vendor_id: null
  grouped_avps:
    - My-Type
    - My-Value
```

### Add a Vendor-Specific AVP

```yaml
Vendor-Custom-AVP:
  code: 10001
  data_type: UTF8String
  mandatory: false
  protected: false
  vendor_id: 12345  # Your vendor ID
```

## Data Types Quick Reference

| YAML Value | Python Type | Description |
|------------|-------------|-------------|
| `OctetString` | bytes | Binary data |
| `UTF8String` | str | Text string |
| `Unsigned32` | int | 0 to 2^32-1 |
| `Unsigned64` | int | 0 to 2^64-1 |
| `Integer32` | int | -2^31 to 2^31-1 |
| `Integer64` | int | -2^63 to 2^63-1 |
| `Enumerated` | int | Predefined values |
| `Grouped` | dict | Container for AVPs |
| `Time` | int | Unix timestamp |

## Python Usage

```python
from main import GyAVPDictionary

# Get AVP definition
avp = GyAVPDictionary.get_avp('My-New-AVP')

# Get AVP code
code = GyAVPDictionary.get_code('My-New-AVP')

# Get enumerated value
value = GyAVPDictionary.get_enum_value('My-Status', 'SUCCESS')

# Check if grouped
is_grouped = GyAVPDictionary.is_grouped('My-Info')

# List all AVPs
all_avps = GyAVPDictionary.list_all_avps()
```

## File Location

```
Diameter_Sim/avp_definitions.yaml
```

## Reload After Changes

Restart your Python application to load changes.

## More Information

See `AVP_CONFIGURATION_GUIDE.md` for complete documentation.

