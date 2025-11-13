# Gy Protocol Implementation with Bromelia Integration

A comprehensive Python implementation of the Diameter Gy (Credit-Control) protocol with bromelia library integration for building Diameter applications.

## Features

### 1. Full Bromelia Integration ⭐ NEW
- **Production-ready Diameter stack** using bromelia library
- Automatic detection and fallback to mock mode
- Complete RFC 6733 and RFC 4006 support
- Standards-compliant AVP handling
- See `BROMELIA_INTEGRATION.md` for complete documentation
- Install: `pip install bromelia`

### 2. Listening Mode
- **AVP definitions loaded from YAML file** for easy customization
- No code changes required to add/modify AVPs
- Better readability and maintainability
- See `avp_definitions.yaml` and `AVP_CONFIGURATION_GUIDE.md` for details

### 2. Complete AVP Dictionary
- **45+ AVP definitions** covering all major Gy protocol AVPs
- Support for all AVP data types (Integer, Unsigned, OctetString, UTF8String, Grouped, Enumerated, Time, etc.)
- Proper handling of grouped AVPs (Subscription-Id, Service-Parameter-Info, Granted-Service-Unit, etc.)
- Enumerated value mappings for all enumerated AVPs

### 2. Message Definitions
- Credit-Control-Request (CCR) structure
- Credit-Control-Answer (CCA) structure
- Complete mandatory and optional AVP specifications

### 3. Message Building
- Build CCR Initial messages
- Build CCR Update messages with used/requested units
- Build CCR Terminate messages
- Automatic AVP code resolution from dictionary

### 4. Message Parsing
- Parse CCR messages with full AVP extraction
- Parse CCA messages with quota and cost information
- Handle nested grouped AVPs (3+ levels deep)
- Extract Subscription-Id, Service-Unit, Cost-Information, etc.

### 5. Bromelia Integration
- `GyDiameterApplication` class for real Diameter applications
- Message handler registration
- Statistics tracking (CCR Initial/Update/Terminate counts)
- Error handling and fallback mechanisms

## Installation

```bash
# Clone or download this repository
cd Diameter_Sim

# Optional: Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On Linux/Mac

# Install required dependencies
pip install PyYAML

# Install bromelia for full Diameter functionality (RECOMMENDED)
pip install bromelia

# Verify installation
python -c "import bromelia; print('Bromelia installed successfully!')"
```

### What You Get

**With Bromelia** (Recommended):
- ✅ Full Diameter protocol stack (RFC 6733)
- ✅ Credit-Control Application (RFC 4006)
- ✅ Standards-compliant message handling
- ✅ Production-ready networking
- ✅ Proper AVP encoding/decoding

**Without Bromelia** (Testing only):
- ⚠️ Mock TCP server
- ⚠️ Basic message parsing
- ⚠️ Development/testing only

## Quick Start

### Starting in Listening Mode (Server)

```bash
# Start Diameter server (listens for CCR messages)
python server.py

# Or with custom settings
python server.py --ip 127.0.0.1 --port 3868 --host ocs.example.com

# Or using main.py
python main.py --listen --ip 0.0.0.0 --port 3868
```

The server will:
- Listen for incoming Diameter connections
- Receive and parse CCR messages
- Send CCA responses automatically
- Track statistics (shown on shutdown)

See `LISTENING_MODE_GUIDE.md` for complete documentation.

### Sending Test Messages (Client)

```bash
# Send test CCR to server
python client.py --host 127.0.0.1 --port 3868

# Send multiple test messages
python client.py --host 127.0.0.1 --port 3868 --count 10
```

### Customizing AVPs

The AVP definitions are now in `avp_definitions.yaml`. To add a custom AVP:

```yaml
# Edit avp_definitions.yaml
avps:
  My-Custom-AVP:
    code: 50001
    data_type: UTF8String
    mandatory: false
    protected: false
    vendor_id: null
    description: "My custom AVP"
```

Then use it immediately:

```python
from main import GyAVPDictionary

avp = GyAVPDictionary.get_avp('My-Custom-AVP')
print(f"Code: {avp.code}")  # 50001
```

See `AVP_CONFIGURATION_GUIDE.md` for complete documentation.

### Basic Usage - AVP Dictionary

```python
from main import GyAVPDictionary

# Get AVP information
avp = GyAVPDictionary.get_avp('CC-Request-Type')
print(f"AVP Code: {avp.code}")
print(f"Data Type: {avp.data_type.value}")

# Get AVP code by name
code = GyAVPDictionary.get_code('Subscription-Id')
print(f"Subscription-Id code: {code}")  # 443

# Get enumerated value
req_type = GyAVPDictionary.get_enum_value('CC-Request-Type', 'INITIAL_REQUEST')
print(f"INITIAL_REQUEST value: {req_type}")  # 1

# Print detailed AVP info
GyAVPDictionary.print_avp_info('Subscription-Id')
```

### Building CCR Messages

```python
from main import GyMessageBuilder

builder = GyMessageBuilder()

# Build CCR Initial
ccr_initial = builder.build_ccr_initial(
    session_id="pgw.example.com;1234567890;12345",
    origin_host="pgw.example.com",
    origin_realm="example.com",
    destination_realm="ocs.example.com",
    service_context_id="32251@3gpp.org",
    msisdn="1234567890"
)

# Build CCR Update with usage and request
ccr_update = builder.build_ccr_update(
    session_id="pgw.example.com;1234567890;12345",
    origin_host="pgw.example.com",
    origin_realm="example.com",
    destination_realm="ocs.example.com",
    service_context_id="32251@3gpp.org",
    cc_request_number=1,
    used_units={
        'CC-Time': 300,           # 5 minutes
        'CC-Total-Octets': 1024000  # 1 MB
    },
    requested_units={
        'CC-Time': 600,           # 10 minutes
        'CC-Total-Octets': 2048000  # 2 MB
    }
)

# Build CCR Terminate
ccr_terminate = builder.build_ccr_terminate(
    session_id="pgw.example.com;1234567890;12345",
    origin_host="pgw.example.com",
    origin_realm="example.com",
    destination_realm="ocs.example.com",
    service_context_id="32251@3gpp.org",
    cc_request_number=2,
    used_units={
        'CC-Time': 150,
        'CC-Total-Octets': 512000
    }
)
```

### Parsing Messages

```python
# Parse CCR message
parsed_ccr = builder.parse_ccr(ccr_message_dict)
print(f"Session-Id: {parsed_ccr['session_id']}")
print(f"Request Type: {parsed_ccr['cc_request_type']}")
print(f"Subscription IDs: {parsed_ccr['subscription_ids']}")
print(f"Used Units: {parsed_ccr['used_service_unit']}")
print(f"Requested Units: {parsed_ccr['requested_service_unit']}")

# Parse CCA message
parsed_cca = builder.parse_cca(cca_message_dict)
print(f"Result Code: {parsed_cca['result_code']}")
print(f"Granted Units: {parsed_cca['granted_service_unit']}")
print(f"Cost Info: {parsed_cca['cost_information']}")
print(f"Validity Time: {parsed_cca['validity_time']}")
```

### Bromelia Integration - Diameter Application

```python
from main import GyDiameterApplication

# Configure application
config = {
    'host': 'gy-proxy.example.com',
    'realm': 'example.com',
    'ip': '127.0.0.1',
    'port': 3868,
    'ocs_host': 'ocs.example.com',
    'ocs_realm': 'ocs.example.com',
    'ocs_ip': '10.0.0.100',
    'ocs_port': 3868
}

# Create and start application
app = GyDiameterApplication(config)
app.start()

# The application will automatically:
# - Handle incoming CCR messages
# - Parse AVPs using the dictionary
# - Generate appropriate CCA responses
# - Track statistics

# Get statistics
stats = app.get_statistics()
print(f"CCR Initial: {stats['ccr_initial_received']}")
print(f"CCR Update: {stats['ccr_update_received']}")
print(f"CCR Terminate: {stats['ccr_terminate_received']}")
```

### Proxy Use Case - Modifying Messages

```python
from main import GyProxyWithBromelia

config = {
    'host': 'proxy.example.com',
    'realm': 'example.com',
    'listen_port': 3868,
    'ocs_host': 'ocs.example.com',
    'ocs_realm': 'ocs.example.com'
}

proxy = GyProxyWithBromelia(config)

# The proxy can:
# - Intercept CCR messages
# - Modify AVPs (e.g., transform MSISDN)
# - Add custom Service-Parameter-Info
# - Forward to OCS
# - Modify CCA responses
```

## Architecture

### Class Structure

```
GyAVPDictionary
├── AVP definitions with codes, types, and values
├── Methods to lookup AVPs by name or code
└── Enumerated value mappings

GyMessageBuilder
├── build_ccr_initial()
├── build_ccr_update()
├── build_ccr_terminate()
├── parse_ccr()
├── parse_cca()
└── Helper methods for grouped AVPs

GyDiameterApplication
├── Bromelia integration
├── Message handler registration
├── Statistics tracking
└── CCA generation

GyProxyWithBromelia
├── Proxy functionality
├── Message modification
└── Forwarding logic
```

## AVP Coverage

### Simple AVPs
- CC-Request-Type, CC-Request-Number
- CC-Time, CC-Total-Octets, CC-Input-Octets, CC-Output-Octets
- CC-Service-Specific-Units
- Service-Context-Id, Service-Identifier
- Rating-Group, Validity-Time
- Currency-Code, Cost-Unit
- And 30+ more...

### Grouped AVPs
- **Subscription-Id** (Type + Data)
- **Granted-Service-Unit** (Time, Octets, etc.)
- **Requested-Service-Unit** (Time, Octets, Money, etc.)
- **Used-Service-Unit** (Time, Octets, Money, etc.)
- **Cost-Information** (Unit-Value, Currency, Cost-Unit)
- **Service-Parameter-Info** (Type + Value)
- **User-Equipment-Info** (Type + Value)
- **Unit-Value** (Value-Digits + Exponent)
- **CC-Money** (Unit-Value + Currency-Code)
- **Redirect-Server** (Address-Type + Address)
- **G-S-U-Pool-Reference** (Identifier, Unit-Type, Unit-Value)

### Enumerated Values
- **CC-Request-Type**: INITIAL_REQUEST (1), UPDATE_REQUEST (2), TERMINATION_REQUEST (3), EVENT_REQUEST (4)
- **Subscription-Id-Type**: END_USER_E164 (0), END_USER_IMSI (1), END_USER_SIP_URI (2), END_USER_NAI (3)
- **Final-Unit-Action**: TERMINATE (0), REDIRECT (1), RESTRICT_ACCESS (2)
- **Requested-Action**: DIRECT_DEBITING (0), REFUND_ACCOUNT (1), CHECK_BALANCE (2), PRICE_ENQUIRY (3)
- And more...

## Message Flow Example

### Typical Gy Session

```
1. CCR Initial (Request quota)
   ├── Session-Id: new-session-001
   ├── CC-Request-Type: INITIAL_REQUEST (1)
   ├── CC-Request-Number: 0
   ├── Subscription-Id: MSISDN
   └── Requested-Service-Unit: 1 hour, 100 MB

2. CCA Initial (Grant quota)
   ├── Result-Code: DIAMETER_SUCCESS (2001)
   ├── Granted-Service-Unit: 1 hour, 100 MB
   └── Validity-Time: 3600 seconds

3. CCR Update (Report usage, request more)
   ├── CC-Request-Type: UPDATE_REQUEST (2)
   ├── CC-Request-Number: 1
   ├── Used-Service-Unit: 300 seconds, 10 MB
   └── Requested-Service-Unit: 1 hour, 100 MB

4. CCA Update (Grant more quota)
   ├── Result-Code: DIAMETER_SUCCESS (2001)
   └── Granted-Service-Unit: 1 hour, 100 MB

5. CCR Terminate (Final usage)
   ├── CC-Request-Type: TERMINATION_REQUEST (3)
   ├── CC-Request-Number: 2
   └── Used-Service-Unit: 450 seconds, 15 MB

6. CCA Terminate (Acknowledge)
   └── Result-Code: DIAMETER_SUCCESS (2001)
```

## Testing

Run the example program:

```bash
python main.py
```

This will:
1. Display AVP dictionary examples
2. Build sample CCR messages (Initial, Update, Terminate)
3. Parse CCR messages
4. Initialize a Diameter application
5. List all 45+ available AVPs

## Integration Notes

### With Bromelia Library

The implementation is designed to work with the [bromelia](https://github.com/heimiricmr/bromelia) library. When bromelia is installed:

- Full Diameter stack functionality
- Real network communication
- Proper message encoding/decoding
- AVP manipulation using standard Diameter types

### Without Bromelia

The implementation works standalone for:
- AVP dictionary lookups
- Message structure building (as dictionaries)
- Message parsing
- Protocol logic development
- Testing and validation

## Use Cases

1. **OCS (Online Charging System)**: Implement a full OCS using `GyDiameterApplication`
2. **PCRF Integration**: Parse Gy messages for policy decisions
3. **Diameter Proxy**: Use `GyProxyWithBromelia` for message routing and modification
4. **Testing Tools**: Generate test CCR/CCA messages for validation
5. **Protocol Analysis**: Parse captured Diameter messages
6. **Documentation**: Reference for Gy protocol AVPs and message structures

## Protocol References

- **RFC 4006**: Diameter Credit-Control Application
- **3GPP TS 32.251**: Packet Switched (PS) domain charging
- **3GPP TS 32.299**: Diameter charging applications

## License

This implementation is provided as-is for educational and development purposes.

## Contributing

Contributions are welcome! Areas for enhancement:
- Additional AVPs from 3GPP specifications
- Multiple-Services-Credit-Control (MSCC) support
- More comprehensive CCA generation logic
- Unit tests
- Performance optimizations

## Support

For issues or questions about:
- This implementation: Check the code comments and examples
- Bromelia library: Visit https://github.com/heimiricmr/bromelia
- Gy Protocol: Refer to RFC 4006 and 3GPP specifications

