from netlab.network import (
    add_default_route,
    enable_ip_forwarding,
)

add_default_route("staff", "10.10.10.1")
add_default_route("server", "10.10.30.1")

enable_ip_forwarding()
