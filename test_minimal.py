"""Minimal test to see CER/CEA exchange"""
import logging
import time

from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication

# Enable VERY verbose logging
logging.basicConfig(format="%(asctime)s %(name)-40s %(levelname)-7s %(message)s",
                    level=logging.DEBUG)

# Configure our node
node = Node("relay2.test.realm", "mgt.mobistar.be",
            ip_addresses=["16.0.0.1"],
            tcp_port=6091,
            vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2, VENDOR_NONE])

node.idle_timeout = 30

# Adding peer
peer = node.add_peer("aaa://VOICE-OBE.drfbor1.ipbb.prod.be:3875", is_persistent=True,
                     ip_addresses=["16.0.0.30"], realm_name="ipbb.prod.be")

# Add Credit Control application
client = SimpleThreadingApplication(APP_DIAMETER_CREDIT_CONTROL_APPLICATION, is_acct_application=True)
node.add_application(client, [peer])

# Start the node
print("Starting node...")
node.start()

print("Waiting 10 seconds to see CER/CEA exchange...")
time.sleep(10)

print("\nConnections:")
for conn in node.connections.values():
    print(f"  {conn}")

print("\nPeer connection states:")
for conn in peer.connections:
    print(f"  {conn}: state={conn.state if hasattr(conn, 'state') else 'unknown'}")

print("\nApplication ready state:")
print(f"  Is ready: {client.is_ready()}")

node.stop()

