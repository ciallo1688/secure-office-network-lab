# Secure Office Network Lab

A Python-based network automation and security lab built with Linux Network Namespaces, virtual Ethernet interfaces (veth), and nftables.

The project simulates a small enterprise network with three isolated network segments connected through a virtual router.

## Network Topology

```text
Staff (10.10.10.2/24) ──┐
                        │
Guest (10.10.20.2/24) ──┼── Router (nftables)
                        │
Server (10.10.30.2/24) ─┘
```

Each network segment has its own router interface and default gateway.

## Features

- Automated network namespace and veth creation
- IP addressing and routing configuration
- IPv4 forwarding
- Stateful firewall rules using nftables
- Default-deny network segmentation
- Staff access to Server TCP port 8080
- Guest-to-Server traffic blocked by the forwarding policy
- Automated security validation
- Duplicate setup detection and guarded teardown

## Security Policy

| Traffic | Action |
|---|---|
| Staff → Server TCP 8080 | ALLOW |
| Guest → Server TCP 8080 | DROP |
| Staff → Server ICMP | DROP |
| Guest → Server ICMP | DROP |
| Established/related traffic | ALLOW |
| Other unmatched forwarded traffic | DROP |

Firewall rules are applied inside the Router network namespace, not the Ubuntu host network namespace.

## Requirements

- Ubuntu Linux
- Python 3
- iproute2
- nftables
- curl
- Root privileges for network configuration

## Usage

Run commands from the project root using the configured Python virtual environment.

### Start the network

```bash
sudo env PYTHONPATH=src .venv/bin/python -m netlab.cli up
```

### Check network status

```bash
PYTHONPATH=src .venv/bin/python -m netlab.cli status
```

### Start a test HTTP server

In a separate terminal:

```bash
sudo ip netns exec server python3 -m http.server 8080 --bind 10.10.30.2 --directory /tmp
```

### Validate security policies

```bash
sudo env PYTHONPATH=src .venv/bin/python -m netlab.cli validate
```

### Tear down the network

Stop the test HTTP server, then run:

```bash
sudo env PYTHONPATH=src .venv/bin/python -m netlab.cli down
```

## Validation

The validation command currently checks:

1. Staff HTTP access to Server TCP 8080.
2. Guest HTTP access is denied.
3. Staff ICMP traffic is denied.
4. Guest ICMP traffic is denied.
5. Expected firewall rules are present.

Successful validation returns exit code 0; failed validation returns exit code 1.

The HTTP test server must be running for the HTTP validation tests. Rule inspection is currently based on text matching, and denied-connection tests alone cannot prove the cause of a connection failure.

## Limitations and Future Improvements

- Firewall setup is not yet transactional.
- Network teardown relies on namespace and interface checks rather than complete resource ownership tracking.
- HTTP service startup is currently manual.
- Security validation needs stronger checks for unexpected firewall rules and service health.
- Automated unit and integration tests are planned.

## Roadmap

- M0: Development environment — Complete
- M1: Manual network topology — Complete
- M2: Python network lifecycle automation — Complete
- M3: Firewall automation and security validation — Complete
- M4: Automated testing and reporting — Planned
- M5: Portfolio improvements and CI — Planned

## Environment

Developed and tested on Ubuntu 24.04 ARM64 running inside a UTM virtual machine.
