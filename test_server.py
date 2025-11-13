"""
Test script to demonstrate listening mode
"""
import time
import threading
from main import GyDiameterApplication

def test_listening_mode():
    """Test the listening mode functionality"""

    print("="*70)
    print("TESTING LISTENING MODE")
    print("="*70)
    print()

    # Configuration
    config = {
        'host': 'test-ocs.example.com',
        'realm': 'example.com',
        'ip': '127.0.0.1',
        'port': 13868  # Use non-standard port for testing
    }

    print("Creating Diameter application...")
    app = GyDiameterApplication(config)

    print("Starting server in background thread...")
    server_thread = threading.Thread(
        target=lambda: app.start(blocking=True),
        daemon=True
    )
    server_thread.start()

    # Give server time to start
    print("Waiting for server to initialize...")
    time.sleep(2)

    print("\n" + "="*70)
    print("Server should now be listening on 127.0.0.1:13868")
    print("="*70)
    print()
    print("You can test it with:")
    print("  python client.py --host 127.0.0.1 --port 13868")
    print()
    print("Or send a CCR message using any Diameter client.")
    print()
    print("The server will:")
    print("  ✓ Accept incoming connections")
    print("  ✓ Receive CCR messages")
    print("  ✓ Parse command codes")
    print("  ✓ Send CCA responses")
    print("  ✓ Track statistics")
    print()
    print("="*70)
    print("Server is running. Statistics will be shown when stopped.")
    print("="*70)
    print()

    # Keep server running for demonstration
    try:
        print("Server running for 30 seconds (or press Ctrl+C to stop)...\n")
        for i in range(30):
            time.sleep(1)
            if (i + 1) % 10 == 0:
                print(f"  Still running... ({i+1}/30 seconds)")
    except KeyboardInterrupt:
        print("\n\nStopping server...")

    print("\n" + "="*70)
    print("Test completed. Server statistics:")
    print("="*70)
    app.print_statistics()


if __name__ == '__main__':
    test_listening_mode()

