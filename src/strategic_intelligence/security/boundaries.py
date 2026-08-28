"""Deterministic boundaries for untrusted external research inputs."""

from __future__ import annotations

import ipaddress
import re
import socket
from enum import Enum
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class UrlSafetyCode(str, Enum):
    MALFORMED = "MALFORMED"
    UNSUPPORTED_SCHEME = "UNSUPPORTED_SCHEME"
    CREDENTIALS = "CREDENTIALS"
    INTERNAL_DESTINATION = "INTERNAL_DESTINATION"
    RESOLUTION_FAILED = "RESOLUTION_FAILED"


class UnsafeExternalUrlError(ValueError):
    """Raised before an unsafe external URL can reach a network boundary."""

    def __init__(self, code: UrlSafetyCode) -> None:
        super().__init__(f"external URL rejected: {code.value}")
        self.code = code


_INTERNAL_HOSTS = frozenset({"localhost", "metadata.google.internal"})
_INTERNAL_SUFFIXES = (".localhost", ".local", ".internal")
_HOST_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")


def normalize_external_url(value: str, *, preserve_fragment: bool = False) -> str:
    """Return a normalized public HTTP(S) URL or fail closed without fetching it."""

    if value != value.strip() or any(character.isspace() for character in value):
        raise UnsafeExternalUrlError(UrlSafetyCode.MALFORMED)
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeExternalUrlError(UrlSafetyCode.UNSUPPORTED_SCHEME)
    if not parsed.hostname:
        raise UnsafeExternalUrlError(UrlSafetyCode.MALFORMED)
    if parsed.username or parsed.password:
        raise UnsafeExternalUrlError(UrlSafetyCode.CREDENTIALS)
    try:
        port = parsed.port
    except ValueError as error:
        raise UnsafeExternalUrlError(UrlSafetyCode.MALFORMED) from error

    hostname = parsed.hostname.lower().rstrip(".")
    if not _has_valid_host_syntax(hostname):
        raise UnsafeExternalUrlError(UrlSafetyCode.MALFORMED)
    if _is_internal_hostname(hostname):
        raise UnsafeExternalUrlError(UrlSafetyCode.INTERNAL_DESTINATION)
    host_for_netloc = f"[{hostname}]" if ":" in hostname else hostname
    netloc = host_for_netloc if port is None else f"{host_for_netloc}:{port}"
    return urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "", parsed.query, parsed.fragment if preserve_fragment else ""))


def normalize_redirect_url(current_url: str, location: str) -> str:
    """Apply the external URL policy to every redirect destination."""

    return normalize_external_url(urljoin(current_url, location))


def validate_resolved_external_url(value: str) -> str:
    """Validate the addresses the owned network boundary is about to resolve."""

    normalized = normalize_external_url(value)
    parsed = urlsplit(normalized)
    try:
        destinations = socket.getaddrinfo(
            parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM,
        )
    except OSError as error:
        raise UnsafeExternalUrlError(UrlSafetyCode.RESOLUTION_FAILED) from error
    if not destinations:
        raise UnsafeExternalUrlError(UrlSafetyCode.RESOLUTION_FAILED)
    for destination in destinations:
        if _is_prohibited_address(destination[4][0]):
            raise UnsafeExternalUrlError(UrlSafetyCode.INTERNAL_DESTINATION)
    return normalized


def _is_internal_hostname(hostname: str) -> bool:
    if hostname in _INTERNAL_HOSTS or hostname.endswith(_INTERNAL_SUFFIXES):
        return True
    return _is_prohibited_address(hostname)


def _has_valid_host_syntax(hostname: str) -> bool:
    """Accept an IP literal or an ASCII DNS reg-name; reject encoded authority text."""

    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        pass
    if not hostname.isascii() or not hostname or len(hostname) > 253:
        return False
    return all(_HOST_LABEL.fullmatch(label) for label in hostname.split("."))


def _is_prohibited_address(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        try:
            # inet_aton recognizes resolver-supported numeric IPv4 spellings such as
            # decimal and hexadecimal integers without performing DNS resolution.
            address = ipaddress.ip_address(socket.inet_aton(value))
        except OSError:
            return False
    if address.version == 6 and address.ipv4_mapped is not None:
        return _is_prohibited_address(str(address.ipv4_mapped))
    return not (
        address.is_global
        and not address.is_loopback
        and not address.is_private
        and not address.is_link_local
        and not address.is_unspecified
        and not address.is_multicast
        and not address.is_reserved
    )


class _SafeRedirectHandler(HTTPRedirectHandler):
    """urllib redirect hook that prevents an initially safe URL from bypassing policy."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_resolved_external_url(urljoin(req.full_url, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_external_url(url: str, *, timeout: float):
    """Open one policy-validated public URL with policy-validated redirects."""

    normalized = validate_resolved_external_url(url)
    return build_opener(_SafeRedirectHandler()).open(normalized, timeout=timeout)


def open_external_request(request: Request, *, timeout: float):
    """Open one policy-validated external request, including redirect destinations."""

    validate_resolved_external_url(request.full_url)
    return build_opener(_SafeRedirectHandler()).open(request, timeout=timeout)
