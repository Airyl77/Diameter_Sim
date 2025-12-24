"""
A sample of a node acting as a client that does nothing.

Starting this script, and then starting the `idle_server.py` script, located
in the same directory, will result in the two nodes exchanging CER/CEA and then
idling forever, with occasional Device-Watchdog messages being sent back and
forth.
"""
import logging
import time
import datetime

from diameter.message.commands.credit_control import CreditControlRequest
from diameter.message.commands.credit_control import RequestedServiceUnit
from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import SmsInformation
from diameter.message.commands.credit_control import RecipientInfo
from diameter.message.commands.credit_control import RecipientAddress
from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication


logging.basicConfig(format="%(asctime)s %(name)-30s %(levelname)-7s %(message)s",
                    level=logging.DEBUG)

# this shows a human-readable message dump in the logs
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)
# Also enable connection-level debugging
logging.getLogger("diameter.peer").setLevel(logging.DEBUG)
# Enable all diameter loggers
logging.getLogger("diameter").setLevel(logging.DEBUG)


# Configure our server node
node = Node("relay2.test.realm", "mobistar.be",
            ip_addresses=["16.0.0.1"],
            vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2, VENDOR_NONE])
# Sets a higher Device-Watchdog trigger than the server, so that the nodes will
# not send DWRs simultaneously
node.idle_timeout = 30

# Adding the other idler as a peer, but not configuring it as persistent. The
# connectivity will only be established by the other peer.
peer = node.add_peer("aaa://VOICE-OBE.drfbor1.ipbb.prod.be:3875", is_persistent=True,
                     ip_addresses=["16.0.0.30"], realm_name="ipbb.prod.be")


# Constructing a Credit Control application client. Credit Control can be either
# an authentication or accounting application depending on the peer's implementation.
# This peer advertises it as Auth-Application-Id.
client = SimpleThreadingApplication(APP_DIAMETER_CREDIT_CONTROL_APPLICATION, is_auth_application=True)
node.add_application(client, [peer])


# Start the node and idle until interrupted with CTRL+C
node.start()

# Send DWR first (this was working before)
print("Sending DWR to establish connection...")
for conn in node.connections.values():
    print(f"Sending DWR to: {conn}")
    node.send_dwr(conn)

# Wait for the connection to be ready before sending CCR
print("Waiting for connection to be ready...")
client.wait_for_ready()
print("Connection ready!")

for conn in node.connections.values():
    print(f"Connected to: {conn}")

# Construct a credit control request
ccr = CreditControlRequest()

# These are required:
ccr.session_id = client.node.session_generator.next_id()
ccr.origin_host = client.node.origin_host.encode()
ccr.origin_realm = client.node.realm_name.encode()
ccr.destination_realm = b"ipbb.prod.be"  # Must match peer's realm
ccr.destination_host = b"VOICE-OBE.drfbor1.ipbb.prod.be"  # Specify the exact peer
ccr.auth_application_id = client.application_id
ccr.service_context_id = "32274@3gpp.org"
ccr.cc_request_type = E_CC_REQUEST_TYPE_INITIAL_REQUEST
ccr.cc_request_number = 1
ccr.origin_state_id = client.node.state_id  # Add Origin-State-Id

# These are usually wanted by charging servers:
ccr.user_name = "diameter"
ccr.event_timestamp = datetime.datetime.now()
ccr.requested_action = E_REQUESTED_ACTION_DIRECT_DEBITING

ccr.add_subscription_id(
    subscription_id_type=E_SUBSCRIPTION_ID_TYPE_END_USER_E164,
    subscription_id_data="41780000001")
ccr.add_multiple_services_credit_control(
    requested_service_unit=RequestedServiceUnit(cc_service_specific_units=1),
    service_identifier=1)

# Adds the following 3GPP vendor-specific AVP structure at the end, which
# contains the SMS type and recipient. Looks like:
#
#   Service-Information <Code: 0x369, Flags: 0xc0 (VM-), Length: 120, Vnd: TGPP>
#     SMS-Information <Code: 0x7d0, Flags: 0x80 (V--), Length: 108, Vnd: TGPP>
#       Data-Coding-Scheme <Code: 0x7d1, Flags: 0x80 (V--), Length: 16, Vnd: TGPP, Val: 8>
#       SM-Message-Type <Code: 0x7d7, Flags: 0x80 (V--), Length: 16, Vnd: TGPP, Val: 0>
#       Recipient-Info <Code: 0x7ea, Flags: 0x80 (V--), Length: 64, Vnd: TGPP>
#         Recipient-Address <Code: 0x4b1, Flags: 0x80 (V--), Length: 52, Vnd: TGPP>
#           Address-Type <Code: 0x383, Flags: 0xc0 (VM-), Length: 16, Vnd: TGPP, Val: 1>
#           Address-Data <Code: 0x381, Flags: 0xc0 (VM-), Length: 23, Vnd: TGPP, Val: 41780000001>
#
# Actual content wanted by the OCS on the receiving end may vary depending on
# the vendor and their implementation.
#
# Note that `RecipientInfo` and `RecipientAddress` are wrapped in lists, as the
# specification allows more than one recipient.
ccr.service_information = ServiceInformation(
    sms_information=SmsInformation(
        data_coding_scheme=8,
        sm_message_type=E_SM_MESSAGE_TYPE_SUBMISSION,
        recipient_info=[RecipientInfo(
            recipient_address=[RecipientAddress(
                address_type=E_ADDRESS_TYPE_MSISDN,
                address_data="41780000002"
            )]
        )]
    )
)


# Send the CCR and wait for CCA response
print("Sending Credit Control Request...")
cca = client.send_request(ccr, timeout=10)

# Should print 2001, if all goes well. 5005 means missing AVPs.
print(f"Result Code: {cca.result_code}")
node.stop()

#
# try:
#     while True:
#         time.sleep(1)
#
# except (KeyboardInterrupt, SystemExit) as e:
#     node.stop()