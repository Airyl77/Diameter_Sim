# Diameter Connection Troubleshooting - Detailed Steps

## Date
December 22-23, 2025

## Initial Problem
User reported error when trying to establish Diameter connection to peer `VOICE-OBE.drfbor1.ipbb.prod.be:3875`:
```
WARNING <PeerConnection(...) was last available peer connection for <Diameter Credit Control Application (4)>, flagging app as not ready
```

The connection was immediately failing without any CER/CEA exchange taking place.

---

## Investigation Process

### Step 1: Initial Diagnostics
- Verified network connectivity to peer (ping successful)
- Verified TCP connectivity to port 3875 (successful)
- Verified local IP address 16.0.0.1 exists on the machine
- Identified that connections were being created but immediately removed

### Step 2: Root Cause Analysis
Investigated the diameter library source code and discovered **three critical bugs** affecting Windows compatibility:

---

## Bug Fixes Applied

### Bug #1: Windows Non-Blocking Socket Compatibility Issue

**File Modified:** `D:\work\PythonProjects\Diameter_Sim\.venv\Lib\site-packages\diameter\node\node.py`

**Location:** Lines ~512 and ~540 (in `_connect_to_peer` method)

**Problem:**
- On Windows, non-blocking `socket.connect()` returns error code `EWOULDBLOCK` (10035)
- On Unix/Linux, non-blocking `socket.connect()` returns error code `EINPROGRESS` (10036)
- The diameter library only checked for `EINPROGRESS`
- This caused Windows connections to be immediately rejected as "failed"

**Original Code:**
```python
try:
    peer_socket.connect((peer.ip_addresses[0], peer.port))
except socket.error as e:
    if e.args[0] != errno.EINPROGRESS:
        self.remove_peer_connection(conn, DISCONNECT_REASON_SOCKET_FAIL)
        return
    self.logger.warning(f"{conn} socket not yet ready, waiting")
```

**Fixed Code:**
```python
try:
    peer_socket.connect((peer.ip_addresses[0], peer.port))
except socket.error as e:
    # On Windows, non-blocking connect returns EWOULDBLOCK instead of EINPROGRESS
    if e.args[0] not in (errno.EINPROGRESS, errno.EWOULDBLOCK):
        self.remove_peer_connection(conn, DISCONNECT_REASON_SOCKET_FAIL)
        return
    self.logger.warning(f"{conn} socket not yet ready, waiting")
```

**Applied twice:**
1. For TCP connections (line ~512)
2. For SCTP connections (line ~540)

---

### Bug #2: Missing Host-IP-Address for Non-Blocking Connections

**File Modified:** `D:\work\PythonProjects\Diameter_Sim\.venv\Lib\site-packages\diameter\node\node.py`

**Location:** Line ~751 (in `_handle_connections` method, where socket becomes writable)

**Problem:**
- When a non-blocking socket connection completes, `conn.host_ip_address` was never set
- This resulted in CER messages being sent with `Host-IP-Address = (1, '0.0.0.0')` instead of the actual local IP
- Peers typically reject CER messages with invalid or missing Host-IP-Address

**Original Code:**
```python
if conn.state == PEER_CONNECTING:
    socket_error = wsock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
    if socket_error == 0:
        self._flag_peer_as_connected(conn)
        self.send_cer(conn)
```

**Fixed Code:**
```python
if conn.state == PEER_CONNECTING:
    socket_error = wsock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
    if socket_error == 0:
        # Set host_ip_address from the local socket address
        conn.host_ip_address = [wsock.getsockname()[0]]
        self._flag_peer_as_connected(conn)
        self.send_cer(conn)
```

**Impact:**
- CER now correctly includes `Host-IP-Address: (1, '16.0.0.1')` instead of `0.0.0.0`

---

### Bug #3: CEA Timeout Triggered Immediately

**File Modified:** `D:\work\PythonProjects\Diameter_Sim\.venv\Lib\site-packages\diameter\node\node.py`

**Location:** Line ~568 (in `_flag_peer_as_connected` method)

**Problem:**
- `PeerConnection._last_read` was initialized to `0` in the constructor
- When CEA timeout was checked, `last_read_since` calculated as `int(time.time()) - 0`
- This returned ~1.7 billion seconds (current Unix timestamp)
- This massively exceeded the 4-second CEA timeout
- Connection was immediately closed before peer could respond

**Original Code:**
```python
def _flag_peer_as_connected(self, conn: PeerConnection):
    conn.state = PEER_CONNECTED
    peer = self._find_connection_peer(conn)
    if peer:
        peer.last_connect = int(time.time())

    self.connection_logger.info(
        f"{conn} is now connected, waiting CER/CEA to complete")
```

**Fixed Code:**
```python
def _flag_peer_as_connected(self, conn: PeerConnection):
    conn.state = PEER_CONNECTED
    # Reset the read timer so CEA timeout starts from now
    conn.reset_last_read()
    peer = self._find_connection_peer(conn)
    if peer:
        peer.last_connect = int(time.time())

    self.connection_logger.info(
        f"{conn} is now connected, waiting CER/CEA to complete")
```

**Impact:**
- CEA timeout now correctly waits 6 seconds for peer response
- Connection stays open long enough to receive CEA

---

## Application Code Changes

### Change #1: Fixed CCR Destination Realm

**File Modified:** `D:\work\PythonProjects\Diameter_Sim\main.py`

**Problem:**
- Original code used `destination_realm = client.node.realm_name.encode()` which resolved to `"mobistar.be"`
- But the peer is in realm `"ipbb.prod.be"`
- This caused routing error: `NotRoutable: No peers in realm mobistar.be configured`

**Original Code (line ~81):**
```python
ccr.destination_realm = client.node.realm_name.encode()
```

**Fixed Code:**
```python
ccr.destination_realm = b"ipbb.prod.be"  # Must match peer's realm
```

---

### Change #2: Added Destination-Host to CCR

**File Modified:** `D:\work\PythonProjects\Diameter_Sim\main.py`

**Location:** After `destination_realm` (line ~82)

**Problem:**
- Some peers require explicit `Destination-Host` for proper routing
- This was missing in the original code

**Added:**
```python
ccr.destination_host = b"VOICE-OBE.drfbor1.ipbb.prod.be"  # Specify the exact peer
```

---

### Change #3: Added Origin-State-Id to CCR

**File Modified:** `D:\work\PythonProjects\Diameter_Sim\main.py`

**Location:** After `cc_request_number` (line ~87)

**Problem:**
- Peer was returning error code 5005 (DIAMETER_MISSING_AVP)
- `Origin-State-Id` is often required for Credit Control requests

**Added:**
```python
ccr.origin_state_id = client.node.state_id  # Add Origin-State-Id
```

---

### Change #4: Increased CCR Timeout

**File Modified:** `D:\work\PythonProjects\Diameter_Sim\main.py`

**Location:** Line ~137

**Problem:**
- Peer was taking ~6 seconds to respond
- Original timeout was 5 seconds
- This caused `TimeoutError` even though peer was responding

**Original Code:**
```python
cca = client.send_request(ccr, timeout=5)
```

**Fixed Code:**
```python
cca = client.send_request(ccr, timeout=10)
```

---

### Change #5: Added DWR Before Connection Ready

**File Modified:** `D:\work\PythonProjects\Diameter_Sim\main.py`

**Location:** Lines ~61-65

**Problem:**
- Peer was not consistently responding to CER
- Sending DWR first seemed to help establish connection

**Added:**
```python
# Send DWR first (this was working before)
print("Sending DWR to establish connection...")
for conn in node.connections.values():
    print(f"Sending DWR to: {conn}")
    node.send_dwr(conn)
```

---

### Change #6: Added Connection Ready Wait

**File Modified:** `D:\work\PythonProjects\Diameter_Sim\main.py`

**Location:** Lines ~67-72

**Problem:**
- Original code tried to send CCR before CER/CEA completed
- This caused routing errors

**Added:**
```python
# Wait for the connection to be ready before sending CCR
print("Waiting for connection to be ready...")
client.wait_for_ready()
print("Connection ready!")
```

---

### Change #7: Improved Result Code Display

**File Modified:** `D:\work\PythonProjects\Diameter_Sim\main.py`

**Location:** Line ~140

**Original Code:**
```python
print(cca.result_code)
```

**Fixed Code:**
```python
print(f"Result Code: {cca.result_code}")
```

**Added comment:**
```python
# Should print 2001, if all goes well. 5005 means missing AVPs.
```

---

## Results After All Fixes

### Connection Status: ✅ WORKING
- TCP connection establishes successfully
- CER sent with correct Host-IP-Address: `16.0.0.1`
- CEA received successfully with Result-Code: 2001 (SUCCESS)
- Connection marked as READY
- Peer advertises: `Auth-Application-Id: 4` (Credit Control)

### CCR/CCA Exchange: ⚠️ PARTIALLY WORKING
- CCR sent successfully
- CCA received successfully (within 10-second timeout)
- **Current Result-Code: 5005** (DIAMETER_MISSING_AVP)
- This means peer still requires additional AVPs beyond what we've provided

### Current CCR Structure Being Sent:
```
Session-Id: relay2.test.realm;[unique-id]
Origin-Host: relay2.test.realm
Origin-Realm: mobistar.be
Destination-Realm: ipbb.prod.be
Destination-Host: VOICE-OBE.drfbor1.ipbb.prod.be
Auth-Application-Id: 4
Service-Context-Id: 32274@3gpp.org
CC-Request-Type: 4 (EVENT_REQUEST)
CC-Request-Number: 1
Origin-State-Id: [state-id]
User-Name: diameter
Event-Timestamp: [current-time]
Requested-Action: 0 (DIRECT_DEBITING)
Subscription-Id:
  Subscription-Id-Type: 0 (END_USER_E164)
  Subscription-Id-Data: 41780000001
Multiple-Services-Credit-Control:
  Requested-Service-Unit:
    CC-Service-Specific-Units: 1
  Service-Identifier: 1
Service-Information (3GPP):
  SMS-Information:
    Data-Coding-Scheme: 8
    SM-Message-Type: 0 (SUBMISSION)
    Recipient-Info:
      Recipient-Address:
        Address-Type: 1 (MSISDN)
        Address-Data: 41780000002
```

---

## Outstanding Issues

### Issue: Result-Code 5005 (DIAMETER_MISSING_AVP)

The peer is still rejecting the CCR due to missing mandatory AVPs. The peer does not specify which AVPs are missing in the Failed-AVP field.

**Possible Missing AVPs:**
1. **Originator-Address** - For SMS charging, often required
2. **Multiple-Services-Indicator** - May be required for some implementations
3. **Service-Parameter-Info** - Vendor-specific requirements
4. **Originator-SCCP-Address** - For SMS-specific implementations
5. **Recipient-SCCP-Address** - For SMS-specific implementations

**Next Steps to Resolve:**
1. Contact peer administrator for documentation on required AVPs
2. Check peer logs to see which AVP is missing
3. Review vendor-specific (MediationZone by Oracle) documentation for Credit Control
4. Try adding common required AVPs one by one
5. Use Wireshark to compare with working CCR examples if available

---

## Files Modified Summary

### Library Files (in .venv):
1. `diameter/node/node.py` - 3 bug fixes for Windows compatibility

### Application Files:
1. `main.py` - 7 changes for proper CCR structure and flow

### Documentation Files Created:
1. `FIXES_APPLIED.md` - Initial summary of fixes
2. `steps.md` - This detailed step-by-step document

---

## Important Notes

### About Library Modifications
The fixes were applied directly to the installed diameter library in:
```
D:\work\PythonProjects\Diameter_Sim\.venv\Lib\site-packages\diameter\node\node.py
```

**⚠️ WARNING:** If you recreate the virtual environment or reinstall the diameter package, these fixes will be lost and need to be reapplied.

**Recommended Actions:**
1. Create a patch file for the library fixes
2. Consider contributing these fixes back to the diameter library maintainers
3. Document the need to reapply fixes if venv is recreated
4. Consider forking the diameter library and using your patched version

### Testing Environment
- **OS:** Windows 10/11
- **Python Version:** 3.x (using .venv)
- **Local IP:** 16.0.0.1
- **Peer IP:** 16.0.0.30
- **Peer Port:** 3875
- **Peer Product:** MediationZone (Oracle)
- **Application:** Credit Control (ID: 4) as Auth-Application

---

## Commands Used for Testing

### Network Testing:
```powershell
ping -n 2 16.0.0.30
Test-NetConnection -ComputerName 16.0.0.30 -Port 3875
```

### Running the Application:
```powershell
cd D:\work\PythonProjects\Diameter_Sim
python main.py
```

### Checking IP Configuration:
```powershell
Get-NetIPAddress | Where-Object {$_.IPAddress -eq '16.0.0.1'}
```

---

## Timeline of Events

1. **Initial Problem Report** - Connection failing immediately with "flagging app as not ready"
2. **Bug #1 Discovered** - Windows EWOULDBLOCK vs EINPROGRESS issue
3. **Bug #1 Fixed** - Connection now attempts properly
4. **Bug #2 Discovered** - Host-IP-Address set to 0.0.0.0
5. **Bug #2 Fixed** - CER now has correct local IP
6. **Bug #3 Discovered** - CEA timeout triggering immediately
7. **Bug #3 Fixed** - CEA timeout now waits properly
8. **Connection Established** - CER/CEA exchange working, peer responds with code 2001
9. **CCR Routing Error** - Wrong destination realm
10. **Realm Fixed** - CCR now routes to correct peer
11. **CCR Timeout** - Response taking 6 seconds, timeout was 5
12. **Timeout Increased** - Now receiving CCA responses
13. **Result Code 5005** - Peer reporting missing AVPs
14. **AVPs Added** - Added Destination-Host, Origin-State-Id
15. **Current Status** - Connection fully working, CCR needs additional AVPs

---

## Conclusion

The core connection issues have been **completely resolved**. The application can now:
- ✅ Establish TCP connections on Windows
- ✅ Send CER with correct parameters
- ✅ Receive CEA successfully
- ✅ Maintain active Diameter connections
- ✅ Send CCR messages
- ✅ Receive CCA responses

The remaining work is to identify which specific AVPs the peer's Credit Control implementation requires, which is a configuration/business logic issue rather than a technical connectivity problem.

