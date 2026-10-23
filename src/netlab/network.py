import subprocess

ALLOWED_NAMESPACES = {"staff", "router", "server"}

def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout

    except subprocess.CalledProcessError as e:
        print("Command failed:", command)
        print("Error:", e.stderr)
        raise


def namespace_exists(name):
    output = run_command(["ip", "netns", "list"])
    
    for line in output.splitlines():
       namespace_name = line.split()[0]

       if namespace_name == name:
           return True

    return False

def validate_namespace(name):
    if name not in ALLOWED_NAMESPACES:
        raise ValueError(f"Namespace '{name}' is not managed by this lab.")


def create_namespace(name):
    validate_namespace(name)

    if namespace_exists(name):
        print(f"Namespace '{name}' already exists.")
        return

    run_command(["ip", "netns", "add", name])
    print(f"NameSpace '{name}' created.")

def delete_namespace(name):
    validate_namespace(name)

    if not namespace_exists(name):
        print(f"Namespace '{name}' does not exist.")
        return

    run_command(["ip", "netns", "del", name])
    print(f"NameSpace '{name}' deleted.")

def create_veth_pair(interface_a, interface_b):
    run_command(["ip", "link", "add", interface_a, "type", "veth", "peer", "name", interface_b])
    print(f"Created veth pair: {interface_a} <-> {interface_b}")

def move_interface(interface, namespace):
    validate_namespace(namespace)

    run_command(["ip", "link", "set", interface, "netns", namespace])

    print(f"Moved {interface} into {namespace}")

def assign_ip(namespace, interface, ip_address):
    validate_namespace(namespace)
    
    run_command(["ip", "netns", "exec", namespace, "ip", "addr", "add", ip_address, "dev", interface])

    print(f"Assigned {ip_address} to {interface} in {namespace}")

def set_interface_up(namespace, interface):
    validate_namespace(namespace)

    run_command(["ip", "netns", "exec", namespace, "ip", "link", "set", interface, "up"])

    print(f"Interface {interface} is UP in {namespace}")

def add_default_route(namespace, gateway):
    validate_namespace(namespace)
    
    run_command(["ip", "netns", "exec", namespace, "ip", "route", "replace", "default", "via", gateway])

    print(f"Default gateway for {namespace}: {gateway}")

def enable_ip_forwarding():
    run_command(["ip", "netns", "exec", "router", "sysctl", "-w", "net.ipv4.ip_forward=1"])

    print("IPv4 forwarding enabled in router") 
def setup_network():
    existing = []

    for name in ["staff", "router", "server"]:
        if namespace_exists(name):
            existing.append(name)
    
    if existing:
        raise RuntimeError(
            f"Cannot start: existing namespaces found: {existing}"
    )
    print("=== Setting up SecureNet Lab ===")

    create_namespace("staff")
    create_namespace("router")
    create_namespace("server")

    create_veth_pair("veth-staff", "veth-rstaff")
    create_veth_pair("veth-server", "veth-rserver")

    move_interface("veth-staff", "staff")
    move_interface("veth-rstaff", "router")
    move_interface("veth-server", "server")
    move_interface("veth-rserver", "router")

    assign_ip("staff", "veth-staff", "10.10.10.2/24")
    assign_ip("router", "veth-rstaff", "10.10.10.1/24")
    assign_ip("server", "veth-server", "10.10.30.2/24")
    assign_ip("router", "veth-rserver", "10.10.30.1/24")

    set_interface_up("staff", "veth-staff")
    set_interface_up("router", "veth-rstaff")
    set_interface_up("server", "veth-server")
    set_interface_up("router", "veth-rserver")

    add_default_route("staff", "10.10.10.1")
    add_default_route("server", "10.10.30.1")

    enable_ip_forwarding()

    print("=== SecureNet Lab setup complete ===")

def show_status():
    print("=== SecureNet Lab Status ===")

    for name in ["staff", "router", "server"]:
        if namespace_exists(name):
            print(f"{name}: EXISTS")
        else:
            print(f"{name}: MISSING")

def teardown_network():
    print("=== Tearing down SecureNet Lab ===")
    
    expected_interfaces = {
        "staff": ["veth-staff"],
        "router": ["veth-rstaff", "veth-rserver"],
        "server": ["veth-server"],
    }

    for namespace, interfaces in expected_interfaces.items():
        if not namespace_exists(namespace):
            print(f"{namespace}: MISSING")
            return

        for interface in interfaces:
            run_command([
                "ip", "netns", "exec", namespace,
                "ip", "link", "show", interface
            ])
   
    print("Preflight checks passed.")

    confirmation = input("Delete SecureNet Lab namespaces? [y/N]: ")

    if confirmation.lower() != "y":
        print("Teardown cancelled.")
        return

    for namespace in ["staff", "server", "router"]:
        delete_namespace(namespace)

    print("=== SecureNet Lab teardown complete ===")
