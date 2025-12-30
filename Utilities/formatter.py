from mailbox import Message

from diameter.message import Avp, AvpGrouped, Message
from diameter.message.avp import AvpUtf8String, avp
from typing import Dict, Any, List

from diameter.message.avp.grouped import ServiceInformation


def format_avp_value(avp_name: str, value: Any) -> str:
    """Format AVP value based on type."""
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return f"0x{value.hex()}"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, list):
        return str(value)
    else:
        return str(value)


def parse_grouped_avp(avp_value: List, indent: int = 2) -> List[str]:
    """Parse grouped AVP recursively."""
    lines = []
    indent_str = " " * indent

    for sub_avp in avp_value:
        avp_name = sub_avp.avp_def.name if hasattr(sub_avp, 'avp_def') else "Unknown"

        if hasattr(sub_avp, 'value') and isinstance(sub_avp.value, list):
            # Grouped AVP
            lines.append(f"{indent_str}{avp_name}:")
            lines.extend(parse_grouped_avp(sub_avp.value, indent + 2))
        else:
            # Simple AVP
            value_str = format_avp_value(avp_name, sub_avp.value if hasattr(sub_avp, 'value') else sub_avp)
            lines.append(f"{indent_str}{avp_name}: {value_str}")

    return lines


def parse_ccr(ccr: Message) -> str:
    """
    Parse CCR message and return formatted structure.

    Args:
        ccr: Credit-Control-Request message object

    Returns:
        Formatted string showing CCR structure
    """
    output_lines = ["Current CCR Structure Being Sent:"]
    output_lines.append("")

    # Map common CCR AVPs to their display order
    avp_order = [
        "Session-Id",
        "Origin-Host",
        "Origin-Realm",
        "Destination-Realm",
        "Destination-Host",
        "Auth-Application-Id",
        "Service-Context-Id",
        "CC-Request-Type",
        "CC-Request-Number",
        "Origin-State-Id",
        "User-Name",
        "Event-Timestamp",
        "Requested-Action",
        "Subscription-Id",
        "Multiple-Services-Credit-Control",
        "Service-Information",
    ]

    # Create a dict of AVPs by name for easy lookup
    avp_dict: Dict[str, Any] = {}

    for avp in ccr.avps:
        avp_name = avp.avp_def.name if hasattr(avp, 'avp_def') else f"AVP-{avp.code}"

        if avp_name in avp_dict:
            # Handle multiple AVPs with same name (convert to list)
            if not isinstance(avp_dict[avp_name], list):
                avp_dict[avp_name] = [avp_dict[avp_name]]
            avp_dict[avp_name].append(avp)
        else:
            avp_dict[avp_name] = avp

    # Process AVPs in order
    for avp_name in avp_order:
        if avp_name not in avp_dict:
            continue

        avp_value = avp_dict[avp_name]

        # Handle multiple instances
        if isinstance(avp_value, list):
            for avp in avp_value:
                output_lines.extend(_format_single_avp(avp_name, avp))
        else:
            output_lines.extend(_format_single_avp(avp_name, avp_value))

    # Add any remaining AVPs not in the order list
    for avp_name, avp_value in avp_dict.items():
        if avp_name not in avp_order:
            if isinstance(avp_value, list):
                for avp in avp_value:
                    output_lines.extend(_format_single_avp(avp_name, avp))
            else:
                output_lines.extend(_format_single_avp(avp_name, avp_value))

    return "\n".join(output_lines)


def _format_single_avp(avp_name: str, avp) -> List[str]:
    """Format a single AVP with proper indentation."""
    lines = []

    # Check if it's a grouped AVP
    if hasattr(avp, 'value') and isinstance(avp.value, list):
        lines.append(f"{avp_name}:")
        lines.extend(parse_grouped_avp(avp.value))
    else:
        # Simple AVP with description
        value = avp.value if hasattr(avp, 'value') else avp
        formatted_value = format_avp_value(avp_name, value)

        # Add descriptions for known values
        description = _get_avp_description(avp_name, value)
        if description:
            lines.append(f"{avp_name}: {formatted_value} ({description})")
        else:
            lines.append(f"{avp_name}: {formatted_value}")

    return lines


def _get_avp_description(avp_name: str, value: Any) -> str:
    """Get human-readable description for known AVP values."""
    descriptions = {
        "CC-Request-Type": {
            1: "INITIAL_REQUEST",
            2: "UPDATE_REQUEST",
            3: "TERMINATION_REQUEST",
            4: "EVENT_REQUEST"
        },
        "Requested-Action": {
            0: "DIRECT_DEBITING",
            1: "REFUND_ACCOUNT",
            2: "CHECK_BALANCE",
            3: "PRICE_ENQUIRY"
        },
        "Subscription-Id-Type": {
            0: "END_USER_E164",
            1: "END_USER_IMSI",
            2: "END_USER_SIP_URI",
            3: "END_USER_NAI"
        },
        "Address-Type": {
            0: "IPv4",
            1: "MSISDN",
            2: "IPv6"
        },
        "SM-Message-Type": {
            0: "SUBMISSION",
            1: "DELIVERY_REPORT"
        }
    }

    if avp_name in descriptions and isinstance(value, int):
        return descriptions[avp_name].get(value, "")

    return ""


# Example usage
if __name__ == "__main__":
    from diameter.message.commands import CreditControlRequest
    from diameter.node.application import SimpleThreadingApplication
    from diameter.message.constants import *

    # Your existing code to create CCR
    APP_DIAMETER_CREDIT_CONTROL_APPLICATION = 4
    client = SimpleThreadingApplication(
        APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
        is_auth_application=True
    )

    # Create CCR (your existing code)
    a = bytes.fromhex("0100028cc00001100000000400c08b674553737a000001074000004b6d756c2d7268696e6f322d70726f642e7268696e6"
                      "f2e6f73673b6469616d65746572726f2d6f63732d6f73672d6f6c753b313830393237373634303b3336363130323500000"
                      "00108400000216d756c2d7268696e6f322d70726f642e7268696e6f2e6f736700000000000128400000156f73672e6f7261"
                      "6e67652e62650000000000011b40000014697062622e70726f642e6265000001024000000c00000004000001cd40000027534"
                      "3502d4e42492e3230362e31302e53324633406d6f6269737461722e626500000001a04000000c000000010000019f4000000c0"
                      "0000000000000374000000cecd812e7000001bb40000028000001c24000000c00000000000001bc400000143335323636313833"
                      "32333530000001c74000000c00000001000001c840000028000001be40000014000001a44000000c00000000000001b04000000c0"
                      "000025800000369c0000128000028af00000385c000011c0000055800000386c00000100000055800000004000003afc000001"
                      "00000055800000001000003968000000d0000055811000000000003978000001300000558000040500a590d000000038780000"
                      "010000005580000000a00000388c00000180000055833353236363138333233353000000389c00000100000055800000004000"
                      "0038ec0000018000005583335323639313236373837300000038fc000001000000558000000040000038cc00000180000055833"
                      "353230363130303038343000000398c0000018000005583335323036313030303834300000038ac0000018000005583335323036"
                      "313030303834300000039ac000001000000558ecd812e70000039980000014000005580252211041311140")
    ccr = CreditControlRequest()
    avp.register(avp=908,
                 name="Calling-LAI",
                 type_cls=AvpUtf8String,
                 vendor=VENDOR_FRANCETELECOM)

    # ccr.append_avp(avp908)
    # ccr.service_information = ServiceInformation()

    print(avp.VENDORS)

    ccr = Message.from_bytes(a)
    print(type(ccr))
    assert isinstance(ccr, CreditControlRequest)
    print(ccr.session_id)
    print(ccr.service_information)



    # assert isinstance(ccr, CreditControlRequest)
    # ... rest of your CCR setup ...

    # Parse and print
    print(parse_ccr(ccr))
    # print(ccr.session_id)

