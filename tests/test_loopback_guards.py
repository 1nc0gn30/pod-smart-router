"""Loopback Host guard, security headers, body-cap, and numeric-validation
regression tests for the POD Smart Router server (audit #071)."""
import http.client
import json
import socket
import threading
import time
import unittest
from http.server import ThreadingHTTPServer

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pod_smart_router.server import SmartRouterHandler, _is_trusted_host, _parse_float, _parse_int, _BadRequest


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestLoopbackGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = _free_port()
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", cls.port), SmartRouterHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _raw(self, method, path, host, body=None, extra_headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        headers = {"Host": host, "Connection": "close"}
        if extra_headers:
            headers.update(extra_headers)
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        conn.close()
        return resp.status, {k.lower(): v for k, v in resp.getheaders()}, data

    def test_trusted_hosts(self):
        for h in ("127.0.0.1", "127.0.0.1:8117", "localhost", "localhost:3000", "127.0.0.1:1", "[::1]:8117"):
            self.assertTrue(_is_trusted_host(h), h)
        for h in ("", "evil.example.invalid", "127.0.0.1.evil.com", "example.com", "192.168.1.50"):
            self.assertFalse(_is_trusted_host(h), h)

    def test_evil_host_rejected(self):
        status, _, _ = self._raw("GET", "/health", "evil.example.invalid")
        self.assertEqual(status, 403)
        status, _, _ = self._raw(
            "POST", "/api/route", "evil.example.invalid",
            body=b"{}", extra_headers={"Content-Type": "application/json"},
        )
        self.assertEqual(status, 403)

    def test_security_headers_and_banner(self):
        import urllib.request
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/health", timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get("X-Content-Type-Options"), "nosniff")
            self.assertIn("strict-origin", resp.headers.get("Referrer-Policy") or "")
            csp = resp.headers.get("Content-Security-Policy") or ""
            self.assertIn("frame-ancestors", csp)
            self.assertIn("http://127.0.0.1:3000", csp)
            self.assertTrue(resp.headers.get("Server", "").startswith("POD-Router"))
            self.assertNotIn("Python", resp.headers.get("Server", ""))

    def test_health_alias(self):
        import urllib.request
        for path in ("/health", "/api/health"):
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode())
                self.assertEqual(data["service"], "pod-smart-router")

    def test_body_cap_enforced(self):
        big = b"x" * (1_048_576 + 8)
        status, _, _ = self._raw(
            "POST", "/api/route", "127.0.0.1",
            body=big, extra_headers={"Content-Type": "application/json"},
        )
        self.assertEqual(status, 413)

    def test_bad_numerics_rejected(self):
        cases = [
            ("POST", "/api/route", {"quantity": "notanint"}),
            ("POST", "/api/dispatch", {"quantity": "xx"}),
            ("GET", "/api/savings?monthly_orders=abc", None),
        ]
        for method, path, payload in cases:
            body = json.dumps(payload).encode() if payload is not None else None
            headers = {"Content-Type": "application/json"} if body else None
            status, _, body_bytes = self._raw(method, path, "127.0.0.1", body, headers)
            self.assertEqual(status, 400, (method, path, payload))
            self.assertIn(b"error", body_bytes)

    def test_traversal_rooted(self):
        status, _, body = self._raw("GET", "/%2e%2e/%2e%2e/etc/hostname", "127.0.0.1")
        self.assertIn(status, (200, 403, 404))
        self.assertNotIn(b"root:", body)

    def test_parse_bounds(self):
        self.assertEqual(_parse_float("12.5", 0, 0, 100, "x"), 12.5)
        self.assertEqual(_parse_float("999", 0, 0, 100, "x"), 100)
        self.assertEqual(_parse_int("50", 0, 0, 100, "x"), 50)
        with self.assertRaises(_BadRequest):
            _parse_float("abc", 0, 0, 100, "x")
        with self.assertRaises(_BadRequest):
            _parse_int("abc", 0, 0, 100, "x")


if __name__ == "__main__":
    unittest.main()
