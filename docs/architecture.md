# Network Architecture — Milestone 1

## Overview

This project uses Linux network namespaces and virtual Ethernet (veth) pairs to simulate a small routed office network within a single Ubuntu Server virtual machine.

Each namespace has an isolated network stack, including its own interfaces, IP addresses, routing table and neighbour table. All namespaces share the same Linux kernel.

## Network Topology

```text
Staff Namespace           Router Namespace          Server Namespace
10.10.10.2/24             10.10.10.1/24             10.10.30.2/24
      |                    10.10.30.1/24                    |
      |                          |                          |
  veth-staff -------- veth-rstaff                  veth-rserver -------- veth-server
                            [ Router ]
```

The router namespace connects two separate IPv4 subnets:

- Staff network: `10.10.10.0/24`
- Server network: `10.10.30.0/24`

The Staff namespace uses `10.10.10.1` as its default gateway, while the Server namespace uses `10.10.30.1`.

IPv4 forwarding is enabled inside the Router namespace to allow communication between the two subnets.

## Technologies

- Ubuntu Server 24.04 ARM64
- Linux network namespaces (`ip netns`)
- Virtual Ethernet interfaces (`veth`)
- IPv4 addressing and routing
- ARP / neighbour discovery
- ICMP and `tcpdump`

## Validation

Connectivity was verified by sending ICMP Echo Requests from Staff (`10.10.10.2`) to Server (`10.10.30.2`), with four packets transmitted and four received.

Routing inspection confirmed that Staff forwards traffic for `10.10.30.2` through its default gateway, `10.10.10.1`.

Packet captures on both router interfaces showed the expected TTL decrement during IPv4 forwarding.

## Scope and Limitations

This milestone demonstrates a manually configured virtual routed network. It does not yet implement firewall rules, network segmentation policies, or automated provisioning.

Network namespaces are used to emulate separate network hosts and routing domains; they are not physical VLANs.
