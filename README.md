
# SecureNet Lab

A Python-based network segmentation and security automation lab built on Linux.

## Project Overview

SecureNet Lab is a hands-on networking project designed to simulate a small office network using Linux network namespaces.

The project aims to automate network configuration, routing, firewall policies, and connectivity testing.

## Planned Features

- Virtual network topology using Linux network namespaces
- IP addressing and routing configuration
- Network segmentation between Staff, Guest, and Server
- Firewall policies using nftables
- Python-based network automation
- Automated connectivity and security testing

## Technology Stack

- Ubuntu Server 24.04 LTS
- Python 3
- Linux iproute2
- nftables
- Git

## Project Status

Milestone 0: Environment setup and project initialization.

## Development Roadmap

- M0: Environment and Git setup
- M1: Virtual network topology
- M2: Python network automation
- M3: Firewall and security policies
- M4: Automated testing and reporting
- M5: Documentation and portfolio release


## Project Progress

- [x] M0 — Ubuntu development environment and GitHub repository setup
- [x] M1 — Manual network namespaces, veth connectivity, IPv4 routing and packet analysis
- [ ] M2 — Python-based network provisioning and CLI
- [ ] M3 — Firewall and network segmentation policies
- [ ] M4 — Automated network validation and reporting
- [ ] M5 — Documentation, testing and CI improvements

## Current Network Topology

The current lab contains three isolated Linux network namespaces: Staff, Router and Server.

Staff (`10.10.10.2/24`) communicates with Server (`10.10.30.2/24`) through a Router namespace with IPv4 forwarding enabled.

See [Network Architecture](docs/architecture.md) and [Troubleshooting](docs/troubleshooting.md) for implementation details and validation results.

**Note:** The topology is currently configured manually. Python automation will be introduced in Milestone 2.
