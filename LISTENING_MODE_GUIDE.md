# Listening Mode Guide

## Overview

The Gy Protocol implementation now supports **listening mode**, allowing it to function as a Diameter server that receives and responds to CCR (Credit-Control-Request) messages.

## Features

✅ **Full Server Mode** - Listen for incoming Diameter connections  
✅ **Automatic Message Handling** - Process CCR, send CCA responses  
✅ **Statistics Tracking** - Monitor messages received and sent  
✅ **Mock Mode** - Works without bromelia for testing  
✅ **Command-Line Interface** - Easy to start and configure  
✅ **Multi-threaded** - Handle multiple clients simultaneously  

## Quick Start

### Method 1: Using server.py (Recommended)

```bash
# Start with defaults (0.0.0.0:3868)
python server.py

# Start on localhost only
python server.py --ip 127.0.0.1

# Custom port
python server.py --port 3869

# Custom host identity
python server.py --host ocs.mycompany.com --realm mycompany.com
```

### Method 2: Using main.py with --listen flag

```bash
# Start in listening mode
python main.py --listen

# With custom settings
python main.py --listen --ip 127.0.0.1 --port 3868 --host ocs.example.com
```

### Method 3: Programmatic API

```python
from main import GyDiameterApplication

config = {
    'host': 'ocs.example.com',
    'realm': 'example.com',
    'ip': '0.0.0.0',
    'port': 3868
}

app = GyDiameterApplication(config)
app.start(blocking=True)  # Starts server and blocks
```

## Command-Line Options

### server.py Options

```
--host HOST         Diameter host identity (default: gy-server.example.com)
--realm REALM       Diameter realm (default: example.com)
--ip IP             IP address to bind to (default: 0.0.0.0)
--port, -p PORT     Port to listen on (default: 3868)
--verbose, -v       Enable verbose logging
```

### main.py --listen Options

```
--listen, -l        Start in listening mode
--host HOST         Diameter host identity
--realm REALM       Diameter realm
--ip IP             IP address to bind to
--port, -p PORT     Port to listen on
```

## Operating Modes

### With Bromelia (Full Diameter Stack)

When bromelia is installed:
```bash
pip install bromelia
python server.py
```

Features:
- Full Diameter protocol support
- Proper message encoding/decoding
- Standard Diameter capabilities exchange
- Production-ready

### Without Bromelia (Mock Mode)

When bromelia is not installed:
```bash
python server.py
```

Features:
- Simple TCP socket server
- Basic Diameter message handling
- Perfect for testing and development
- No external dependencies

The server automatically detects bromelia and uses mock mode if not available.

## Testing the Server

### Using the Test Client

```bash
# In Terminal 1: Start server
python server.py --ip 127.0.0.1 --port 3868

# In Terminal 2: Send test message
python client.py --host 127.0.0.1 --port 3868

# Send multiple messages
python client.py --host 127.0.0.1 --port 3868 --count 10
```

### Using netcat

```bash
# Start server
python server.py

# Send test data
echo "test" | nc localhost 3868
```

### Using diameter tools

```bash
# With diameterctl or other Diameter testing tools
diameterctl send-ccr --host localhost --port 3868
```

## Examples

### Example 1: Local Testing

```bash
# Terminal 1
python server.py --ip 127.0.0.1 --port 13868

# Terminal 2
python client.py --host 127.0.0.1 --port 13868
```

### Example 2: Network Server

```bash
# Start server on all interfaces
python server.py --ip 0.0.0.0 --port 3868 --host ocs.example.com --realm example.com

# Clients can connect from network
python client.py --host 192.168.1.100 --port 3868
```

### Example 3: Programmatic Control

```python
from main import GyDiameterApplication
import threading

config = {
    'host': 'test-ocs.example.com',
    'realm': 'example.com',
    'ip': '127.0.0.1',
    'port': 3868
}

app = GyDiameterApplication(config)

# Start in background thread
server_thread = threading.Thread(target=lambda: app.start(blocking=True), daemon=True)
server_thread.start()

# Do other work...
# Server runs in background

# Stop when done
app.stop()
```

## Server Behavior

### What the Server Does

1. **Binds to specified IP and port**
   ```
   Listening on: 0.0.0.0:3868
   ```

2. **Accepts incoming connections**
   ```
   [10:30:45] New connection from ('192.168.1.100', 52341)
   ```

3. **Receives Diameter messages**
   ```
   [10:30:45] Received 156 bytes from ('192.168.1.100', 52341)
   [10:30:45] Detected CCR message
   ```

4. **Sends CCA responses**
   ```
   [10:30:45] Sent CCA response
   ```

5. **Tracks statistics**
   ```
   CCR Initial Received:    5
   CCR Update Received:     3
   CCR Terminate Received:  2
   CCA Sent:                10
   Errors:                  0
   ```

### Message Handling

The server handles:
- **CCR Initial** (CC-Request-Type = 1)
- **CCR Update** (CC-Request-Type = 2)
- **CCR Terminate** (CC-Request-Type = 3)
- **CCR Event** (CC-Request-Type = 4)

For each CCR, it sends an appropriate CCA response.

## Statistics

View statistics at shutdown:

```
============================================================
Gy Diameter Application Statistics:
============================================================
CCR Initial Received:    15
CCR Update Received:     8
CCR Terminate Received:  3
CCA Sent:                26
Errors:                  0
============================================================
```

## Logging

Server logs include:
- Connection events
- Message receipts
- Response sending
- Errors and warnings

Example output:
```
======================================================================
Starting MOCK Gy Diameter Server (Testing Mode)
======================================================================
Host Identity: gy-server.example.com
Realm: example.com
Listening on: 127.0.0.1:3868
======================================================================

✓ Server started successfully
✓ Waiting for connections...

[14:23:15] New connection from ('127.0.0.1', 54321)
[14:23:15] Received 20 bytes from ('127.0.0.1', 54321)
[14:23:15] Detected CCR message
[14:23:15] Sent CCA response
[14:23:15] Connection closed: ('127.0.0.1', 54321)
```

## Error Handling

### Port Already in Use

```
Error starting mock server: [Errno 98] Address already in use
```

**Solution**: Use a different port or stop the other service.

### Permission Denied (Port < 1024)

```
Error starting mock server: [Errno 13] Permission denied
```

**Solution**: Use port >= 1024 or run with elevated privileges.

### Connection Refused (Client)

```
Error: Connection refused. Is the server running on 127.0.0.1:3868?
```

**Solution**: Start the server first.

## Production Deployment

### With Bromelia

```bash
# Install bromelia
pip install bromelia

# Start server
python server.py --ip 0.0.0.0 --port 3868 --host ocs.production.com --realm production.com
```

### As a Service (Linux)

Create `/etc/systemd/system/diameter-gy.service`:

```ini
[Unit]
Description=Diameter Gy Server
After=network.target

[Service]
Type=simple
User=diameter
WorkingDirectory=/opt/diameter-gy
ExecStart=/usr/bin/python3 /opt/diameter-gy/server.py --ip 0.0.0.0 --port 3868
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable diameter-gy
sudo systemctl start diameter-gy
sudo systemctl status diameter-gy
```

### As a Service (Windows)

Use NSSM (Non-Sucking Service Manager):

```cmd
nssm install DiameterGy "C:\Python\python.exe" "C:\DiameterSim\server.py"
nssm set DiameterGy AppDirectory "C:\DiameterSim"
nssm start DiameterGy
```

## Security Considerations

### Firewall

Open the Diameter port:

```bash
# Linux (iptables)
sudo iptables -A INPUT -p tcp --dport 3868 -j ACCEPT

# Linux (firewalld)
sudo firewall-cmd --permanent --add-port=3868/tcp
sudo firewall-cmd --reload

# Windows
netsh advfirewall firewall add rule name="Diameter Gy" dir=in action=allow protocol=TCP localport=3868
```

### Binding

- **0.0.0.0** - Listen on all interfaces (public access)
- **127.0.0.1** - Listen on localhost only (local testing)
- **Specific IP** - Listen on one interface only

### TLS/IPsec

For production, consider:
- TLS encryption (if supported by bromelia)
- IPsec tunnels for transport security
- VPN connections for client-server communication

## Performance Tuning

### Socket Options

The mock server uses:
```python
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

### Thread Pool

Each connection is handled in a separate thread (daemon=True).

### Timeouts

Client timeout: 10 seconds (configurable in client.py)

## Troubleshooting

### Server won't start

1. Check if port is available: `netstat -an | findstr 3868`
2. Try different port: `--port 3869`
3. Check permissions for ports < 1024

### No connections received

1. Check firewall settings
2. Verify server is listening: `netstat -an | findstr 3868`
3. Test with telnet: `telnet localhost 3868`

### Client can't connect

1. Verify server is running
2. Check IP address (0.0.0.0 vs 127.0.0.1)
3. Verify port number matches
4. Check network connectivity

## API Reference

### GyDiameterApplication.start(blocking=True)

Start the Diameter server.

**Parameters:**
- `blocking` (bool): If True, blocks until Ctrl+C. If False, returns immediately.

**Returns:** None

**Raises:** ImportError if bromelia required but not installed

### GyDiameterApplication.stop()

Stop the Diameter server and print statistics.

**Returns:** None

### GyDiameterApplication.get_statistics()

Get current statistics dictionary.

**Returns:** Dict with keys:
- `ccr_initial_received`
- `ccr_update_received`
- `ccr_terminate_received`
- `cca_sent`
- `errors`

### GyDiameterApplication.print_statistics()

Print statistics to console.

**Returns:** None

## Next Steps

1. **Test locally**: `python server.py --ip 127.0.0.1`
2. **Send test message**: `python client.py`
3. **Review statistics**: Check output on server shutdown
4. **Install bromelia**: `pip install bromelia` for full features
5. **Deploy**: Set up as a service for production use

## Support

For issues or questions:
1. Check this guide for common solutions
2. Review server logs for error messages
3. Test with mock mode first before using bromelia
4. Verify network connectivity and firewall rules

## References

- RFC 6733 - Diameter Base Protocol
- RFC 4006 - Diameter Credit-Control Application
- Bromelia Documentation: https://github.com/heimiricmr/bromelia

