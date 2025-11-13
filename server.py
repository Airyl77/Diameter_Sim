#!/usr/bin/env python3
"""
Gy Diameter Server - Listening Mode

This script starts a Diameter server that listens for incoming CCR (Credit-Control-Request)
messages and responds with CCA (Credit-Control-Answer) messages.

Usage:
    python server.py                          # Start with defaults
    python server.py --port 3868              # Custom port
    python server.py --ip 127.0.0.1 --port 3868
    python server.py --host ocs.example.com --realm example.com
"""

import argparse
import sys
from main import GyDiameterApplication


def main():
    """Main entry point for the Diameter server"""

    parser = argparse.ArgumentParser(
        description='Gy Diameter Server - Start in listening mode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with default settings (0.0.0.0:3868)
  python server.py
  
  # Start on localhost only
  python server.py --ip 127.0.0.1
  
  # Start on custom port
  python server.py --port 3869
  
  # Custom host identity and realm
  python server.py --host ocs.mycompany.com --realm mycompany.com
  
  # All options
  python server.py --ip 0.0.0.0 --port 3868 --host ocs.example.com --realm example.com

Notes:
  - Without bromelia library, runs in MOCK mode for testing
  - Install bromelia for full Diameter protocol support: pip install bromelia
  - Press Ctrl+C to stop the server
  - Statistics will be shown on shutdown
        """
    )

    parser.add_argument(
        '--host',
        default='gy-server.example.com',
        help='Diameter host identity (default: gy-server.example.com)'
    )

    parser.add_argument(
        '--realm',
        default='example.com',
        help='Diameter realm (default: example.com)'
    )

    parser.add_argument(
        '--ip',
        default='0.0.0.0',
        help='IP address to bind to (default: 0.0.0.0 - all interfaces)'
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        default=3868,
        help='Port to listen on (default: 3868 - standard Diameter port)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Validate port
    if not (1 <= args.port <= 65535):
        print(f"Error: Invalid port number {args.port}. Must be between 1 and 65535.")
        sys.exit(1)

    # Build configuration
    config = {
        'host': args.host,
        'realm': args.realm,
        'ip': args.ip,
        'port': args.port,
        'verbose': args.verbose
    }

    # Create and start application
    print("="*70)
    print("Gy Diameter Server")
    print("="*70)
    print()

    app = GyDiameterApplication(config)

    try:
        app.start(blocking=True)
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("Shutdown signal received...")
        print("="*70)
        app.stop()
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

