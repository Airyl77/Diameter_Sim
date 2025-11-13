"""
Quick test to verify all components are working
"""

from main import (
    GyAVPDictionary,
    GyMessageBuilder,
    GyMessages,
    GyDiameterApplication,
    GyProxyWithBromelia
)

def test_all_components():
    print("="*60)
    print("TESTING ALL COMPONENTS")
    print("="*60)

    # Test 1: AVP Dictionary
    print("\n1. Testing AVP Dictionary...")
    avp_count = len(GyAVPDictionary.list_all_avps())
    assert avp_count > 40, f"Expected 40+ AVPs, got {avp_count}"

    avp = GyAVPDictionary.get_avp('CC-Request-Type')
    assert avp is not None, "CC-Request-Type not found"
    assert avp.code == 416, f"Wrong code for CC-Request-Type: {avp.code}"

    initial_value = GyAVPDictionary.get_enum_value('CC-Request-Type', 'INITIAL_REQUEST')
    assert initial_value == 1, f"Wrong value for INITIAL_REQUEST: {initial_value}"

    print(f"   ✓ {avp_count} AVPs loaded")
    print(f"   ✓ CC-Request-Type found (code: {avp.code})")
    print(f"   ✓ Enumerated values working")

    # Test 2: Message Builder - Initial
    print("\n2. Testing CCR Initial Builder...")
    builder = GyMessageBuilder()

    ccr_initial = builder.build_ccr_initial(
        session_id="test-session-001",
        origin_host="test.host",
        origin_realm="test.realm",
        destination_realm="dest.realm",
        service_context_id="32251@3gpp.org",
        msisdn="1234567890"
    )

    assert ccr_initial['command_code'] == 272, "Wrong command code"
    assert ccr_initial['is_request'] == True, "Should be request"
    assert ccr_initial['application_id'] == 4, "Wrong application ID"
    assert len(ccr_initial['avps']) >= 7, "Missing AVPs"

    print(f"   ✓ CCR Initial built with {len(ccr_initial['avps'])} AVPs")

    # Test 3: Message Builder - Update
    print("\n3. Testing CCR Update Builder...")
    ccr_update = builder.build_ccr_update(
        session_id="test-session-001",
        origin_host="test.host",
        origin_realm="test.realm",
        destination_realm="dest.realm",
        service_context_id="32251@3gpp.org",
        cc_request_number=1,
        used_units={'CC-Time': 300, 'CC-Total-Octets': 1024000},
        requested_units={'CC-Time': 600}
    )

    assert len(ccr_update['avps']) >= 8, "Missing AVPs in update"
    print(f"   ✓ CCR Update built with {len(ccr_update['avps'])} AVPs")

    # Test 4: Message Builder - Terminate
    print("\n4. Testing CCR Terminate Builder...")
    ccr_terminate = builder.build_ccr_terminate(
        session_id="test-session-001",
        origin_host="test.host",
        origin_realm="test.realm",
        destination_realm="dest.realm",
        service_context_id="32251@3gpp.org",
        cc_request_number=2,
        used_units={'CC-Time': 150}
    )

    assert len(ccr_terminate['avps']) >= 7, "Missing AVPs in terminate"
    print(f"   ✓ CCR Terminate built with {len(ccr_terminate['avps'])} AVPs")

    # Test 5: CCR Parsing
    print("\n5. Testing CCR Parser...")
    parsed = builder.parse_ccr(ccr_update)

    assert parsed['message_type'] == 'CCR', "Wrong message type"
    assert parsed['cc_request_type'] == 2, "Wrong request type (should be UPDATE)"
    assert parsed['cc_request_number'] == 1, "Wrong request number"
    assert 'CC-Time' in parsed['used_service_unit'], "Missing used time"
    assert parsed['used_service_unit']['CC-Time'] == 300, "Wrong used time value"

    print(f"   ✓ Parsed session: {parsed['session_id']}")
    print(f"   ✓ Request type: {parsed['cc_request_type']} (UPDATE)")
    print(f"   ✓ Used units extracted: {parsed['used_service_unit']}")
    print(f"   ✓ Requested units extracted: {parsed['requested_service_unit']}")

    # Test 6: Grouped AVP Parsing
    print("\n6. Testing Grouped AVP Parsing...")
    # The subscription_id should be in the initial request
    parsed_initial = builder.parse_ccr(ccr_initial)
    assert len(parsed_initial['subscription_ids']) > 0, "No subscription IDs found"

    sub_id = parsed_initial['subscription_ids'][0]
    assert sub_id['type'] == 0, "Wrong subscription type"
    assert sub_id['data'] == "1234567890", "Wrong MSISDN"

    print(f"   ✓ Subscription-Id parsed: Type={sub_id['type']}, Data={sub_id['data']}")

    # Test 7: Message Definitions
    print("\n7. Testing Message Definitions...")
    ccr_def = GyMessages.get_ccr_definition()
    cca_def = GyMessages.get_cca_definition()

    assert ccr_def.command_code == 272, "Wrong CCR command code"
    assert cca_def.command_code == 272, "Wrong CCA command code"
    assert ccr_def.is_request == True, "CCR should be request"
    assert cca_def.is_request == False, "CCA should be answer"

    print(f"   ✓ CCR definition: {len(ccr_def.mandatory_avps)} mandatory AVPs")
    print(f"   ✓ CCA definition: {len(cca_def.mandatory_avps)} mandatory AVPs")

    # Test 8: Application Classes
    print("\n8. Testing Application Classes...")
    config = {
        'host': 'test.host',
        'realm': 'test.realm',
        'ip': '127.0.0.1',
        'port': 3868
    }

    app = GyDiameterApplication(config)
    assert app.config == config, "Config not stored"
    assert app.stats['ccr_initial_received'] == 0, "Stats should start at 0"

    proxy = GyProxyWithBromelia(config)
    assert proxy.config == config, "Proxy config not stored"

    print(f"   ✓ GyDiameterApplication initialized")
    print(f"   ✓ GyProxyWithBromelia initialized")

    # Test 9: All AVP Types
    print("\n9. Testing Different AVP Types...")
    test_avps = {
        'CC-Time': 'Unsigned32',
        'CC-Total-Octets': 'Unsigned64',
        'Exponent': 'Integer32',
        'Value-Digits': 'Integer64',
        'Service-Context-Id': 'UTF8String',
        'CC-Correlation-Id': 'OctetString',
        'Tariff-Time-Change': 'Time',
        'CC-Request-Type': 'Enumerated',
        'Subscription-Id': 'Grouped'
    }

    for avp_name, expected_type in test_avps.items():
        avp = GyAVPDictionary.get_avp(avp_name)
        assert avp is not None, f"{avp_name} not found"
        assert avp.data_type.value == expected_type, \
            f"{avp_name} should be {expected_type}, got {avp.data_type.value}"

    print(f"   ✓ All {len(test_avps)} AVP types verified")

    # Summary
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60)
    print(f"\nImplementation Summary:")
    print(f"  - {avp_count} AVPs defined")
    print(f"  - 3 message builders (Initial, Update, Terminate)")
    print(f"  - 2 message parsers (CCR, CCA)")
    print(f"  - 2 application classes (Application, Proxy)")
    print(f"  - Full bromelia integration ready")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    try:
        test_all_components()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        raise

