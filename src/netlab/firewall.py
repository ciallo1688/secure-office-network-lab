from netlab.network import run_command


def firewall_exists():
    result = run_command([
        "ip", "netns", "exec", "router",
        "nft", "list", "tables"
    ])

    return "table inet filter" in result

def setup_firewall():
    if firewall_exists():
        raise RuntimeError("SecureNet firewall table already exists.")

    print("=== Setting up SecureNet Firewall ===")

    run_command([
        "ip", "netns", "exec", "router",
        "nft", "add", "table", "inet", "filter"
    ])

    run_command([
        "ip", "netns", "exec", "router",
        "nft", "add", "chain", "inet", "filter", "forward",
        "{ type filter hook forward priority 0; policy drop; }"
    ])

    run_command([
        "ip", "netns", "exec", "router",
        "nft", "add", "rule", "inet", "filter", "forward",
        "ct", "state", "established,related", "accept"
    ])

    run_command([
        "ip", "netns", "exec", "router",
        "nft", "add", "rule", "inet", "filter", "forward",
        "ip", "saddr", "10.10.10.0/24",
        "ip", "daddr", "10.10.30.2",
        "tcp", "dport", "8080",
        "ct", "state", "new",
        "accept"
    ])

    print("=== SecureNet Firewall setup complete ===")
