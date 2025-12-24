"""Test to see what happens when connecting"""
import socket
import struct
import time

# Open a raw connection and try to do a Diameter handshake
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)

try:
    print("Connecting to 16.0.0.30:3875...")
    sock.connect(('16.0.0.30', 3875))
    print("Connected! Waiting for data...")

    # Wait to see if the server sends anything first
    sock.settimeout(5)
    try:
        data = sock.recv(4096)
        if data:
            print(f"Received {len(data)} bytes from server:")
            print(f"  First 20 bytes (hex): {data[:20].hex()}")
            # Check if it's a Diameter message (starts with version 1)
            if len(data) >= 4:
                version = data[0]
                length = struct.unpack('!I', b'\x00' + data[1:4])[0]
                print(f"  Diameter version: {version}, message length: {length}")
        else:
            print("Server closed connection without sending data")
    except socket.timeout:
        print("No data received from server (timeout)")
        print("Server expects client to send CER first")

    print("\nConnection is still open. Closing...")
    sock.close()
    print("Closed successfully")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

