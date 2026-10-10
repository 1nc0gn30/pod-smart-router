"""REST Client connecting to local Printify (:8115) and Gelato (:8116) connectors.

Gracefully falls back to normalized catalog matrix if connectors are offline.
100% Python Standard Library.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

logger = logging.getLogger("pod_smart_router.partner_client")

PRINTIFY_PORT = 8115
GELATO_PORT = 8116


def is_printify_online(timeout: float = 0.5) -> bool:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{PRINTIFY_PORT}/health")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def is_gelato_online(timeout: float = 0.5) -> bool:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{GELATO_PORT}/health")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def query_printify_catalog(timeout: float = 1.0) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{PRINTIFY_PORT}/api/catalog")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.debug("Printify catalog query skipped: %s", e)
    return None


def query_gelato_catalog(timeout: float = 1.0) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{GELATO_PORT}/api/catalog")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.debug("Gelato catalog query skipped: %s", e)
    return None


class PartnerClient:
    """Convenience wrapper for partner status and queries."""
    @staticmethod
    def ping_printify() -> bool:
        return is_printify_online()

    @staticmethod
    def ping_gelato() -> bool:
        return is_gelato_online()

    @staticmethod
    def get_printify_catalog() -> Optional[Dict[str, Any]]:
        return query_printify_catalog()

    @staticmethod
    def get_gelato_catalog() -> Optional[Dict[str, Any]]:
        return query_gelato_catalog()

