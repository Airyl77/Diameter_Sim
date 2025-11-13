"""
Example: Building and Parsing Gy Messages
Demonstrates practical usage of the Gy protocol implementation
"""

from main import GyMessageBuilder, GyAVPDictionary

def simulate_mobile_session():
    """Simulate a complete mobile data session with Gy protocol"""

    builder = GyMessageBuilder()
    session_id = "pgw.mnc001.mcc234.3gppnetwork.org;1732901234;67890"
    msisdn = "+447700900123"

    print("="*80)
    print("SIMULATING MOBILE DATA SESSION")
    print("="*80)
    print(f"\nMSISDN: {msisdn}")
    print(f"Session-Id: {session_id}\n")

    # ========================================================================
    # 1. User starts browsing - Send CCR Initial
    # ========================================================================
    print("\n" + "-"*80)
    print("1. USER STARTS DATA SESSION - CCR INITIAL")
    print("-"*80)

    ccr_initial = builder.build_ccr_initial(
        session_id=session_id,
        origin_host="pgw.mnc001.mcc234.3gppnetwork.org",
        origin_realm="mnc001.mcc234.3gppnetwork.org",
        destination_realm="ocs.example.com",
        service_context_id="32251@3gpp.org",
        msisdn=msisdn
    )

    parsed = builder.parse_ccr(ccr_initial)
    print(f"CCR Initial sent:")
    print(f"  Request Type: {parsed['cc_request_type']} (INITIAL_REQUEST)")
    print(f"  Request Number: {parsed['cc_request_number']}")
    print(f"  Subscription IDs: {len(parsed['subscription_ids'])} provided")

    # Simulate CCA response
    print(f"\nCCA Initial received:")
    print(f"  Result-Code: 2001 (DIAMETER_SUCCESS)")
    print(f"  Granted Quota: 1 hour / 100 MB")
    print(f"  Validity-Time: 3600 seconds")

    # ========================================================================
    # 2. After 5 minutes and 50 MB - Send CCR Update
    # ========================================================================
    print("\n" + "-"*80)
    print("2. QUOTA THRESHOLD REACHED - CCR UPDATE")
    print("-"*80)

    ccr_update_1 = builder.build_ccr_update(
        session_id=session_id,
        origin_host="pgw.mnc001.mcc234.3gppnetwork.org",
        origin_realm="mnc001.mcc234.3gppnetwork.org",
        destination_realm="ocs.example.com",
        service_context_id="32251@3gpp.org",
        cc_request_number=1,
        used_units={
            'CC-Time': 300,           # 5 minutes
            'CC-Total-Octets': 52428800  # 50 MB
        },
        requested_units={
            'CC-Time': 3600,          # 1 hour
            'CC-Total-Octets': 104857600  # 100 MB
        }
    )

    parsed = builder.parse_ccr(ccr_update_1)
    print(f"CCR Update sent:")
    print(f"  Request Type: {parsed['cc_request_type']} (UPDATE_REQUEST)")
    print(f"  Request Number: {parsed['cc_request_number']}")
    print(f"  Used Time: {parsed['used_service_unit'].get('CC-Time', 0)} seconds")
    print(f"  Used Data: {parsed['used_service_unit'].get('CC-Total-Octets', 0) / 1024 / 1024:.1f} MB")
    print(f"  Requested Time: {parsed['requested_service_unit'].get('CC-Time', 0)} seconds")
    print(f"  Requested Data: {parsed['requested_service_unit'].get('CC-Total-Octets', 0) / 1024 / 1024:.1f} MB")

    print(f"\nCCA Update received:")
    print(f"  Result-Code: 2001 (DIAMETER_SUCCESS)")
    print(f"  Granted Quota: 30 minutes / 50 MB (reduced due to low balance)")
    print(f"  Validity-Time: 1800 seconds")

    # ========================================================================
    # 3. After another 20 minutes and 45 MB - Send CCR Update
    # ========================================================================
    print("\n" + "-"*80)
    print("3. QUOTA THRESHOLD REACHED AGAIN - CCR UPDATE")
    print("-"*80)

    ccr_update_2 = builder.build_ccr_update(
        session_id=session_id,
        origin_host="pgw.mnc001.mcc234.3gppnetwork.org",
        origin_realm="mnc001.mcc234.3gppnetwork.org",
        destination_realm="ocs.example.com",
        service_context_id="32251@3gpp.org",
        cc_request_number=2,
        used_units={
            'CC-Time': 1200,          # 20 minutes
            'CC-Total-Octets': 47185920  # 45 MB
        },
        requested_units={
            'CC-Time': 1800,          # 30 minutes
            'CC-Total-Octets': 52428800  # 50 MB
        }
    )

    parsed = builder.parse_ccr(ccr_update_2)
    print(f"CCR Update sent:")
    print(f"  Request Number: {parsed['cc_request_number']}")
    print(f"  Used Time: {parsed['used_service_unit'].get('CC-Time', 0)} seconds")
    print(f"  Used Data: {parsed['used_service_unit'].get('CC-Total-Octets', 0) / 1024 / 1024:.1f} MB")

    print(f"\nCCA Update received:")
    print(f"  Result-Code: 4012 (DIAMETER_CREDIT_LIMIT_REACHED)")
    print(f"  Final-Unit-Indication: TERMINATE")
    print(f"  Granted Quota: 60 seconds / 5 MB (final quota)")

    # ========================================================================
    # 4. User finishes or quota exhausted - Send CCR Terminate
    # ========================================================================
    print("\n" + "-"*80)
    print("4. SESSION ENDS - CCR TERMINATE")
    print("-"*80)

    ccr_terminate = builder.build_ccr_terminate(
        session_id=session_id,
        origin_host="pgw.mnc001.mcc234.3gppnetwork.org",
        origin_realm="mnc001.mcc234.3gppnetwork.org",
        destination_realm="ocs.example.com",
        service_context_id="32251@3gpp.org",
        cc_request_number=3,
        used_units={
            'CC-Time': 45,            # 45 seconds
            'CC-Total-Octets': 4194304   # 4 MB
        }
    )

    parsed = builder.parse_ccr(ccr_terminate)
    print(f"CCR Terminate sent:")
    print(f"  Request Type: {parsed['cc_request_type']} (TERMINATION_REQUEST)")
    print(f"  Request Number: {parsed['cc_request_number']}")
    print(f"  Used Time: {parsed['used_service_unit'].get('CC-Time', 0)} seconds")
    print(f"  Used Data: {parsed['used_service_unit'].get('CC-Total-Octets', 0) / 1024 / 1024:.1f} MB")

    print(f"\nCCA Terminate received:")
    print(f"  Result-Code: 2001 (DIAMETER_SUCCESS)")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "="*80)
    print("SESSION SUMMARY")
    print("="*80)
    print(f"Total Duration: 25 minutes 45 seconds")
    print(f"Total Data Usage: 99 MB")
    print(f"Number of CCR messages: 4 (1 Initial + 2 Updates + 1 Terminate)")
    print(f"Session Termination Reason: Credit limit reached")
    print("="*80 + "\n")


def demonstrate_avp_parsing():
    """Demonstrate AVP dictionary usage"""

    print("\n" + "="*80)
    print("AVP DICTIONARY DEMONSTRATION")
    print("="*80 + "\n")

    # Show different AVP types
    avp_examples = [
        'CC-Request-Type',      # Enumerated
        'Subscription-Id',      # Grouped
        'CC-Total-Octets',      # Unsigned64
        'Service-Context-Id',   # UTF8String
        'Final-Unit-Action',    # Enumerated
    ]

    for avp_name in avp_examples:
        avp = GyAVPDictionary.get_avp(avp_name)
        print(f"AVP: {avp.name}")
        print(f"  Code: {avp.code}")
        print(f"  Type: {avp.data_type.value}")

        if avp.enumerated_values:
            print(f"  Values:")
            for name, value in avp.enumerated_values.items():
                print(f"    {name} = {value}")

        if avp.grouped_avps:
            print(f"  Contains: {', '.join(avp.grouped_avps)}")

        print()


def show_message_structure():
    """Show the structure of CCR messages"""

    print("\n" + "="*80)
    print("CREDIT-CONTROL-REQUEST MESSAGE STRUCTURE")
    print("="*80 + "\n")

    builder = GyMessageBuilder()

    # Build a complete CCR Update with all fields
    ccr = builder.build_ccr_update(
        session_id="test.session.123",
        origin_host="test.host",
        origin_realm="test.realm",
        destination_realm="dest.realm",
        service_context_id="32251@3gpp.org",
        cc_request_number=1,
        used_units={
            'CC-Time': 300,
            'CC-Total-Octets': 1048576,
            'CC-Input-Octets': 524288,
            'CC-Output-Octets': 524288
        },
        requested_units={
            'CC-Time': 600,
            'CC-Total-Octets': 2097152
        }
    )

    print("Message Components:")
    print(f"  Command Code: {ccr['command_code']}")
    print(f"  Is Request: {ccr['is_request']}")
    print(f"  Application ID: {ccr['application_id']}")
    print(f"  Number of AVPs: {len(ccr['avps'])}")

    print("\nAVP Breakdown:")
    for i, avp in enumerate(ccr['avps'], 1):
        avp_def = builder.dict.get_avp_by_code(avp['code'])
        if avp_def:
            print(f"  {i}. {avp_def.name} (Code: {avp['code']})")
            if 'grouped_avps' in avp:
                print(f"     → Contains {len(avp['grouped_avps'])} sub-AVPs")
    print()


if __name__ == '__main__':
    # Run all demonstrations
    simulate_mobile_session()
    demonstrate_avp_parsing()
    show_message_structure()

    print("\n" + "="*80)
    print("For more information, see README.md or run: python main.py")
    print("="*80 + "\n")

