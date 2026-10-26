import subprocess


def test_http(namespace, url, expected_success):
    result = subprocess.run(
        [
            "ip", "netns", "exec", namespace,
            "curl", "--max-time", "3",
            "-s", "-o", "/dev/null",
            "-w", "%{http_code}",
            url
        ],
        capture_output=True,
        text=True
    )

    success = (
        result.returncode == 0
        and result.stdout.strip() == "200"
    )

    passed = success == expected_success

    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {namespace} -> {url}")

    return passed


def run_validation():
    print("=== SecureNet Security Validation ===")

    url = "http://10.10.30.2:8080/"

    results = [
        test_http("staff", url, True),
        test_http("guest", url, False),

        test_ping("staff", "10.10.30.2", False),
        test_ping("guest", "10.10.30.2", False),

        test_firewall_rules()
    ]

    passed = sum(results)
    total = len(results)

    print(f"\nResult: {passed}/{total} tests passed")

    return passed == total

def test_ping(namespace, destination, expected_success):
    result = subprocess.run(
        [
            "ip", "netns", "exec", namespace,
            "ping", "-c", "2", "-W", "1",
            destination
        ],
        capture_output=True,
        text=True
    )

    success = result.returncode == 0
    passed = success == expected_success

    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {namespace} -> {destination} (ICMP)")

    return passed

def test_firewall_rules():
    result = subprocess.run(
        [
            "ip", "netns", "exec", "router",
            "nft", "list", "chain", "inet", "filter", "forward"
        ],
        capture_output=True,
        text=True
    )

    rules = result.stdout

    passed = (
        result.returncode == 0
        and "policy drop" in rules
        and "ct state established,related accept" in rules
        and "tcp dport 8080" in rules
    )

    status = "PASS" if passed else "FAIL"

    print(f"[{status}] Firewall rules configured")

    return passed

