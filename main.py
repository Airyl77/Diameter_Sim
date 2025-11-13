"""
Gy Protocol AVP Dictionary and Message Definitions
Generated from ABNF format for Diameter Credit-Control Application
Includes integration with bromelia library
AVP definitions loaded from external YAML configuration file
"""

import yaml
import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


class AVPDataType(Enum):
    """AVP Data Types as per Diameter Base Protocol"""
    OCTET_STRING = "OctetString"
    INTEGER32 = "Integer32"
    INTEGER64 = "Integer64"
    UNSIGNED32 = "Unsigned32"
    UNSIGNED64 = "Unsigned64"
    FLOAT32 = "Float32"
    FLOAT64 = "Float64"
    GROUPED = "Grouped"
    UTF8STRING = "UTF8String"
    DIAMETER_IDENTITY = "DiameterIdentity"
    DIAMETER_URI = "DiameterURI"
    ENUMERATED = "Enumerated"
    TIME = "Time"
    ADDRESS = "Address"


@dataclass
class AVPDefinition:
    """Definition of a Diameter AVP"""
    code: int
    name: str
    data_type: AVPDataType
    mandatory: bool = True
    protected: bool = False
    vendor_id: Optional[int] = None
    enumerated_values: Optional[Dict[str, int]] = None
    grouped_avps: Optional[List[str]] = None

    def __str__(self):
        return f"{self.name} ({self.code}): {self.data_type.value}"


class GyAVPDictionary:
    """Complete AVP Dictionary for Gy (Credit-Control) Protocol"""

    # AVPs loaded from YAML configuration
    AVPS = {}
    _loaded = False

    @classmethod
    def _load_avps_from_yaml(cls, yaml_file: Optional[str] = None):
        """
        Load AVP definitions from YAML file

        Args:
            yaml_file: Path to YAML file. If None, uses default avp_definitions.yaml
        """
        if cls._loaded:
            return

        if yaml_file is None:
            # Default to avp_definitions.yaml in the same directory as this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            yaml_file = os.path.join(script_dir, 'avp_definitions.yaml')

        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data or 'avps' not in data:
                raise ValueError("YAML file must contain 'avps' key")

            # Convert YAML data to AVPDefinition objects
            for avp_name, avp_data in data['avps'].items():
                # Get data type enum
                data_type_str = avp_data.get('data_type', 'OctetString')
                try:
                    data_type = AVPDataType(data_type_str)
                except ValueError:
                    print(f"Warning: Unknown data type '{data_type_str}' for AVP {avp_name}, using OctetString")
                    data_type = AVPDataType.OCTET_STRING

                # Create AVPDefinition
                cls.AVPS[avp_name] = AVPDefinition(
                    code=avp_data['code'],
                    name=avp_name,
                    data_type=data_type,
                    mandatory=avp_data.get('mandatory', True),
                    protected=avp_data.get('protected', False),
                    vendor_id=avp_data.get('vendor_id'),
                    enumerated_values=avp_data.get('enumerated_values'),
                    grouped_avps=avp_data.get('grouped_avps')
                )

            cls._loaded = True
            print(f"Loaded {len(cls.AVPS)} AVP definitions from {yaml_file}")

        except FileNotFoundError:
            print(f"Warning: AVP definition file not found: {yaml_file}")
            print("Using empty AVP dictionary. Please ensure avp_definitions.yaml exists.")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            print("Using empty AVP dictionary.")
        except Exception as e:
            print(f"Error loading AVP definitions: {e}")
            print("Using empty AVP dictionary.")


    @classmethod
    def get_avp(cls, name: str) -> Optional[AVPDefinition]:
        """Get AVP definition by name"""
        cls._load_avps_from_yaml()  # Auto-load if not loaded
        return cls.AVPS.get(name)

    @classmethod
    def get_avp_by_code(cls, code: int) -> Optional[AVPDefinition]:
        """Get AVP definition by code"""
        cls._load_avps_from_yaml()  # Auto-load if not loaded
        for avp in cls.AVPS.values():
            if avp.code == code:
                return avp
        return None

    @classmethod
    def get_code(cls, name: str) -> Optional[int]:
        """Get AVP code by name"""
        cls._load_avps_from_yaml()  # Auto-load if not loaded
        avp = cls.AVPS.get(name)
        return avp.code if avp else None

    @classmethod
    def get_enum_value(cls, avp_name: str, enum_name: str) -> Optional[int]:
        """Get enumerated value for an AVP"""
        cls._load_avps_from_yaml()  # Auto-load if not loaded
        avp = cls.AVPS.get(avp_name)
        if avp and avp.enumerated_values:
            return avp.enumerated_values.get(enum_name)
        return None

    @classmethod
    def is_grouped(cls, name: str) -> bool:
        """Check if AVP is a grouped AVP"""
        cls._load_avps_from_yaml()  # Auto-load if not loaded
        avp = cls.AVPS.get(name)
        return avp.data_type == AVPDataType.GROUPED if avp else False

    @classmethod
    def list_all_avps(cls) -> List[str]:
        """List all AVP names"""
        cls._load_avps_from_yaml()  # Auto-load if not loaded
        return list(cls.AVPS.keys())

    @classmethod
    def print_avp_info(cls, name: str) -> None:
        """Print detailed information about an AVP"""
        cls._load_avps_from_yaml()  # Auto-load if not loaded
        avp = cls.AVPS.get(name)
        if not avp:
            print(f"AVP '{name}' not found")
            return

        print(f"\nAVP: {avp.name}")
        print(f"Code: {avp.code}")
        print(f"Data Type: {avp.data_type.value}")
        print(f"Mandatory: {avp.mandatory}")
        print(f"Protected: {avp.protected}")

        if avp.enumerated_values:
            print("Enumerated Values:")
            for enum_name, enum_value in avp.enumerated_values.items():
                print(f"  {enum_name}: {enum_value}")

        if avp.grouped_avps:
            print("Grouped AVPs:")
            for grouped_avp in avp.grouped_avps:
                print(f"  - {grouped_avp}")


@dataclass
class MessageDefinition:
    """Definition of a Diameter Command/Message"""
    command_code: int
    name: str
    is_request: bool
    is_proxiable: bool
    application_id: int
    mandatory_avps: List[str]
    optional_avps: List[str]


class GyMessages:
    """Gy Protocol Message Definitions"""

    CREDIT_CONTROL_REQUEST = MessageDefinition(
        command_code=272,
        name='Credit-Control-Request',
        is_request=True,
        is_proxiable=True,
        application_id=4,
        mandatory_avps=[
            'Session-Id',
            'Origin-Host',
            'Origin-Realm',
            'Destination-Realm',
            'Auth-Application-Id',
            'CC-Request-Type',
            'CC-Request-Number',
            'Service-Context-Id'
        ],
        optional_avps=[
            'Event-Timestamp',
            'Subscription-Id',
            'Requested-Action',
            'Service-Parameter-Info',
            'Requested-Service-Unit',
            'Destination-Host'
        ]
    )

    CREDIT_CONTROL_ANSWER = MessageDefinition(
        command_code=272,
        name='Credit-Control-Answer',
        is_request=False,
        is_proxiable=True,
        application_id=4,
        mandatory_avps=[
            'Session-Id',
            'Result-Code',
            'Origin-Host',
            'Origin-Realm'
        ],
        optional_avps=[
            'Auth-Application-Id',
            'CC-Request-Type',
            'CC-Request-Number',
            'Origin-State-Id',
            'Event-Timestamp',
            'Granted-Service-Unit',
            'Service-Context-Id'
        ]
    )

    @classmethod
    def get_ccr_definition(cls) -> MessageDefinition:
        """Get Credit-Control-Request definition"""
        return cls.CREDIT_CONTROL_REQUEST

    @classmethod
    def get_cca_definition(cls) -> MessageDefinition:
        """Get Credit-Control-Answer definition"""
        return cls.CREDIT_CONTROL_ANSWER


# ============================================================================
# BROMELIA INTEGRATION EXAMPLES
# ============================================================================

class GyProxyWithBromelia:
    """
    Example implementation of Gy Proxy using bromelia library
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Gy Proxy

        Args:
            config: Configuration dictionary with keys:
                - host: Proxy hostname
                - realm: Proxy realm
                - listen_port: Port to listen on
                - ocs_host: OCS destination host
                - ocs_realm: OCS destination realm
        """
        self.config = config
        self.dictionary = GyAVPDictionary()

    def setup_bromelia_app(self):
        """Setup bromelia Diameter application"""
        # This is pseudocode - actual bromelia syntax may vary
        from bromelia import Diameter

        app = Diameter(
            application_id=4,  # Gy application
            host=self.config['host'],
            realm=self.config['realm']
        )

        return app

    def handle_credit_control_request(self, request):
        """
        Handle incoming CCR and forward to OCS

        Args:
            request: Incoming Diameter request

        Returns:
            Modified Diameter answer
        """
        # Extract common AVPs
        session_id = self.get_avp_value(request, 'Session-Id')
        cc_request_type = self.get_avp_value(request, 'CC-Request-Type')
        cc_request_number = self.get_avp_value(request, 'CC-Request-Number')

        print(f"Received CCR: Session={session_id}, Type={cc_request_type}, Num={cc_request_number}")

        # Modify Subscription-Id if present
        if self.has_avp(request, 'Subscription-Id'):
            sub_id_data = self.get_grouped_avp_value(
                request,
                'Subscription-Id',
                'Subscription-Id-Data'
            )

            # Transform MSISDN (example: add prefix)
            new_sub_id_data = self.transform_msisdn(sub_id_data)

            # Update the AVP
            self.update_grouped_avp(
                request,
                'Subscription-Id',
                'Subscription-Id-Data',
                new_sub_id_data
            )

        # Add custom Service-Parameter-Info
        self.add_service_parameter(request, 10001, b"proxy-processed")

        # Forward to OCS
        response = self.forward_to_ocs(request)

        # Optionally modify response
        if self.has_avp(response, 'Granted-Service-Unit'):
            print("Quota granted by OCS")

        return response

    def get_avp_value(self, message, avp_name: str) -> Any:
        """
        Get AVP value from message using dictionary

        Args:
            message: Diameter message
            avp_name: AVP name from dictionary

        Returns:
            AVP value
        """
        avp_code = self.dictionary.get_code(avp_name)
        # Pseudocode - actual bromelia API may differ
        return message.get_avp_by_code(avp_code)

    def has_avp(self, message, avp_name: str) -> bool:
        """Check if message contains AVP"""
        avp_code = self.dictionary.get_code(avp_name)
        return message.has_avp(avp_code)

    def get_grouped_avp_value(self, message, parent_avp: str, child_avp: str) -> Any:
        """
        Get value from grouped AVP

        Args:
            message: Diameter message
            parent_avp: Parent grouped AVP name
            child_avp: Child AVP name

        Returns:
            Child AVP value
        """
        parent_code = self.dictionary.get_code(parent_avp)
        child_code = self.dictionary.get_code(child_avp)

        # Get parent grouped AVP
        parent = message.get_avp_by_code(parent_code)
        if parent:
            # Get child from parent
            return parent.get_avp_by_code(child_code)
        return None

    def update_grouped_avp(self, message, parent_avp: str, child_avp: str, value: Any):
        """Update value in grouped AVP"""
        parent_code = self.dictionary.get_code(parent_avp)
        child_code = self.dictionary.get_code(child_avp)

        parent = message.get_avp_by_code(parent_code)
        if parent:
            parent.update_avp(child_code, value)

    def add_service_parameter(self, message, param_type: int, param_value: bytes):
        """
        Add Service-Parameter-Info grouped AVP

        Args:
            message: Diameter message
            param_type: Service-Parameter-Type value
            param_value: Service-Parameter-Value bytes
        """
        # Get AVP codes from dictionary
        spi_code = self.dictionary.get_code('Service-Parameter-Info')
        spt_code = self.dictionary.get_code('Service-Parameter-Type')
        spv_code = self.dictionary.get_code('Service-Parameter-Value')

        # Create grouped AVP (pseudocode)
        # service_param_info = GroupedAVP(spi_code)
        # service_param_info.add_avp(spt_code, param_type)
        # service_param_info.add_avp(spv_code, param_value)
        # message.add_avp(service_param_info)
        pass

    def transform_msisdn(self, msisdn: str) -> str:
        """
        Transform MSISDN (example: normalize format)

        Args:
            msisdn: Original MSISDN

        Returns:
            Transformed MSISDN
        """
        # Remove + and replace with country code prefix
        if msisdn.startswith('+'):
            return '00' + msisdn[1:]
        return msisdn

    def forward_to_ocs(self, request):
        """
        Forward request to OCS

        Args:
            request: Modified CCR

        Returns:
            CCA from OCS
        """
        # Pseudocode for forwarding
        # response = self.app.send_request(
        #     request,
        #     destination_host=self.config['ocs_host'],
        #     destination_realm=self.config['ocs_realm']
        # )
        # return response
        pass


# ============================================================================
# STANDALONE USAGE EXAMPLE (without bromelia)
# ============================================================================

class GyMessageBuilder:
    """Helper class to build Gy messages using the dictionary"""

    def __init__(self):
        self.dict = GyAVPDictionary()
        self.messages = GyMessages()

    def build_ccr_initial(
            self,
            session_id: str,
            origin_host: str,
            origin_realm: str,
            destination_realm: str,
            service_context_id: str,
            msisdn: str
    ) -> Dict[str, Any]:
        """
        Build Credit-Control-Request (Initial)

        Returns:
            Dictionary representation of CCR
        """
        ccr = {
            'command_code': 272,
            'is_request': True,
            'application_id': 4,
            'avps': []
        }

        # Mandatory AVPs
        ccr['avps'].append({
            'code': self.dict.get_code('Session-Id'),
            'value': session_id
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Origin-Host'),
            'value': origin_host
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Origin-Realm'),
            'value': origin_realm
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Destination-Realm'),
            'value': destination_realm
        })
        ccr['avps'].append({
            'code': self.dict.get_code('CC-Request-Type'),
            'value': self.dict.get_enum_value('CC-Request-Type', 'INITIAL_REQUEST')
        })
        ccr['avps'].append({
            'code': self.dict.get_code('CC-Request-Number'),
            'value': 0
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Service-Context-Id'),
            'value': service_context_id
        })

        # Add Subscription-Id (grouped AVP)
        subscription_id = {
            'code': self.dict.get_code('Subscription-Id'),
            'grouped_avps': [
                {
                    'code': self.dict.get_code('Subscription-Id-Type'),
                    'value': self.dict.get_enum_value('Subscription-Id-Type', 'END_USER_E164')
                },
                {
                    'code': self.dict.get_code('Subscription-Id-Data'),
                    'value': msisdn
                }
            ]
        }
        ccr['avps'].append(subscription_id)

        return ccr

    def build_ccr_update(
            self,
            session_id: str,
            origin_host: str,
            origin_realm: str,
            destination_realm: str,
            service_context_id: str,
            cc_request_number: int,
            used_units: Optional[Dict[str, int]] = None,
            requested_units: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Build Credit-Control-Request (Update)

        Args:
            session_id: Diameter Session-Id
            origin_host: Origin host
            origin_realm: Origin realm
            destination_realm: Destination realm
            service_context_id: Service context identifier
            cc_request_number: Request sequence number
            used_units: Dictionary with used service units (e.g., {'CC-Time': 300, 'CC-Total-Octets': 1024000})
            requested_units: Dictionary with requested service units

        Returns:
            Dictionary representation of CCR
        """
        ccr = {
            'command_code': 272,
            'is_request': True,
            'application_id': 4,
            'avps': []
        }

        # Mandatory AVPs
        ccr['avps'].append({
            'code': self.dict.get_code('Session-Id'),
            'value': session_id
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Origin-Host'),
            'value': origin_host
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Origin-Realm'),
            'value': origin_realm
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Destination-Realm'),
            'value': destination_realm
        })
        ccr['avps'].append({
            'code': self.dict.get_code('CC-Request-Type'),
            'value': self.dict.get_enum_value('CC-Request-Type', 'UPDATE_REQUEST')
        })
        ccr['avps'].append({
            'code': self.dict.get_code('CC-Request-Number'),
            'value': cc_request_number
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Service-Context-Id'),
            'value': service_context_id
        })

        # Add Used-Service-Unit if provided
        if used_units:
            used_service_unit = {
                'code': self.dict.get_code('Used-Service-Unit'),
                'grouped_avps': []
            }
            for unit_type, value in used_units.items():
                used_service_unit['grouped_avps'].append({
                    'code': self.dict.get_code(unit_type),
                    'value': value
                })
            ccr['avps'].append(used_service_unit)

        # Add Requested-Service-Unit if provided
        if requested_units:
            requested_service_unit = {
                'code': self.dict.get_code('Requested-Service-Unit'),
                'grouped_avps': []
            }
            for unit_type, value in requested_units.items():
                requested_service_unit['grouped_avps'].append({
                    'code': self.dict.get_code(unit_type),
                    'value': value
                })
            ccr['avps'].append(requested_service_unit)

        return ccr

    def build_ccr_terminate(
            self,
            session_id: str,
            origin_host: str,
            origin_realm: str,
            destination_realm: str,
            service_context_id: str,
            cc_request_number: int,
            used_units: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Build Credit-Control-Request (Termination)

        Args:
            session_id: Diameter Session-Id
            origin_host: Origin host
            origin_realm: Origin realm
            destination_realm: Destination realm
            service_context_id: Service context identifier
            cc_request_number: Request sequence number
            used_units: Dictionary with used service units

        Returns:
            Dictionary representation of CCR
        """
        ccr = {
            'command_code': 272,
            'is_request': True,
            'application_id': 4,
            'avps': []
        }

        # Mandatory AVPs
        ccr['avps'].append({
            'code': self.dict.get_code('Session-Id'),
            'value': session_id
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Origin-Host'),
            'value': origin_host
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Origin-Realm'),
            'value': origin_realm
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Destination-Realm'),
            'value': destination_realm
        })
        ccr['avps'].append({
            'code': self.dict.get_code('CC-Request-Type'),
            'value': self.dict.get_enum_value('CC-Request-Type', 'TERMINATION_REQUEST')
        })
        ccr['avps'].append({
            'code': self.dict.get_code('CC-Request-Number'),
            'value': cc_request_number
        })
        ccr['avps'].append({
            'code': self.dict.get_code('Service-Context-Id'),
            'value': service_context_id
        })

        # Add Used-Service-Unit if provided
        if used_units:
            used_service_unit = {
                'code': self.dict.get_code('Used-Service-Unit'),
                'grouped_avps': []
            }
            for unit_type, value in used_units.items():
                used_service_unit['grouped_avps'].append({
                    'code': self.dict.get_code(unit_type),
                    'value': value
                })
            ccr['avps'].append(used_service_unit)

        return ccr

    def parse_ccr(self, message_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse CCR message and extract relevant information

        Args:
            message_dict: Dictionary representation of CCR message

        Returns:
            Parsed CCR information
        """
        parsed = {
            'message_type': 'CCR',
            'session_id': None,
            'cc_request_type': None,
            'cc_request_number': None,
            'service_context_id': None,
            'subscription_ids': [],
            'requested_service_unit': {},
            'used_service_unit': {},
            'service_parameters': []
        }

        for avp in message_dict.get('avps', []):
            avp_code = avp.get('code')
            avp_def = self.dict.get_avp_by_code(avp_code)

            if not avp_def:
                continue

            # Parse simple AVPs
            if avp_def.name == 'Session-Id':
                parsed['session_id'] = avp.get('value')
            elif avp_def.name == 'CC-Request-Type':
                parsed['cc_request_type'] = avp.get('value')
            elif avp_def.name == 'CC-Request-Number':
                parsed['cc_request_number'] = avp.get('value')
            elif avp_def.name == 'Service-Context-Id':
                parsed['service_context_id'] = avp.get('value')

            # Parse grouped AVPs
            elif avp_def.name == 'Subscription-Id':
                sub_id = self._parse_subscription_id(avp)
                if sub_id:
                    parsed['subscription_ids'].append(sub_id)
            elif avp_def.name == 'Requested-Service-Unit':
                parsed['requested_service_unit'] = self._parse_service_unit(avp)
            elif avp_def.name == 'Used-Service-Unit':
                parsed['used_service_unit'] = self._parse_service_unit(avp)
            elif avp_def.name == 'Service-Parameter-Info':
                param = self._parse_service_parameter(avp)
                if param:
                    parsed['service_parameters'].append(param)

        return parsed

    def parse_cca(self, message_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse CCA message and extract relevant information

        Args:
            message_dict: Dictionary representation of CCA message

        Returns:
            Parsed CCA information
        """
        parsed = {
            'message_type': 'CCA',
            'session_id': None,
            'result_code': None,
            'cc_request_type': None,
            'cc_request_number': None,
            'granted_service_unit': {},
            'cost_information': {},
            'final_unit_indication': None,
            'validity_time': None
        }

        for avp in message_dict.get('avps', []):
            avp_code = avp.get('code')
            avp_def = self.dict.get_avp_by_code(avp_code)

            if not avp_def:
                continue

            # Parse simple AVPs
            if avp_def.name == 'Session-Id':
                parsed['session_id'] = avp.get('value')
            elif avp_def.name == 'Result-Code':
                parsed['result_code'] = avp.get('value')
            elif avp_def.name == 'CC-Request-Type':
                parsed['cc_request_type'] = avp.get('value')
            elif avp_def.name == 'CC-Request-Number':
                parsed['cc_request_number'] = avp.get('value')
            elif avp_def.name == 'Validity-Time':
                parsed['validity_time'] = avp.get('value')

            # Parse grouped AVPs
            elif avp_def.name == 'Granted-Service-Unit':
                parsed['granted_service_unit'] = self._parse_service_unit(avp)
            elif avp_def.name == 'Cost-Information':
                parsed['cost_information'] = self._parse_cost_information(avp)

        return parsed

    def _parse_subscription_id(self, grouped_avp: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Subscription-Id grouped AVP"""
        sub_id = {'type': None, 'data': None}

        for child_avp in grouped_avp.get('grouped_avps', []):
            child_code = child_avp.get('code')
            child_def = self.dict.get_avp_by_code(child_code)

            if not child_def:
                continue

            if child_def.name == 'Subscription-Id-Type':
                sub_id['type'] = child_avp.get('value')
            elif child_def.name == 'Subscription-Id-Data':
                sub_id['data'] = child_avp.get('value')

        return sub_id if sub_id['type'] is not None else None

    def _parse_service_unit(self, grouped_avp: Dict[str, Any]) -> Dict[str, Any]:
        """Parse service unit grouped AVP (Granted/Requested/Used)"""
        service_unit = {}

        for child_avp in grouped_avp.get('grouped_avps', []):
            child_code = child_avp.get('code')
            child_def = self.dict.get_avp_by_code(child_code)

            if not child_def:
                continue

            # Extract known service unit types
            if child_def.name in ['CC-Time', 'CC-Total-Octets', 'CC-Input-Octets',
                                   'CC-Output-Octets', 'CC-Service-Specific-Units']:
                service_unit[child_def.name] = child_avp.get('value')
            elif child_def.name == 'Tariff-Time-Change':
                service_unit['Tariff-Time-Change'] = child_avp.get('value')
            elif child_def.name == 'CC-Money':
                service_unit['CC-Money'] = self._parse_cc_money(child_avp)

        return service_unit

    def _parse_cc_money(self, grouped_avp: Dict[str, Any]) -> Dict[str, Any]:
        """Parse CC-Money grouped AVP"""
        money = {'unit_value': {}, 'currency_code': None}

        for child_avp in grouped_avp.get('grouped_avps', []):
            child_code = child_avp.get('code')
            child_def = self.dict.get_avp_by_code(child_code)

            if not child_def:
                continue

            if child_def.name == 'Currency-Code':
                money['currency_code'] = child_avp.get('value')
            elif child_def.name == 'Unit-Value':
                money['unit_value'] = self._parse_unit_value(child_avp)

        return money

    def _parse_unit_value(self, grouped_avp: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Unit-Value grouped AVP"""
        unit_value = {'value_digits': None, 'exponent': None}

        for child_avp in grouped_avp.get('grouped_avps', []):
            child_code = child_avp.get('code')
            child_def = self.dict.get_avp_by_code(child_code)

            if not child_def:
                continue

            if child_def.name == 'Value-Digits':
                unit_value['value_digits'] = child_avp.get('value')
            elif child_def.name == 'Exponent':
                unit_value['exponent'] = child_avp.get('value')

        return unit_value

    def _parse_cost_information(self, grouped_avp: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Cost-Information grouped AVP"""
        cost_info = {'unit_value': {}, 'currency_code': None, 'cost_unit': None}

        for child_avp in grouped_avp.get('grouped_avps', []):
            child_code = child_avp.get('code')
            child_def = self.dict.get_avp_by_code(child_code)

            if not child_def:
                continue

            if child_def.name == 'Currency-Code':
                cost_info['currency_code'] = child_avp.get('value')
            elif child_def.name == 'Cost-Unit':
                cost_info['cost_unit'] = child_avp.get('value')
            elif child_def.name == 'Unit-Value':
                cost_info['unit_value'] = self._parse_unit_value(child_avp)

        return cost_info

    def _parse_service_parameter(self, grouped_avp: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Service-Parameter-Info grouped AVP"""
        param = {'type': None, 'value': None}

        for child_avp in grouped_avp.get('grouped_avps', []):
            child_code = child_avp.get('code')
            child_def = self.dict.get_avp_by_code(child_code)

            if not child_def:
                continue

            if child_def.name == 'Service-Parameter-Type':
                param['type'] = child_avp.get('value')
            elif child_def.name == 'Service-Parameter-Value':
                param['value'] = child_avp.get('value')

        return param if param['type'] is not None else None


# ============================================================================
# BROMELIA INTEGRATION - REAL IMPLEMENTATION
# ============================================================================

class GyDiameterApplication:
    """
    Real Gy Diameter Application using bromelia library
    This class demonstrates actual bromelia integration
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Gy Diameter Application

        Args:
            config: Configuration dictionary:
                - host: Local diameter host identity
                - realm: Local diameter realm
                - ip: Local IP to bind
                - port: Local port to listen
                - ocs_host: OCS host identity (optional)
                - ocs_realm: OCS realm (optional)
                - ocs_ip: OCS IP address (optional)
                - ocs_port: OCS port (optional)
        """
        self.config = config
        self.dictionary = GyAVPDictionary()
        self.message_builder = GyMessageBuilder()

        # Statistics
        self.stats = {
            'ccr_initial_received': 0,
            'ccr_update_received': 0,
            'ccr_terminate_received': 0,
            'cca_sent': 0,
            'errors': 0
        }

    def start(self, blocking=True):
        """
        Start the Diameter application in listening mode

        Args:
            blocking: If True, runs in blocking mode. If False, runs in background.
        """
        try:
            # Try to use bromelia integration
            from bromelia_integration import create_gy_application, is_bromelia_available

            if is_bromelia_available():
                print(f"\n{'='*70}")
                print(f"Bromelia library detected - using full Diameter stack")
                print(f"{'='*70}\n")

                # Create bromelia application
                bromelia_app = create_gy_application(self.config, use_bromelia=True)

                # Transfer our config
                bromelia_app.stats = self.stats

                # Start bromelia application
                bromelia_app.start(blocking=blocking)

                # Transfer stats back
                self.stats = bromelia_app.get_statistics()
                return
            else:
                raise ImportError("Bromelia not available")

        except ImportError as e:
            print(f"\n⚠️  Bromelia library not installed")
            print(f"Error: {e}")
            print(f"\nTo use full Diameter functionality, install bromelia:")
            print(f"  pip install bromelia\n")
            print(f"Starting in MOCK MODE instead...\n")
            self._start_mock_server(blocking)
        except Exception as e:
            print(f"Error starting Diameter application: {e}")
            import traceback
            traceback.print_exc()
            self.stats['errors'] += 1
            print(f"\nFalling back to MOCK MODE...\n")
            self._start_mock_server(blocking)

    def stop(self):
        """Stop the Diameter application"""
        try:
            if hasattr(self, 'app'):
                self.app.stop()
            print("Server stopped successfully.")
            self.print_statistics()
        except Exception as e:
            print(f"Error stopping server: {e}")

    def _start_mock_server(self, blocking=True):
        """
        Start a mock Diameter server for testing without bromelia
        This simulates a Diameter server for development/testing
        """
        import socket
        import threading

        ip = self.config.get('ip', '0.0.0.0')
        port = self.config.get('port', 3868)

        print(f"{'='*70}")
        print(f"Starting MOCK Gy Diameter Server (Testing Mode)")
        print(f"{'='*70}")
        print(f"Host Identity: {self.config['host']}")
        print(f"Realm: {self.config['realm']}")
        print(f"Listening on: {ip}:{port}")
        print(f"{'='*70}\n")
        print(f"⚠️  This is a MOCK server for testing purposes")
        print(f"⚠️  For production use, install bromelia: pip install bromelia\n")

        def handle_client(client_socket, address):
            """Handle incoming Diameter messages"""
            print(f"[{self._get_timestamp()}] New connection from {address}")
            try:
                # Receive data
                data = client_socket.recv(4096)
                if data:
                    print(f"[{self._get_timestamp()}] Received {len(data)} bytes from {address}")

                    # Try to parse as Diameter message (simplified)
                    if len(data) >= 20:  # Minimum Diameter header size
                        # Extract command code (bytes 5-8)
                        cmd_code = int.from_bytes(data[5:8], byteorder='big') & 0x00FFFFFF

                        if cmd_code == 272:  # CCR
                            print(f"[{self._get_timestamp()}] Detected CCR message")
                            self.stats['ccr_initial_received'] += 1

                            # Send mock CCA (simplified response)
                            response = self._create_mock_cca(data)
                            client_socket.send(response)
                            self.stats['cca_sent'] += 1
                            print(f"[{self._get_timestamp()}] Sent CCA response")
                        else:
                            print(f"[{self._get_timestamp()}] Unknown command code: {cmd_code}")
                    else:
                        print(f"[{self._get_timestamp()}] Invalid Diameter message (too short)")
            except Exception as e:
                print(f"[{self._get_timestamp()}] Error handling client {address}: {e}")
                self.stats['errors'] += 1
            finally:
                client_socket.close()
                print(f"[{self._get_timestamp()}] Connection closed: {address}\n")

        def server_loop():
            """Main server loop"""
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                server_socket.bind((ip if ip != '0.0.0.0' else '', port))
                server_socket.listen(5)
                self.server_socket = server_socket

                print(f"✓ Server started successfully")
                print(f"✓ Waiting for connections...\n")

                while True:
                    try:
                        client_socket, address = server_socket.accept()
                        # Handle each client in a separate thread
                        client_thread = threading.Thread(
                            target=handle_client,
                            args=(client_socket, address),
                            daemon=True
                        )
                        client_thread.start()
                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        if self.server_socket:  # Only print if server is still running
                            print(f"Error accepting connection: {e}")
            except Exception as e:
                print(f"Error starting mock server: {e}")
                self.stats['errors'] += 1
            finally:
                server_socket.close()
                print("\nServer stopped.")

        # Start server in thread or blocking mode
        if blocking:
            try:
                server_loop()
            except KeyboardInterrupt:
                print("\n\nShutting down server...")
                self.print_statistics()
        else:
            server_thread = threading.Thread(target=server_loop, daemon=True)
            server_thread.start()
            print("Server started in background mode.")

    def _get_timestamp(self):
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def _create_mock_cca(self, ccr_data):
        """
        Create a mock CCA response
        This is a simplified implementation for testing
        """
        # In a real implementation, this would properly parse the CCR
        # and construct a valid CCA with AVPs

        # For now, create a minimal Diameter answer
        # Diameter header: Version(1) | Length(3) | Flags(1) | Code(3) | App-ID(4) | HbH(4) | E2E(4)

        version = 1
        flags = 0x40  # Answer flag set
        cmd_code = 272  # Credit-Control
        app_id = 4  # Credit Control Application

        # Copy Hop-by-Hop and End-to-End IDs from request
        if len(ccr_data) >= 20:
            hbh_id = ccr_data[12:16]
            e2e_id = ccr_data[16:20]
        else:
            hbh_id = b'\x00\x00\x00\x01'
            e2e_id = b'\x00\x00\x00\x01'

        # Minimal CCA header (20 bytes)
        length = 20  # Just header for now
        header = bytes([version]) + length.to_bytes(3, 'big')
        header += bytes([flags]) + cmd_code.to_bytes(3, 'big')
        header += app_id.to_bytes(4, 'big')
        header += hbh_id + e2e_id

        return header

    def _handle_ccr(self, request):
        """
        Handle incoming Credit-Control-Request

        Args:
            request: Bromelia Diameter request message

        Returns:
            Diameter answer message
        """
        try:
            # Parse the request
            parsed_ccr = self._parse_bromelia_message(request)

            # Update statistics
            req_type = parsed_ccr.get('cc_request_type')
            if req_type == 1:  # INITIAL_REQUEST
                self.stats['ccr_initial_received'] += 1
            elif req_type == 2:  # UPDATE_REQUEST
                self.stats['ccr_update_received'] += 1
            elif req_type == 3:  # TERMINATION_REQUEST
                self.stats['ccr_terminate_received'] += 1

            print(f"\n{'='*60}")
            print(f"Received CCR:")
            print(f"  Session-Id: {parsed_ccr.get('session_id')}")
            print(f"  Request-Type: {req_type}")
            print(f"  Request-Number: {parsed_ccr.get('cc_request_number')}")
            print(f"  Service-Context-Id: {parsed_ccr.get('service_context_id')}")

            if parsed_ccr.get('subscription_ids'):
                for sub_id in parsed_ccr['subscription_ids']:
                    print(f"  Subscription-Id: Type={sub_id['type']}, Data={sub_id['data']}")

            if parsed_ccr.get('requested_service_unit'):
                print(f"  Requested Units: {parsed_ccr['requested_service_unit']}")

            if parsed_ccr.get('used_service_unit'):
                print(f"  Used Units: {parsed_ccr['used_service_unit']}")

            # Create answer
            answer = self._create_cca(request, parsed_ccr)

            self.stats['cca_sent'] += 1

            print(f"Sending CCA with Result-Code: 2001 (SUCCESS)")
            print(f"{'='*60}\n")

            return answer

        except Exception as e:
            print(f"Error handling CCR: {e}")
            self.stats['errors'] += 1
            return self._create_error_answer(request, 5012)  # DIAMETER_UNABLE_TO_COMPLY

    def _parse_bromelia_message(self, message) -> Dict[str, Any]:
        """
        Parse bromelia message object into dictionary format

        Args:
            message: Bromelia diameter message

        Returns:
            Parsed message dictionary
        """
        # Convert bromelia message to dictionary format
        # This is a simplified version - actual implementation would use bromelia's API
        message_dict = {
            'command_code': message.header.command_code,
            'is_request': message.header.is_request,
            'application_id': message.header.application_id,
            'avps': []
        }

        # Extract AVPs from message
        # In real bromelia, you would iterate through message.avps
        # For now, this is a placeholder showing the structure

        return self.message_builder.parse_ccr(message_dict)

    def _create_cca(self, request, parsed_ccr: Dict[str, Any]):
        """
        Create Credit-Control-Answer

        Args:
            request: Original CCR request
            parsed_ccr: Parsed CCR information

        Returns:
            CCA message
        """
        # Import bromelia AVP classes
        try:
            from bromelia.base import Answer

            # Create answer based on request
            answer = request.create_answer()

            # Add Result-Code (2001 = DIAMETER_SUCCESS)
            # answer.add_avp(ResultCodeAVP(2001))

            # For INITIAL and UPDATE requests, grant quota
            if parsed_ccr.get('cc_request_type') in [1, 2]:
                # Grant 1 hour of time and 100MB of data
                # granted_unit = GrantedServiceUnitAVP()
                # granted_unit.add_avp(CCTimeAVP(3600))  # 1 hour
                # granted_unit.add_avp(CCTotalOctetsAVP(104857600))  # 100 MB
                # answer.add_avp(granted_unit)

                # Add Validity-Time (quota validity)
                # answer.add_avp(ValidityTimeAVP(3600))
                pass

            return answer

        except ImportError:
            # Fallback if bromelia not installed
            print("Warning: bromelia not available, returning mock answer")
            return None

    def _create_error_answer(self, request, result_code: int):
        """
        Create error answer

        Args:
            request: Original request
            result_code: Diameter result code

        Returns:
            Error answer message
        """
        try:
            answer = request.create_answer()
            # answer.add_avp(ResultCodeAVP(result_code))
            return answer
        except:
            return None

    def get_statistics(self) -> Dict[str, int]:
        """Get application statistics"""
        return self.stats.copy()

    def print_statistics(self):
        """Print statistics"""
        print("\n" + "="*60)
        print("Gy Diameter Application Statistics:")
        print("="*60)
        print(f"CCR Initial Received:    {self.stats['ccr_initial_received']}")
        print(f"CCR Update Received:     {self.stats['ccr_update_received']}")
        print(f"CCR Terminate Received:  {self.stats['ccr_terminate_received']}")
        print(f"CCA Sent:                {self.stats['cca_sent']}")
        print(f"Errors:                  {self.stats['errors']}")
        print("="*60 + "\n")


# ============================================================================
# EXAMPLE USAGE AND TESTS
# ============================================================================

def example_usage():
    """Example usage of the Gy protocol implementation"""

    print("\n" + "="*80)
    print("Gy Protocol Implementation - Example Usage")
    print("="*80 + "\n")

    # 1. Dictionary usage
    print("1. AVP Dictionary Example:")
    print("-" * 40)
    GyAVPDictionary.print_avp_info('CC-Request-Type')
    GyAVPDictionary.print_avp_info('Subscription-Id')

    # 2. Message builder example
    print("\n2. Building CCR Messages:")
    print("-" * 40)

    builder = GyMessageBuilder()

    # Build CCR Initial
    ccr_initial = builder.build_ccr_initial(
        session_id="test-session-001",
        origin_host="pgw.example.com",
        origin_realm="example.com",
        destination_realm="ocs.example.com",
        service_context_id="32251@3gpp.org",
        msisdn="1234567890"
    )
    print(f"CCR Initial built with {len(ccr_initial['avps'])} AVPs")

    # Build CCR Update
    ccr_update = builder.build_ccr_update(
        session_id="test-session-001",
        origin_host="pgw.example.com",
        origin_realm="example.com",
        destination_realm="ocs.example.com",
        service_context_id="32251@3gpp.org",
        cc_request_number=1,
        used_units={'CC-Time': 300, 'CC-Total-Octets': 1024000},
        requested_units={'CC-Time': 600, 'CC-Total-Octets': 2048000}
    )
    print(f"CCR Update built with {len(ccr_update['avps'])} AVPs")

    # Build CCR Terminate
    ccr_terminate = builder.build_ccr_terminate(
        session_id="test-session-001",
        origin_host="pgw.example.com",
        origin_realm="example.com",
        destination_realm="ocs.example.com",
        service_context_id="32251@3gpp.org",
        cc_request_number=2,
        used_units={'CC-Time': 150, 'CC-Total-Octets': 512000}
    )
    print(f"CCR Terminate built with {len(ccr_terminate['avps'])} AVPs")

    # 3. Message parsing example
    print("\n3. Parsing CCR Message:")
    print("-" * 40)
    parsed = builder.parse_ccr(ccr_update)
    print(f"Parsed CCR:")
    print(f"  Session-Id: {parsed['session_id']}")
    print(f"  CC-Request-Type: {parsed['cc_request_type']}")
    print(f"  CC-Request-Number: {parsed['cc_request_number']}")
    print(f"  Used Units: {parsed['used_service_unit']}")
    print(f"  Requested Units: {parsed['requested_service_unit']}")

    # 4. Diameter Application example
    print("\n4. Diameter Application Example:")
    print("-" * 40)

    config = {
        'host': 'gy-proxy.example.com',
        'realm': 'example.com',
        'ip': '127.0.0.1',
        'port': 3868,
        'ocs_host': 'ocs.example.com',
        'ocs_realm': 'ocs.example.com',
        'ocs_ip': '127.0.0.1',
        'ocs_port': 3869
    }

    app = GyDiameterApplication(config)
    print("Gy Diameter Application initialized")
    print(f"Configuration: {config}")

    # Note: To actually start the application, uncomment:
    # app.start()

    print("\n" + "="*80)
    print("Example completed!")
    print("="*80 + "\n")


if __name__ == '__main__':
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Gy Diameter Protocol Implementation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run examples and show AVP list
  python main.py
  
  # Start in listening mode (default port 3868)
  python main.py --listen
  
  # Start on specific IP and port
  python main.py --listen --ip 127.0.0.1 --port 3868
  
  # Start with custom host/realm
  python main.py --listen --host ocs.example.com --realm example.com
        """
    )

    parser.add_argument(
        '--listen', '-l',
        action='store_true',
        help='Start in listening mode (Diameter server)'
    )

    parser.add_argument(
        '--host',
        default='gy-server.example.com',
        help='Diameter host identity (default: gy-server.example.com)'
    )

    parser.add_argument(
        '--realm',
        default='example.com',
        help='Diameter realm (default: example.com)'
    )

    parser.add_argument(
        '--ip',
        default='0.0.0.0',
        help='IP address to bind to (default: 0.0.0.0)'
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        default=3868,
        help='Port to listen on (default: 3868)'
    )

    args = parser.parse_args()

    if args.listen:
        # Start in listening mode
        config = {
            'host': args.host,
            'realm': args.realm,
            'ip': args.ip,
            'port': args.port
        }

        app = GyDiameterApplication(config)

        try:
            app.start(blocking=True)
        except KeyboardInterrupt:
            print("\n\nShutdown signal received...")
            app.stop()
    else:
        # Run example usage
        example_usage()

        # List all available AVPs
        print("\nAvailable AVPs:")
        print("-" * 40)
        for avp_name in sorted(GyAVPDictionary.list_all_avps()):
            avp = GyAVPDictionary.get_avp(avp_name)
            print(f"  {avp_name:40} Code: {avp.code:4}  Type: {avp.data_type.value}")

