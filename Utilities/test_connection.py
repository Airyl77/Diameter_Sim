import socket
import time

# Test binding to the local address first
try:
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    test_sock.bind(('16.0.0.1', 6091))
    print(f"Successfully bound to 16.0.0.1:6091")
    test_sock.listen(1)
    test_sock.close()
except Exception as e:
    print(f"Failed to bind to local address: {e}")

# Test connecting to peer
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    print(f"Attempting to connect to 16.0.0.30:3875...")
    sock.connect(('16.0.0.30', 3875))
    print(f"Connected successfully!")

    # Keep the socket open briefly
    time.sleep(2)
    sock.close()
    print("Connection closed")
except Exception as e:
    print(f"Connection failed: {e}")

