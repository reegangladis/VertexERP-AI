"""Server-Side Request Forgery (SSRF) Protection and URL Validation Engine."""

from __future__ import annotations

import ipaddress
import logging
import socket
from urllib.parse import urlparse

logger = logging.getLogger("vertexerp.security.ssrf")

# Forbidden IPv4 networks: Private, Loopback, Link-Local, Carrier NAT, Cloud Metadata
FORBIDDEN_IPV4_NETWORKS = [
    ipaddress.IPv4Network("0.0.0.0/8"),  # Current network
    ipaddress.IPv4Network("10.0.0.0/8"),  # Private RFC 1918
    ipaddress.IPv4Network("100.64.0.0/10"),  # Shared Address Space (Carrier NAT)
    ipaddress.IPv4Network("127.0.0.0/8"),  # Loopback
    ipaddress.IPv4Network("169.254.0.0/16"),  # Link-local / Cloud Metadata (AWS, GCP, Azure)
    ipaddress.IPv4Network("172.16.0.0/12"),  # Private RFC 1918
    ipaddress.IPv4Network("192.0.0.0/24"),  # IETF Protocol Assignments
    ipaddress.IPv4Network("192.0.2.0/24"),  # TEST-NET-1
    ipaddress.IPv4Network("192.88.99.0/24"),  # 6to4 Relay Anycast
    ipaddress.IPv4Network("192.168.0.0/16"),  # Private RFC 1918
    ipaddress.IPv4Network("198.18.0.0/15"),  # Network Benchmark Tests
    ipaddress.IPv4Network("198.51.100.0/24"),  # TEST-NET-2
    ipaddress.IPv4Network("203.0.113.0/24"),  # TEST-NET-3
    ipaddress.IPv4Network("224.0.0.0/4"),  # Multicast
    ipaddress.IPv4Network("240.0.0.0/4"),  # Reserved for Future Use
    ipaddress.IPv4Network("255.255.255.255/32"),  # Limited Broadcast
]

# Forbidden IPv6 networks
FORBIDDEN_IPV6_NETWORKS = [
    ipaddress.IPv6Network("::/128"),  # Unspecified
    ipaddress.IPv6Network("::1/128"),  # Loopback
    ipaddress.IPv6Network("::ffff:0:0/96"),  # IPv4-mapped IPv6
    ipaddress.IPv6Network("64:ff9b::/96"),  # IPv4/IPv6 translation
    ipaddress.IPv6Network("100::/64"),  # Discard prefix
    ipaddress.IPv6Network("2001::/23"),  # IETF Protocol Assignments
    ipaddress.IPv6Network("2001:db8::/32"),  # Documentation
    ipaddress.IPv6Network("fc00::/7"),  # Unique Local Address (ULA)
    ipaddress.IPv6Network("fe80::/10"),  # Link-local Unicast
    ipaddress.IPv6Network("ff00::/8"),  # Multicast
]

# Explicitly blocked hostnames (Cloud metadata and internal services)
BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
    "metadata.internal",
    "instance-data",
    "169.254.169.254",
    "kubernetes.default.svc",
    "vault",
    "redis",
    "db",
    "postgres",
}


class SSRFProtectionError(ValueError):
    """Raised when an outbound URL violates SSRF safety policy."""

    pass


def is_ip_allowed(ip_str: str) -> bool:
    """Verifies that an IP address is a public, routable IP address not in any private/internal range."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False

    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        return False

    if isinstance(ip, ipaddress.IPv4Address):
        for net in FORBIDDEN_IPV4_NETWORKS:
            if ip in net:
                return False
    elif isinstance(ip, ipaddress.IPv6Address):
        for v6_net in FORBIDDEN_IPV6_NETWORKS:
            if ip in v6_net:
                return False

    return True


def validate_outbound_url(
    url: str,
    allow_http: bool = False,
    allow_localhost_for_testing: bool = False,
) -> str:
    """
    Validates that a URL is safe for outbound HTTP/HTTPS requests.
    Prevents SSRF attacks against internal network endpoints, link-local metadata services,
    and forbidden protocols.

    Raises SSRFProtectionError if the URL violates safety constraints.
    Returns the validated, normalized URL.
    """
    if not url or not isinstance(url, str):
        raise SSRFProtectionError("URL cannot be empty.")

    try:
        parsed = urlparse(url.strip())
    except Exception as exc:
        raise SSRFProtectionError(f"Invalid URL format: {exc}") from exc

    # Scheme validation
    allowed_schemes = {"https"} if not allow_http else {"http", "https"}
    if parsed.scheme.lower() not in allowed_schemes:
        raise SSRFProtectionError(
            f"Invalid URL scheme '{parsed.scheme}'. Only {list(allowed_schemes)} are permitted."
        )

    hostname = parsed.hostname
    if not hostname:
        raise SSRFProtectionError("URL must include a valid hostname.")

    hostname_lower = hostname.lower()

    # Blocked hostnames check
    if not allow_localhost_for_testing and (
        hostname_lower in BLOCKED_HOSTNAMES or hostname_lower.endswith(".internal")
    ):
        raise SSRFProtectionError(f"Requests to internal hostname '{hostname}' are forbidden.")

    # Check if hostname is directly an IP literal
    try:
        direct_ip = ipaddress.ip_address(hostname_lower)
        if not allow_localhost_for_testing and not is_ip_allowed(str(direct_ip)):
            raise SSRFProtectionError(f"Requests to private/reserved IP '{direct_ip}' are blocked.")
        return url
    except ValueError:
        pass  # Hostname is a domain name, resolve DNS

    # Resolve hostname via DNS and inspect all resolved addresses
    try:
        addr_info = socket.getaddrinfo(
            hostname, parsed.port or (443 if parsed.scheme == "https" else 80)
        )
    except socket.gaierror as exc:
        raise SSRFProtectionError(f"Could not resolve host '{hostname}': {exc}") from exc

    if not addr_info:
        raise SSRFProtectionError(f"Host '{hostname}' resolved to no IP addresses.")

    for _family, _, _, _, sockaddr in addr_info:
        ip_addr = str(sockaddr[0])
        if not allow_localhost_for_testing and not is_ip_allowed(ip_addr):
            logger.warning(
                "SSRF block: Hostname '%s' resolved to forbidden internal IP '%s'",
                hostname,
                ip_addr,
            )
            raise SSRFProtectionError(
                f"Destination host '{hostname}' resolved to forbidden internal IP address '{ip_addr}'."
            )

    return url
