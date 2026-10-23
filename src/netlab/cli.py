import subprocess
import sys
import argparse
from netlab.network import setup_network, show_status, teardown_network

def main():
    parser = argparse.ArgumentParser(description="Secure Lab - Network Automation CLI")

    parser.add_argument("command", choices=["up", "status", "down"], help="Network operation to perform")

    args = parser.parse_args()

    try:
        if args.command == "up":
            setup_network()

        elif args.command == "status":
            show_status()

        elif args.command == "down":
            teardown_network()
        
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
