#!/usr/bin/env python3
"""
Simple Diameter Client for Testing

Sends test CCR messages to a Diameter server and displays the responses.
"""

import socket
import argparse
import sys


def send_diameter_message(host, port, message_data):
    """
    Send a Diameter message and receive response

    Args:
        host: Server hostname or IP
        port: Server port
        message_data: Message bytes to send

    Returns:
        Response bytes or None if error
    """
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout

        # Connect
        print(f"Connecting to {host}:{port}...")
        sock.connect((host, port))
        print("Connected!")

        # Send message
        print(f"Sending {len(message_data)} bytes...")
        sock.sendall(message_data)
        print("Message sent!")

        # Receive response
        print("Waiting for response...")
        response = sock.recv(4096)
        print(f"Received {len(response)} bytes!")

        sock.close()
        return response

    except socket.timeout:
        print("Error: Connection timed out")
        return None
    except ConnectionRefusedError:
        print(f"Error: Connection refused. Is the server running on {host}:{port}?")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def create_test_ccr():
    """
    Create a simple test CCR message (minimal Diameter header)

    Returns:
        Bytes representing a minimal CCR
    """
    # Diameter header: Version(1) | Length(3) | Flags(1) | Code(3) | App-ID(4) | HbH(4) | E2E(4)
    version = 1
    flags = 0xC0  # Request flag + Proxiable flag
    cmd_code = 272  # Credit-Control
    app_id = 4  # Credit Control Application
    hbh_id = 0x00000001  # Hop-by-Hop ID
    e2e_id = 0x00000001  # End-to-End ID

    # Build header (20 bytes minimum)
    length = 20
    header = bytes([version]) + length.to_bytes(3, 'big')
    header += bytes([flags]) + cmd_code.to_bytes(3, 'big')
    header += app_id.to_bytes(4, 'big')
    header += hbh_id.to_bytes(4, 'big')
    header += e2e_id.to_bytes(4, 'big')

    return header


def parse_diameter_header(data):
    """Parse Diameter message header"""
    if len(data) < 20:
        return None

    version = data[0]
    length = int.from_bytes(data[1:4], byteorder='big')
    flags = data[4]
    cmd_code = int.from_bytes(data[5:8], byteorder='big') & 0x00FFFFFF
    app_id = int.from_bytes(data[8:12], byteorder='big')
    hbh_id = int.from_bytes(data[12:16], byteorder='big')
    e2e_id = int.from_bytes(data[16:20], byteorder='big')

    is_request = bool(flags & 0x80)
    is_answer = not is_request

    return {
        'version': version,
        'length': length,
        'flags': flags,
        'cmd_code': cmd_code,
        'app_id': app_id,
        'hbh_id': hbh_id,
        'e2e_id': e2e_id,
        'is_request': is_request,
        'is_answer': is_answer
    }


def main():
    parser = argparse.ArgumentParser(
        description='Simple Diameter Client - Send test CCR messages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send to localhost
  python client.py
  
  # Send to specific host and port
  python client.py --host 127.0.0.1 --port 3868
  
  # Send multiple messages
  python client.py --count 5
        """
    )

    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Server hostname or IP (default: 127.0.0.1)'
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        default=3868,
        help='Server port (default: 3868)'
    )

    parser.add_argument(
        '--count', '-c',
        type=int,
        default=1,
        help='Number of messages to send (default: 1)'
    )

    args = parser.parse_args()

    print("="*70)
    print("Diameter Test Client")
    print("="*70)
    print(f"Target: {args.host}:{args.port}")
    print(f"Messages to send: {args.count}")
    print("="*70)
    print()

    success_count = 0

    for i in range(args.count):
        if args.count > 1:
            print(f"\n--- Message {i+1}/{args.count} ---")

        # Create test message
        ccr_data = create_test_ccr()

        # Send and receive
        response = send_diameter_message(args.host, args.port, ccr_data)

        if response:
            # Parse response
            header = parse_diameter_header(response)
            if header:
                print(f"\nResponse Details:")
                print(f"  Command Code: {header['cmd_code']}")
                print(f"  Is Answer: {header['is_answer']}")
                print(f"  Application ID: {header['app_id']}")
                print(f"  Length: {header['length']} bytes")

                if header['cmd_code'] == 272 and header['is_answer']:
                    print(f"  ✓ Valid CCA (Credit-Control-Answer) received!")
                    success_count += 1
                else:
                    print(f"  ⚠ Unexpected response")
            else:
                print("  ⚠ Could not parse response header")
        else:
            print("  ✗ No response received")

        # Small delay between messages
        if i < args.count - 1:
            import time
            time.sleep(0.1)

    print("\n" + "="*70)
    print(f"Summary: {success_count}/{args.count} messages successful")
    print("="*70)

    return 0 if success_count == args.count else 1


if __name__ == '__main__':
    sys.exit(main())

