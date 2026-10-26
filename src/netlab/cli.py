import subprocess
import sys
import argparse
from netlab.network import setup_network, show_status, teardown_network
from netlab.firewall import setup_firewall
from netlab.validation import run_validation

def main():
    parser = argparse.ArgumentParser(description="Secure Lab - Network Automation CLI")

    parser.add_argument("command", choices=["up", "status", "down", "validate"], help="Network operation to perform")

    args = parser.parse_args()

    try:
        if args.command == "up":
            setup_network()
            setup_firewall()
        elif args.command == "status":
            show_status()

        elif args.command == "down":
            teardown_network()
        elif args.command == "validate":
            if run_validation():
                return 0
            return 1

    except (RuntimeError, ValueError, subprocess.CalledProcessError) as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.command == "up":
            print(
                "Setup may be incomplete. "
                "Inspect the namespaces and firewall rules before retrying.",
                file=sys.stderr
            )

        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
