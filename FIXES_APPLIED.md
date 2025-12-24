# Diameter Connection Issues - Fixes Applied

## Problem Summary
You were unable to establish a Diameter connection to peer `VOICE-OBE.drfbor1.ipbb.prod.be:3875`, with the error:
```
WARNING <PeerConnection(...) was last available peer connection for <Diameter Credit Control Application (4)>, flagging app as not ready
```

## Root Causes Found and Fixed

### 1. **Windows Compatibility Issue with Non-Blocking Sockets** ✅ FIXED
**Location:** `diameter/node/node.py` lines ~512 and ~540

**Problem:** 
- On Windows, non-blocking `socket.connect()` returns error code `EWOULDBLOCK` (10035)
- The diameter library only checked for `EINPROGRESS` (10036), which is the Unix/Linux error code
- This caused the library to immediately reject connections as "failed" before they could establish

**Fix Applied:**
```python
# Changed from:
if e.args[0] != errno.EINPROGRESS:

# To:
if e.args[0] not in (errno.EINPROGRESS, errno.EWOULDBLOCK):
```

### 2. **Missing Host-IP-Address for Non-Blocking Connections** ✅ FIXED
**Location:** `diameter/node/node.py` line ~751

**Problem:**
- For non-blocking socket connections, `conn.host_ip_address` was never set
- This resulted in CER messages being sent with `Host-IP-Address = 0.0.0.0`
- Peers typically reject CER messages with invalid Host-IP-Address

**Fix Applied:**
```python
if socket_error == 0:
    # Set host_ip_address from the local socket address
    conn.host_ip_address = [wsock.getsockname()[0]]
    self._flag_peer_as_connected(conn)
    self.send_cer(conn)
```

### 3. **CEA Timeout Triggered Immediately** ✅ FIXED
**Location:** `diameter/node/node.py` line ~568

**Problem:**
- `PeerConnection._last_read` was initialized to `0` in the constructor
- When timeout was checked, `last_read_since` returned ~1.7 billion seconds (current Unix timestamp)
- This exceeded the 4-second CEA timeout immediately, closing the connection before any response could arrive

**Fix Applied:**
```python
def _flag_peer_as_connected(self, conn: PeerConnection):
    conn.state = PEER_CONNECTED
    # Reset the read timer so CEA timeout starts from now
    conn.reset_last_read()  # <-- Added this line
    # ...rest of function
```

## Current Status

### ✅ What's Working Now:
1. TCP connection to peer successfully establishes
2. CER (Capabilities Exchange Request) is properly sent with:
   - Correct Host-IP-Address: `16.0.0.1`
   - Correct Origin-Host: `relay2.test.realm`
   - Correct Origin-Realm: `mgt.mobistar.be`
   - Correct Acct-Application-Id: `4` (Credit Control)
3. CEA timeout works correctly (waits 6 seconds before timing out)

### ❌ Remaining Issue:
**The peer is not responding with a CEA (Capabilities Exchange Answer)**

After 6 seconds, the connection times out with:
```
WARNING <PeerConnection(...) exceeded CEA timeout, closing connection
```

## Why The Peer Might Not Be Responding

1. **Authentication/Authorization Issue:**
   - The peer may not recognize `relay2.test.realm` or `mgt.mobistar.be`
   - The peer may require specific Origin-Host/Origin-Realm values that are whitelisted

2. **Application Mismatch:**
   - You're advertising Credit Control (ID 4) as an **Accounting** application
   - The peer might expect it as an **Authentication** application
   - Or the peer might not support Credit Control at all

3. **Peer Configuration:**
   - The peer at `VOICE-OBE.drfbor1.ipbb.prod.be` might expect:
     - Different vendor IDs
     - Different product name
     - TLS/DTLS encryption
     - Specific Supported-Vendor-Id AVPs

4. **Network Issues:**
   - Firewall might be blocking return traffic
   - The peer might be sending responses but to a different port/address

## Recommendations

1. **Verify Peer Configuration:**
   - Check with the peer administrator if `relay2.test.realm` is authorized
   - Confirm the peer supports Credit Control Application (ID 4)
   - Ask if the peer expects it as Auth or Acct application

2. **Check Peer Logs:**
   - Look at logs on `VOICE-OBE.drfbor1.ipbb.prod.be` to see if CER is received
   - Check if the peer is rejecting it and why

3. **Try Wireshark/tcpdump:**
   ```powershell
   # Capture traffic to see if CEA is being sent
   tcpdump -i any -n port 3875 -w diameter_capture.pcap
   ```

4. **Test with Different Configuration:**
   - Try different Origin-Host/Origin-Realm values
   - Try changing `is_acct_application=True` to `is_auth_application=True`
   - Try adding more Vendor-IDs

5. **Check if Peer Requires Incoming Connections:**
   - Some diameter setups require bidirectional connections
   - The peer might expect to connect TO you as well

## Files Modified

All fixes were applied to:
```
D:\work\PythonProjects\Diameter_Sim\.venv\Lib\site-packages\diameter\node\node.py
```

The changes are in the installed library. If you recreate the virtual environment, you'll need to reapply these fixes.

