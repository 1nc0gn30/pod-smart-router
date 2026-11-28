"""POD Smart Router - High-Performance Threaded HTTP Server (Port 8117)
Zero-dependency Python 3.10+ Standard Library HTTP & Static Server
"""

from typing import Optional
import http.server
import json
import os
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Dict, Any

from .catalog_matrix import CATALOG_MATRIX, get_all_products
from .router import SmartRouter, RoutingDecision
from .payload_gen import DispatchPayloadGenerator
from .partner_client import PartnerClient


def _is_local_origin(origin) -> bool:
    """Browser Origin check. No Origin header = non-browser client (CLI/agent): allowed.
    Otherwise only http(s)://localhost / 127.0.0.1 / [::1] pages may call this API, so a
    random website can't drive the local server from the user's browser (CSRF)."""
    if not origin:
        return True
    from urllib.parse import urlparse
    try:
        u = urlparse(origin)
    except ValueError:
        return False
    return u.scheme in ("http", "https") and u.hostname in ("localhost", "127.0.0.1", "::1")


def _cors_origin(handler) -> str:
    origin = handler.headers.get("Origin")
    return origin if origin and _is_local_origin(origin) else "http://127.0.0.1"



def _default_bind_host() -> str:
    """Bind address: localhost unless explicitly opted in via $ZOTH_BIND_HOST or
    $HOST (IP literal only; zsh sets HOST to the hostname) or --host."""
    import ipaddress, os
    for var in ("ZOTH_BIND_HOST", "HOST"):
        val = os.environ.get(var, "").strip()
        if val == "localhost":
            return "127.0.0.1"
        if val:
            try:
                ipaddress.ip_address(val)
                return val
            except ValueError:
                pass
    return "127.0.0.1"


PORT = int(os.environ.get("POD_ROUTER_PORT", 8117))
START_TIME = time.time()

_TRUSTED_HOSTS = ("127.0.0.1", "localhost", "::1")
_MAX_BODY_BYTES = 1_048_576  # 1 MiB cap on JSON request bodies.


class _BadRequest(Exception):
    """Malformed request (bad Content-Length or JSON body) → HTTP 400."""


class _BodyTooLarge(Exception):
    """Oversized request body → HTTP 413."""


def _is_trusted_host(value) -> bool:
    """True only for loopback Host headers (DNS-rebinding guard)."""
    if not value:
        return False
    host = str(value).split("@")[-1].split(",")[0].strip()
    if host.startswith("["):
        hostname = host[1:].split("]")[0]
    else:
        try:
            import ipaddress as _ip
            return _ip.ip_address(host).is_loopback
        except ValueError:
            hostname = host.split(":")[0].strip().lower()
    return hostname in _TRUSTED_HOSTS


def _parse_int(value, default, minimum=None, maximum=None, name="parameter"):
    """Bounded int parsing (raises _BadRequest on garbage)."""
    if value is None or value == "":
        return default
    try:
        number = int(value)
    except (ValueError, TypeError):
        raise _BadRequest(f"Invalid {name}: must be an integer")
    if minimum is not None:
        number = max(number, minimum)
    if maximum is not None:
        number = min(number, maximum)
    return number


def _parse_float(value, default, minimum=None, maximum=None, name="parameter"):
    """Bounded float parsing (raises _BadRequest on garbage)."""
    if value is None or value == "":
        return default
    try:
        number = float(value)
    except (ValueError, TypeError):
        raise _BadRequest(f"Invalid {name}: must be a number")
    if minimum is not None:
        number = max(number, minimum)
    if maximum is not None:
        number = min(number, maximum)
    return number

TELEMETRY = {
    "routes_evaluated": 0,
    "cumulative_savings_usd": 0.0,
    "cumulative_carbon_miles_saved": 0.0,
    "cumulative_days_saved": 0,
    "gelato_wins": 0,
    "printify_wins": 0,
    "customs_incidents_prevented": 0
}

PUBLIC_DIR = Path(__file__).resolve().parent.parent.parent / "public"

class SmartRouterHandler(http.server.SimpleHTTPRequestHandler):
    """Zero-dependency HTTP Handler for POD Smart Router API and Web UI."""

    server_version = "POD-Router"
    sys_version = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def _deny_non_loopback_host(self) -> bool:
        """Reject DNS-rebinding style Host headers with 403. True when denied."""
        if not _is_trusted_host(self.headers.get("Host", "")):
            self._send_json({"error": "Forbidden: non-loopback Host header"}, status=403)
            return True
        return False

    def _send_security_headers(self) -> None:
        """Loopback-hardened security headers on every response.

        No X-Frame-Options on purpose: it cannot express an allowlist and
        SAMEORIGIN would break the first-party Studio embed on :3000. The
        CSP frame-ancestors allowlist below is the enforced policy.
        """
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        # NOTE: script/style 'unsafe-inline' covers this page's own first-party
        # init script + presentational attributes (audited: no eval, no remote
        # code, no external fetches — all scripts same-origin, all links plain
        # anchors, no webfonts).
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: blob:; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "connect-src 'self' http://127.0.0.1:* http://localhost:*; "
            "frame-ancestors 'self' http://127.0.0.1:3000 http://localhost:3000 http://127.0.0.1:* http://localhost:*; "
            "base-uri 'self'; "
            "object-src 'none'",
        )

    def end_headers(self) -> None:
        self._send_security_headers()
        super().end_headers()

    def _read_json_body(self) -> Dict[str, Any]:
        """Read and parse JSON request body (1 MiB cap; errors raise)."""
        raw_len = (self.headers.get("Content-Length", "0") or "0").split(",")[0].strip()
        try:
            content_len = int(raw_len) if raw_len else 0
        except ValueError:
            raise _BadRequest("Invalid Content-Length")
        if content_len < 0:
            raise _BadRequest("Invalid Content-Length")
        if content_len > _MAX_BODY_BYTES:
            raise _BodyTooLarge("Payload Too Large")
        if content_len == 0:
            return {}
        try:
            data = json.loads(self.rfile.read(content_len).decode("utf-8", errors="replace"))
        except json.JSONDecodeError as e:
            raise _BadRequest(f"Invalid JSON payload: {e}")
        return data if isinstance(data, dict) else {}

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", _cors_origin(self))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        if self._deny_non_loopback_host():
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", _cors_origin(self))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self):
        if self._deny_non_loopback_host():
            return
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path in ("/health", "/api/health"):
            self._send_json({
                "status": "healthy",
                "service": "pod-smart-router",
                "version": "1.0.0",
                "port": PORT,
                "uptime_seconds": round(time.time() - START_TIME, 1),
                "partners": {
                    "printify": "active" if PartnerClient.ping_printify() else "catalog_matrix_active",
                    "gelato": "active" if PartnerClient.ping_gelato() else "catalog_matrix_active"
                }
            })
            return

        if path == "/api/stats":
            total = TELEMETRY["routes_evaluated"]
            gelato_pct = round((TELEMETRY["gelato_wins"] / total * 100), 1) if total > 0 else 50.0
            printify_pct = round((TELEMETRY["printify_wins"] / total * 100), 1) if total > 0 else 50.0
            self._send_json({
                "telemetry": TELEMETRY,
                "partner_split": {
                    "printify_percentage": printify_pct,
                    "gelato_percentage": gelato_pct
                },
                "uptime_seconds": round(time.time() - START_TIME, 1)
            })
            return

        if path == "/api/catalog/matrix":
            catalog = get_all_products()
            self._send_json({
                "count": len(catalog),
                "products": catalog,
                "coverage": {
                    "gelato_local_countries": 32,
                    "printify_print_providers": 90,
                    "supported_destinations": ["US", "CA", "GB", "DE", "FR", "IT", "ES", "AU", "NZ", "JP", "NL", "SE", "GLOBAL"]
                }
            })
            return

        if path == "/api/rules":
            self._send_json({
                "rules": [
                    {
                        "id": "cheapest",
                        "label": "Maximum Margin (Lowest Landed Cost)",
                        "description": "Selects the partner with lowest total wholesale base cost + shipping + import duties."
                    },
                    {
                        "id": "fastest",
                        "label": "Fast Track (Quickest Delivery)",
                        "description": "Prioritizes local production to deliver to customer door in minimum transit days."
                    },
                    {
                        "id": "balanced",
                        "label": "Balanced Sovereign (Recommended)",
                        "description": "Optimizes cost while guaranteeing domestic delivery (<5 days) and 0 customs duty."
                    },
                    {
                        "id": "domestic_only",
                        "label": "100% Domestic Local Only",
                        "description": "Strictly enforces localized print lab within destination country; eliminates cross-border logistics."
                    },
                    {
                        "id": "customs_avoidance",
                        "label": "Zero Customs Duty Lock",
                        "description": "Guarantees zero customer tariffs or clearance fees at customs."
                    }
                ]
            })
            return

        if path == "/api/savings":
            try:
                monthly_orders = _parse_int(query.get("monthly_orders", ["100"])[0], 100, 1, 10_000_000, "monthly_orders")
                avg_savings = _parse_float(query.get("avg_savings", ["3.40"])[0], 3.40, 0, 1e9, "avg_savings")
            except _BadRequest as e:
                self._send_json({"error": str(e)}, status=400)
                return
            annual_savings = monthly_orders * avg_savings * 12
            tool_cost = 19.00
            roi_days = round((tool_cost / (monthly_orders * avg_savings / 30.0)), 1)
            self._send_json({
                "monthly_orders": monthly_orders,
                "projected_monthly_savings_usd": round(monthly_orders * avg_savings, 2),
                "projected_annual_savings_usd": round(annual_savings, 2),
                "license_cost_usd": tool_cost,
                "payback_period_days": roi_days,
                "roi_percentage_year_1": round(((annual_savings - tool_cost) / tool_cost) * 100, 1)
            })
            return

        # Fallback to static files
        super().do_GET()

    def do_POST(self):
        if self._deny_non_loopback_host():
            return
        if not _is_local_origin(self.headers.get("Origin")):
            _body = b'{"error": "cross-origin request blocked"}'
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(_body)))
            self.end_headers()
            self.wfile.write(_body)
            return
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            payload = self._read_json_body()
        except _BodyTooLarge as e:
            self._send_json({"error": str(e)}, status=413)
            return
        except _BadRequest as e:
            self._send_json({"error": str(e)}, status=400)
            return

        if path == "/api/route":
            sku = payload.get("sku") or payload.get("product_id", "gildan_18000")
            dest = payload.get("destination_country", "US")
            try:
                qty = _parse_int(payload.get("quantity", 1), 1, 1, 100_000, "quantity")
            except _BadRequest as e:
                self._send_json({"error": str(e)}, status=400)
                return
            rule = payload.get("rule") or payload.get("priority", "balanced")
            premium = bool(payload.get("printify_premium", True))

            try:
                decision = SmartRouter.route(
                    sku=sku,
                    destination_country=dest,
                    quantity=qty,
                    rule=rule,
                    printify_premium=premium
                )

                TELEMETRY["routes_evaluated"] += 1
                TELEMETRY["cumulative_savings_usd"] += decision.dollar_savings
                TELEMETRY["cumulative_carbon_miles_saved"] += decision.carbon_miles_saved
                TELEMETRY["cumulative_days_saved"] += decision.days_saved
                if decision.recommended_partner == "gelato":
                    TELEMETRY["gelato_wins"] += 1
                else:
                    TELEMETRY["printify_wins"] += 1
                if decision.winner_quote.customs_risk_level.startswith("ZERO"):
                    TELEMETRY["customs_incidents_prevented"] += 1

                self._send_json({
                    "decision": decision.to_dict(),
                    "status": "success"
                })
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        if path == "/api/dispatch":
            sku = payload.get("sku") or payload.get("product_id", "gildan_18000")
            dest = payload.get("destination_country", "US")
            try:
                qty = _parse_int(payload.get("quantity", 1), 1, 1, 100_000, "quantity")
            except _BadRequest as e:
                self._send_json({"error": str(e)}, status=400)
                return
            rule = payload.get("rule") or payload.get("priority", "balanced")
            premium = bool(payload.get("printify_premium", True))
            address = payload.get("customer_address", {})
            artwork_url = payload.get("artwork_url")
            ext_order_id = payload.get("external_order_id")

            try:
                decision = SmartRouter.route(
                    sku=sku,
                    destination_country=dest,
                    quantity=qty,
                    rule=rule,
                    printify_premium=premium
                )

                dispatch_payload = DispatchPayloadGenerator.generate(
                    decision=decision,
                    customer_address=address,
                    artwork_url=artwork_url,
                    external_order_id=ext_order_id
                )

                TELEMETRY["routes_evaluated"] += 1
                TELEMETRY["cumulative_savings_usd"] += decision.dollar_savings
                TELEMETRY["cumulative_carbon_miles_saved"] += decision.carbon_miles_saved
                TELEMETRY["cumulative_days_saved"] += decision.days_saved
                if decision.recommended_partner == "gelato":
                    TELEMETRY["gelato_wins"] += 1
                else:
                    TELEMETRY["printify_wins"] += 1

                self._send_json({
                    "decision": decision.to_dict(),
                    "dispatch_payload": dispatch_payload,
                    "status": "ready_for_transmission"
                })
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        self._send_json({"error": f"Endpoint not found: {path}"}, status=404)

def run_server(port: int = PORT, host: Optional[str] = None):
    host = host or _default_bind_host()
    server_address = (host, port)
    httpd = http.server.ThreadingHTTPServer(server_address, SmartRouterHandler)
    print(f"🚀 POD Smart Router listening on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down POD Smart Router gracefully...")
        httpd.server_close()

if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser(description="Run the HTTP server and web UI")
    _ap.add_argument("--host", default=None, help="Host interface (default: 127.0.0.1 or $ZOTH_BIND_HOST; use 0.0.0.0 only on trusted networks)")
    _ap.add_argument("--port", type=int, default=PORT)
    _a = _ap.parse_args()
    run_server(port=_a.port, host=_a.host)
