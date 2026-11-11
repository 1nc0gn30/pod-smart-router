"""POD Smart Router - Sovereign Command-Line Interface.

Zero-dependency Python standard library CLI.
"""

import argparse
import json
import sys
from .catalog_matrix import CATALOG_MATRIX, get_all_products
from .router import SmartRouter
from .payload_gen import DispatchPayloadGenerator
from .server import run_server


def cmd_status(host: str = "127.0.0.1", port: int = 8117, as_json: bool = False) -> int:
    import urllib.request
    url = f"http://{host}:{port}/health"
    live_info = None
    try:
        with urllib.request.urlopen(url, timeout=2.0) as resp:
            live_info = json.loads(resp.read().decode("utf-8"))
    except Exception:
        pass

    products = get_all_products()

    data = {
        "status": "online" if live_info else "standby",
        "service": "pod-smart-router",
        "version": "2.5.0",
        "port": port,
        "catalog_count": len(products),
        "supported_destinations": ["US", "CA", "GB", "DE", "FR", "IT", "ES", "AU", "NZ", "JP", "NL", "SE", "GLOBAL"],
        "routing_rules": ["cheapest", "fastest", "balanced", "domestic_only", "customs_avoidance"],
        "license": "MIT",
        "daemon": live_info,
    }

    if as_json:
        print(json.dumps(data, indent=2))
        return 0

    print("POD SMART ROUTER v2.5.0")
    print(f"Daemon Status: {data['status'].upper()} ({url})")
    print(f"Catalog Matrix: {len(products)} benchmark items")
    print("Routing Rules:  cheapest, fastest, balanced, domestic_only, customs_avoidance")
    print("License:        MIT (100% Free & Open-Source)")
    return 0

def main():
    parser = argparse.ArgumentParser(
        prog="pod-smart-router",
        description="Autonomous Multi-Channel Print-on-Demand Routing Engine (Printify vs Gelato)"
    )
    parser.add_argument("-v", "--version", action="version", version="pod-smart-router 2.5.0")
    parser.add_argument("--status", action="store_true", help="Print local service status and configuration")
    parser.add_argument("--json", action="store_true", help="Output status/telemetry as JSON")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8117, help="Port to check (default: 8117)")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: status
    p_status = subparsers.add_parser("status", help="Check local service and API configuration status")
    p_status.add_argument("--host", default="127.0.0.1", help="Host interface")
    p_status.add_argument("--port", type=int, default=8117, help="Port (default: 8117)")
    p_status.add_argument("--json", action="store_true", help="Output status report as JSON")

    # Command: route
    p_route = subparsers.add_parser("route", help="Calculate optimal POD routing decision")
    p_route.add_argument("--sku", default="gildan_18000", help="Product SKU (e.g. gildan_18000, comfort_colors_1717)")
    p_route.add_argument("--country", default="US", help="Destination country code (US, GB, DE, FR, CA, AU)")
    p_route.add_argument("--qty", type=int, default=1, help="Item quantity")
    p_route.add_argument("--rule", default="balanced", choices=["cheapest", "fastest", "balanced", "domestic_only", "customs_avoidance"])
    p_route.add_argument("--no-premium", action="store_true", help="Disable Printify Premium 20%% discount calculation")
    p_route.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: matrix
    p_matrix = subparsers.add_parser("matrix", help="View side-by-side catalog matrix across Printify and Gelato")
    p_matrix.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: dispatch
    p_dispatch = subparsers.add_parser("dispatch", help="Generate production API dispatch payload")
    p_dispatch.add_argument("--sku", default="gildan_18000")
    p_dispatch.add_argument("--country", default="GB")
    p_dispatch.add_argument("--qty", type=int, default=1)
    p_dispatch.add_argument("--rule", default="balanced")
    p_dispatch.add_argument("--artwork", default="https://nullai.tech/artwork/master.png")

    # Command: server
    p_server = subparsers.add_parser("server", help="Launch HTTP and Web UI server")
    p_server.add_argument("--port", type=int, default=8117, help="Server port (default: 8117)")

    args = parser.parse_args()
    if getattr(args, "status", False) or (getattr(args, "json", False) and not args.command):
        return cmd_status(host=getattr(args, "host", "127.0.0.1"), port=getattr(args, "port", 8117), as_json=bool(getattr(args, "json", False)))
    try:
        _run(args, parser)
    except ValueError as e:  # includes UnknownSKUError
        raise SystemExit(f"error: {e}")


def _run(args, parser):

    if args.command == "status":
        cmd_status(host=args.host, port=args.port, as_json=args.json)
        return

    if args.command == "route":
        decision = SmartRouter.route(
            sku=args.sku,
            destination_country=args.country,
            quantity=args.qty,
            rule=args.rule,
            printify_premium=not args.no_premium
        )
        if args.json:
            print(json.dumps(decision.to_dict(), indent=2))
        else:
            w = decision.winner_quote
            a = decision.alternative_quote
            print("=" * 65)
            print(f"🎯 POD ROUTING DECISION: {decision.recommended_partner.upper()}")
            print(f"Product: {decision.product_title} | Country: {decision.destination_country}")
            print(f"Reason:  {decision.decision_reason}")
            print(f"Landed Cost: Winner ${w.total_landed_cost:.2f} vs Alt ${a.total_landed_cost:.2f}")
            print(f"Delivery:    Winner {w.total_delivery_days} days vs Alt {a.total_delivery_days} days")
            print(f"Savings:     ${decision.dollar_savings:.2f} ({decision.percent_savings}%) | Days Saved: {decision.days_saved}")
            print(f"Customs Risk: {w.customs_risk_level} | Carbon Saved: {decision.carbon_miles_saved} mi")
            print("=" * 65)

    elif args.command == "matrix":
        catalog = get_all_products()
        if args.json:
            print(json.dumps(catalog, indent=2))
        else:
            print("=" * 75)
            print("POD CATALOG MATRIX (Printify vs Gelato)")
            print("=" * 75)
            for item in catalog:
                p_cost = item["printify"]["base_discount"]
                g_cost = item["gelato"]["base_discount"]
                print(f"[{item['id']}] {item['title']}")
                print(f"  MSRP: ${item['recommended_retail']:.2f} | Printify (Prem): ${p_cost:.2f} | Gelato Club: ${g_cost:.2f}")
                print(f"  Gelato Hubs: {len(item['gelato']['domestic_countries'])} countries | Printify Hubs: {len(item['printify']['domestic_countries'])} countries")
                print("-" * 75)

    elif args.command == "dispatch":
        decision = SmartRouter.route(
            sku=args.sku,
            destination_country=args.country,
            quantity=args.qty,
            rule=args.rule
        )
        dummy_address = {
            "first_name": "Alexander",
            "last_name": "Vance",
            "address1": "10 Downing St",
            "city": "London",
            "postal_code": "SW1A 2AA",
            "country": args.country,
            "email": "customer@example.com"
        }
        payload = DispatchPayloadGenerator.generate(
            decision=decision,
            customer_address=dummy_address,
            artwork_url=args.artwork
        )
        print(json.dumps(payload, indent=2))

    elif args.command == "server":
        run_server(args.port)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
