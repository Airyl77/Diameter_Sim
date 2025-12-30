"""Test to see socket connection error"""
import socket
import select
import errno

# Try to replicate what the diameter library does
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(False)

# Try to bind to a specific local address first
try:
    sock.bind(('16.0.0.1', 0))  # 0 means "any available port"
    print(f"Successfully bound to 16.0.0.1 (local port: {sock.getsockname()[1]})")
except Exception as e:
    print(f"Failed to bind: {e}")

print("Attempting non-blocking connect to 16.0.0.30:3875...")
try:
    sock.connect(('16.0.0.30', 3875))
    print("Connected immediately (unexpected for non-blocking)")
except socket.error as e:
    if e.args[0] == errno.EINPROGRESS or e.args[0] == errno.EWOULDBLOCK or e.args[0] == 10035:  # 10035 is WSAEWOULDBLOCK on Windows
        print(f"Connection in progress (errno {e.args[0]}: {e.args[1]})")
    else:
        print(f"Connection failed immediately with errno {e.args[0]}: {e.args[1]}")
        sock.close()
        exit(1)

# Wait for the socket to become writable (means connection is established or failed)
print("Waiting for socket to become writable...")
_, ready_w, _ = select.select([], [sock], [], 10)

if sock in ready_w:
    # Check for errors using getsockopt like the diameter library does
    socket_error = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
    if socket_error == 0:
        print(f"✓ Connection successful! (SO_ERROR = 0)")
        print(f"  Local address: {sock.getsockname()}")
        print(f"  Peer address: {sock.getpeername()}")
    else:
        print(f"✗ Connection failed with SO_ERROR = {socket_error}")
        print(f"  Error meaning: {errno.errorcode.get(socket_error, 'UNKNOWN')}")
        # Try to get more info
        try:
            error_msg = socket.error(socket_error).strerror
            print(f"  Error message: {error_msg}")
        except:
            pass
else:
    print("Timeout waiting for connection")

sock.close()
print("Socket closed")

