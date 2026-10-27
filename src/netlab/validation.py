import subprocess
from netlab.models import TestResult
from netlab.reporting import save_json_report

def test_ip_forwarding():
    result = subprocess.run(
        [
            "ip", "netns", "exec", "router",
            "sysctl", "-n", "net.ipv4.ip_forward"
        ],
        capture_output=True,
        text=True
    )

    actual = result.stdout.strip()
    passed = result.returncode == 0 and actual == "1"

    test_result = TestResult(
        name="Router IP forwarding",
        passed=passed,
        expected="1",
        actual=actual if result.returncode == 0 else "command failed",
        details=f"sysctl exit code {result.returncode}"
    )

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_result.name}: {test_result.actual}")

    return test_result

def test_network_config(namespace, interface, expected_ip, expected_gateway):
    ip_result = subprocess.run(
        [
            "ip", "netns", "exec", namespace,
            "ip", "-4", "-o", "addr", "show", "dev", interface
        ],
        capture_output=True,
        text=True
    )

    route_result = subprocess.run(
        [
            "ip", "netns", "exec", namespace,
            "ip", "-4", "route", "show", "default"
        ],
        capture_output=True,
        text=True
    )

    ip_ok = (
        ip_result.returncode == 0
        and expected_ip in ip_result.stdout.split()
    )

    gateway_ok = (
        route_result.returncode == 0
        and f"default via {expected_gateway}" in route_result.stdout
    )

    passed = ip_ok and gateway_ok

    test_result = TestResult(
        name=f"{namespace} network config",
        passed=passed,
        expected=f"{expected_ip}, gateway {expected_gateway}",
        actual=f"IP {'OK' if ip_ok else 'FAIL'}, Gateway {'OK' if gateway_ok else 'FAIL'}",
        details=f"Interface: {interface}"
    )

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_result.name}: {test_result.actual}")

    return test_result

def test_server_health():
    result = subprocess.run(
        [
            "ip", "netns", "exec", "server",
            "curl", "--max-time", "3",
            "-s", "-o", "/dev/null",
            "-w", "%{http_code}",
            "http://10.10.30.2:8080/"
        ],
        capture_output=True,
        text=True
    )

    http_code = result.stdout.strip()
    passed = result.returncode == 0 and http_code == "200"

    test_result = TestResult(
        name="Server HTTP health",
        passed=passed,
        expected="HTTP 200",
        actual=(
            "HTTP 200" if passed
            else f"HTTP {http_code or '000'}"
        ),
        details=f"curl exit code {result.returncode}"
    )

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_result.name}: {test_result.actual}")

    return test_result

def test_test_service_health():
    result = subprocess.run(
        [
            "ip", "netns", "exec", "server",
            "curl", "--max-time", "3",
            "-s", "-o", "/dev/null",
            "-w", "%{http_code}",
            "http://10.10.30.2:9090/"
        ],
        capture_output=True,
        text=True
    )

    http_code = result.stdout.strip()
    passed = result.returncode == 0 and http_code == "200"

    test_result = TestResult(
        name="Test service HTTP 9090 health",
        passed=passed,
        expected="HTTP 200",
        actual="HTTP 200" if passed else f"HTTP {http_code or '000'}",
        details=f"curl exit code {result.returncode}"
    )

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_result.name}: {test_result.actual}")

    return test_result

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

    http_code = result.stdout.strip()

    success = (
        result.returncode == 0
        and http_code == "200"
    )

    passed = success == expected_success

    expected = "HTTP 200" if expected_success else "blocked"

    if success:
        actual = "HTTP 200"
    elif result.returncode == 28:
        actual = "timeout"
    elif result.returncode == 0:
        actual = f"HTTP {http_code}"
    else:
        actual = f"curl error {result.returncode}"

    test_result = TestResult(
        name=f"{namespace} HTTP {url.rsplit(':', 1)[-1].split('/')[0]}",
        passed=passed,
        expected=expected,
        actual=actual,
        details=f"curl exit code {result.returncode}"
    )

    status = "PASS" if passed else "FAIL"

    print(f"[{status}] {test_result.name}: {actual}")

    return test_result

def run_validation():
    print("=== SecureNet Security Validation ===")

    url = "http://10.10.30.2:8080/"

    health = test_server_health()

    results = [health]

    if health.passed:
        results.extend([
            test_http("staff", url, True),
            test_http("guest", url, False)
        ])
    else:
        print("[SKIP] HTTP access tests: server is unhealthy")

    results.extend([
        test_network_config("staff", "veth-staff", "10.10.10.2/24", "10.10.10.1"),
        test_network_config("guest", "veth-guest", "10.10.20.2/24", "10.10.20.1"),
        test_network_config("server", "veth-server", "10.10.30.2/24", "10.10.30.1"),
        test_ip_forwarding(), 
        test_ping("staff", "10.10.30.2", False),
        test_ping("guest", "10.10.30.2", False),
        test_firewall_rules()
    ])

    test_service = test_test_service_health()
    results.append(test_service)

    if test_service.passed:
        results.append(
            test_http("staff", "http://10.10.30.2:9090/", False)
        )
    else:
        print("[SKIP] Staff HTTP 9090: test service is unhealthy")

    passed = sum(result.passed for result in results)
    total = len(results)

    print(f"\nResult: {passed}/{total} executed tests passed")

    save_json_report(results)

    return health.passed and passed == total

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

    expected = "reachable" if expected_success else "blocked"
    actual = "reachable" if success else "unreachable"

    test_result = TestResult(
        name=f"{namespace} ICMP",
        passed=passed,
        expected=expected,
        actual=actual,
        details=f"ping exit code {result.returncode}"
    )

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_result.name}: {actual}")

    return test_result

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

    required_rules = [
        "policy drop",
        "ct state established,related accept",
        "tcp dport 8080"
    ]

    missing_rules = []

    for rule in required_rules:
        if rule not in rules:
            missing_rules.append(rule)

    passed = result.returncode == 0 and not missing_rules

    test_result = TestResult(
        name="Firewall rules",
        passed=passed,
        expected="required rules present",
        actual="rules verified" if passed else "missing or invalid rules",
        details=(
            "All required rules found"
            if passed
            else f"Missing rules: {missing_rules}; nft exit code {result.returncode}"
        )
    )

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_result.name}: {test_result.actual}")

    return test_result
