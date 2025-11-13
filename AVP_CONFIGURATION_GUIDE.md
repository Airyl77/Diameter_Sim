# AVP Configuration Guide

## Overview

The Gy Protocol implementation now uses an external YAML configuration file (`avp_definitions.yaml`) to define all AVP (Attribute-Value Pair) definitions. This provides several advantages:

- ✅ **Better Readability**: YAML format is human-readable and easy to understand
- ✅ **Easy Customization**: Add, modify, or remove AVPs without touching code
- ✅ **Centralized Configuration**: All AVP definitions in one place
- ✅ **Version Control Friendly**: Easy to track changes in AVP definitions
- ✅ **Extensibility**: Quickly add custom or vendor-specific AVPs

## YAML File Structure

### Basic Format

```yaml
avps:
  AVP-Name:
    code: <AVP code number>
    data_type: <Data type string>
    mandatory: <true|false>
    protected: <true|false>
    vendor_id: <vendor ID or null>
    description: <Optional description>
    # For Enumerated types:
    enumerated_values:
      VALUE_NAME: <integer>
    # For Grouped types:
    grouped_avps:
      - Child-AVP-Name-1
      - Child-AVP-Name-2
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `code` | Yes | AVP code number (integer) |
| `data_type` | Yes | AVP data type (see supported types below) |
| `mandatory` | Yes | Whether the M (Mandatory) flag is set |
| `protected` | Yes | Whether the P (Protected) flag is set |
| `vendor_id` | Yes | Vendor ID (use `null` for IETF/standard AVPs) |
| `description` | No | Human-readable description of the AVP |
| `enumerated_values` | Conditional | Dictionary of name/value pairs (for Enumerated type only) |
| `grouped_avps` | Conditional | List of child AVP names (for Grouped type only) |

### Supported Data Types

- `OctetString` - Arbitrary binary data
- `Integer32` - 32-bit signed integer
- `Integer64` - 64-bit signed integer
- `Unsigned32` - 32-bit unsigned integer
- `Unsigned64` - 64-bit unsigned integer
- `Float32` - 32-bit floating point
- `Float64` - 64-bit floating point
- `Grouped` - Container for other AVPs
- `UTF8String` - UTF-8 encoded text
- `DiameterIdentity` - Diameter identity (FQDN)
- `DiameterURI` - Diameter URI
- `Enumerated` - Integer with predefined values
- `Time` - Timestamp (seconds since 1900)
- `Address` - IP address (IPv4 or IPv6)

## Examples

### 1. Simple Unsigned32 AVP

```yaml
CC-Request-Number:
  code: 415
  data_type: Unsigned32
  mandatory: true
  protected: false
  vendor_id: null
  description: "Sequence number of request"
```

### 2. Enumerated AVP

```yaml
CC-Request-Type:
  code: 416
  data_type: Enumerated
  mandatory: true
  protected: false
  vendor_id: null
  description: "Type of credit-control request"
  enumerated_values:
    INITIAL_REQUEST: 1
    UPDATE_REQUEST: 2
    TERMINATION_REQUEST: 3
    EVENT_REQUEST: 4
```

### 3. Grouped AVP

```yaml
Subscription-Id:
  code: 443
  data_type: Grouped
  mandatory: true
  protected: false
  vendor_id: null
  description: "Subscription identifier"
  grouped_avps:
    - Subscription-Id-Type
    - Subscription-Id-Data
```

### 4. Vendor-Specific AVP

```yaml
Custom-Vendor-AVP:
  code: 10001
  data_type: UTF8String
  mandatory: false
  protected: false
  vendor_id: 12345  # Your vendor ID
  description: "Custom vendor-specific AVP"
```

## Adding New AVPs

To add a new AVP to your implementation:

1. Open `avp_definitions.yaml`
2. Add your AVP definition under the `avps:` section
3. Follow the format shown in the examples above
4. Save the file
5. Run your application - the new AVP will be automatically loaded

### Example: Adding a Custom AVP

```yaml
avps:
  # ... existing AVPs ...
  
  Custom-Session-Info:
    code: 50001
    data_type: UTF8String
    mandatory: false
    protected: false
    vendor_id: null
    description: "Custom session information field"
```

No code changes required! The AVP will be immediately available:

```python
from main import GyAVPDictionary

avp = GyAVPDictionary.get_avp('Custom-Session-Info')
print(f"Code: {avp.code}, Type: {avp.data_type.value}")
```

## Modifying Existing AVPs

To modify an existing AVP:

1. Locate the AVP in `avp_definitions.yaml`
2. Modify the desired fields
3. Save the file
4. Restart your application

**Example**: Change an AVP from mandatory to optional:

```yaml
Some-Optional-AVP:
  code: 999
  data_type: UTF8String
  mandatory: false  # Changed from true
  protected: false
  vendor_id: null
```

## Validation and Error Handling

The loader includes built-in validation:

- ✅ File not found → Warning message, empty dictionary used
- ✅ Invalid YAML syntax → Error message, empty dictionary used
- ✅ Unknown data type → Warning, defaults to OctetString
- ✅ Missing required fields → Skipped with warning

Check the console output when starting your application for any warnings or errors.

## File Location

The YAML file must be located in the same directory as `main.py`:

```
Diameter_Sim/
├── main.py
├── avp_definitions.yaml  ← Here
├── example.py
└── test.py
```

To use a different location, specify the path when loading:

```python
# Not typically needed - auto-loads from default location
GyAVPDictionary._load_avps_from_yaml('/path/to/custom_avps.yaml')
```

## Best Practices

### 1. Group Related AVPs with Comments

```yaml
avps:
  # =========================================================================
  # Credit-Control AVPs
  # =========================================================================
  
  CC-Request-Type:
    code: 416
    # ... definition ...
  
  CC-Request-Number:
    code: 415
    # ... definition ...
```

### 2. Add Descriptions

Always add descriptions to make the configuration self-documenting:

```yaml
Service-Context-Id:
  code: 461
  data_type: UTF8String
  mandatory: true
  protected: false
  vendor_id: null
  description: "Service context identifier (e.g., 32251@3gpp.org for Gy)"
```

### 3. Use Consistent Naming

- Use the official AVP name from the specification
- Use hyphens (-) in AVP names, underscores (_) in enum values
- Example: `CC-Request-Type` (AVP name), `INITIAL_REQUEST` (enum value)

### 4. Version Control

Track your YAML configuration in version control to maintain history of changes:

```bash
git add avp_definitions.yaml
git commit -m "Added custom AVPs for vendor extension"
```

### 5. Backup Before Major Changes

Before making significant changes:

```bash
cp avp_definitions.yaml avp_definitions.yaml.backup
```

## Common Patterns

### Pattern 1: Service Unit AVP Group

```yaml
Granted-Service-Unit:
  code: 431
  data_type: Grouped
  mandatory: true
  protected: false
  vendor_id: null
  description: "Granted service units (quota)"
  grouped_avps:
    - Tariff-Time-Change
    - CC-Time
    - CC-Total-Octets
    - CC-Input-Octets
    - CC-Output-Octets
    - CC-Service-Specific-Units
```

### Pattern 2: Money Representation

```yaml
Unit-Value:
  code: 445
  data_type: Grouped
  mandatory: true
  protected: false
  vendor_id: null
  description: "Decimal value representation"
  grouped_avps:
    - Value-Digits
    - Exponent

CC-Money:
  code: 413
  data_type: Grouped
  mandatory: true
  protected: false
  vendor_id: null
  description: "Monetary amount"
  grouped_avps:
    - Unit-Value
    - Currency-Code
```

### Pattern 3: Subscription Identifier

```yaml
Subscription-Id-Type:
  code: 450
  data_type: Enumerated
  mandatory: true
  protected: false
  vendor_id: null
  description: "Type of subscription identifier"
  enumerated_values:
    END_USER_E164: 0
    END_USER_IMSI: 1
    END_USER_SIP_URI: 2
    END_USER_NAI: 3
    END_USER_PRIVATE: 4

Subscription-Id-Data:
  code: 444
  data_type: UTF8String
  mandatory: true
  protected: false
  vendor_id: null
  description: "Subscription identifier value (MSISDN, IMSI, etc.)"

Subscription-Id:
  code: 443
  data_type: Grouped
  mandatory: true
  protected: false
  vendor_id: null
  description: "Subscription identifier"
  grouped_avps:
    - Subscription-Id-Type
    - Subscription-Id-Data
```

## Troubleshooting

### Problem: AVP Not Found

**Symptom**: `AVP 'My-AVP' not found`

**Solution**: 
1. Check the AVP name spelling in YAML
2. Ensure YAML file is in the correct location
3. Check for YAML syntax errors
4. Verify the AVP is under the `avps:` key

### Problem: Data Type Error

**Symptom**: `Warning: Unknown data type 'string' for AVP My-AVP`

**Solution**: Use the exact data type names listed in "Supported Data Types" section. For example, use `UTF8String` not `string`.

### Problem: Enumerated Values Not Working

**Symptom**: `get_enum_value` returns None

**Solution**:
1. Verify the AVP has `data_type: Enumerated`
2. Check `enumerated_values` is properly indented
3. Verify the enum value name spelling

### Problem: Grouped AVP Children Not Found

**Symptom**: Child AVPs return None

**Solution**:
1. Ensure all child AVPs are defined in the YAML
2. Check that child AVP names match exactly (case-sensitive)
3. Verify `grouped_avps` is a list (starts with `-`)

## Migration from Hardcoded AVPs

If you have hardcoded AVP definitions, here's how to migrate:

### Old (Hardcoded):

```python
'CC-Time': AVPDefinition(
    code=420,
    name='CC-Time',
    data_type=AVPDataType.UNSIGNED32,
    mandatory=True,
    protected=False
)
```

### New (YAML):

```yaml
CC-Time:
  code: 420
  data_type: Unsigned32
  mandatory: true
  protected: false
  vendor_id: null
  description: "Time in seconds"
```

## Performance Considerations

- YAML file is loaded once at first access and cached
- Subsequent AVP lookups use in-memory dictionary (O(1) lookup)
- No performance penalty compared to hardcoded definitions
- File is automatically reloaded if you restart the application

## Reference

For more information on Diameter AVPs:
- RFC 6733 - Diameter Base Protocol
- RFC 4006 - Diameter Credit-Control Application
- 3GPP TS 32.299 - Diameter charging applications

For YAML syntax:
- https://yaml.org/spec/
- https://learnxinyminutes.com/docs/yaml/

