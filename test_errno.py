"""Check errno values on Windows"""
import errno
import sys

print(f"Platform: {sys.platform}")
print(f"Has EINPROGRESS: {hasattr(errno, 'EINPROGRESS')}")
if hasattr(errno, 'EINPROGRESS'):
    print(f"  errno.EINPROGRESS = {errno.EINPROGRESS}")

print(f"Has EWOULDBLOCK: {hasattr(errno, 'EWOULDBLOCK')}")
if hasattr(errno, 'EWOULDBLOCK'):
    print(f"  errno.EWOULDBLOCK = {errno.EWOULDBLOCK}")

print(f"Has WSAEWOULDBLOCK: {hasattr(errno, 'WSAEWOULDBLOCK')}")
if hasattr(errno, 'WSAEWOULDBLOCK'):
    print(f"  errno.WSAEWOULDBLOCK = {errno.WSAEWOULDBLOCK}")

# Test what Windows actually returns
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(False)
try:
    sock.connect(('16.0.0.30', 3875))
except socket.error as e:
    print(f"\nActual error from non-blocking connect:")
    print(f"  errno: {e.args[0]}")
    print(f"  message: {e.args[1]}")
    print(f"  Matches EINPROGRESS: {e.args[0] == getattr(errno, 'EINPROGRESS', -1)}")
    print(f"  Matches EWOULDBLOCK: {e.args[0] == getattr(errno, 'EWOULDBLOCK', -1)}")
sock.close()

