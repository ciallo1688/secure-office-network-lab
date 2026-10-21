# Network Troubleshooting — Milestone 1

## 1. Interface Inspection

Inspect the network interfaces within a namespace:

```bash
sudo ip netns exec staff ip -br addr
sudo ip netns exec router ip -br addr
sudo ip netns exec server ip -br addr
```

Each virtual Ethernet interface should be UP and assigned to the correct subnet.

## 2. Routing Verification

Inspect the routing tables:

```bash
sudo ip netns exec staff ip route
sudo ip netns exec router ip route
sudo ip netns exec server ip route
```

Determine the selected route from Staff to Server:

```bash
sudo ip netns exec staff ip route get 10.10.30.2
```

Expected next hop: `10.10.10.1` via `veth-staff`.

## 3. ARP / Neighbour Inspection

```bash
sudo ip netns exec staff ip neigh
```

Staff resolves the MAC address of its directly connected gateway (`10.10.10.1`), rather than the remote Server (`10.10.30.2`).

A `STALE` neighbour entry does not necessarily indicate a connectivity problem.

## 4. ICMP Connectivity

```bash
sudo ip netns exec staff ping -c 4 10.10.30.2
```

Observed result: 4 packets transmitted, 4 received, 0% packet loss.

## 5. Packet Capture and TTL

Capture ICMP traffic on the router's Staff-facing interface:

```bash
sudo ip netns exec router tcpdump -ni veth-rstaff -vv icmp -c 4
```

Observed TTL values:

| Direction | TTL |
|---|---|
| Staff → Server | 64 |
| Server → Staff | 63 |

Capture on the Server-facing interface:

```bash
sudo ip netns exec router tcpdump -ni veth-rserver -vv icmp -c 4
```

Observed TTL values:

| Direction | TTL |
|---|---|
| Staff → Server | 63 |
| Server → Staff | 64 |

These captures demonstrate the TTL decrement performed by the router when forwarding IPv4 packets.

## 6. Common Issues

**Namespace not found**

Check namespace names using `ip netns list`. Namespace names must match exactly.

**Interface is DOWN**

Enable the interface inside the correct namespace:

```bash
sudo ip netns exec staff ip link set veth-staff up
```

**Cannot reach another subnet**

Check the default gateway, the router's connected routes, and IPv4 forwarding:

```bash
sudo ip netns exec router sysctl net.ipv4.ip_forward
```

**Neighbour entry shows STALE**

This is a normal neighbour-cache state. Test connectivity before assuming a failure.
