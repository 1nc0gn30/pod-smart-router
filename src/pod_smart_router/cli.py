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

def main():
    parser = argparse.ArgumentParser(
        prog="pod-smart-router",
        description="Autonomous Multi-Channel Print-on-Demand Routing Engine (Printify vs Gelato)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: route
    p_route = subparsers.add_parser("route", help="Calculate optimal POD routing decision")
    p_route.add_argument("--sku", default="gildan_18000", help="Product SKU (e.g. gildan_18000, comfort_colors_1717)")
    p_route.add_argument("--country", default="US", help="Destination country code (US, GB, DE, FR, CA, AU)")
    p_route.add_argument("--qty", type=int, default=1, help="Item quantity")
    p_route.add_argument("--rule", default="balanced", choices=["cheapest", "fastest", "balanced", "domestic_only", "customs_avoidance"])
    p_route.add_argument("--no-premium", action="store_true", help="Disable Printify Premium 20% discount calculation")
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
    try:
        _run(args, parser)
    except ValueError as e:  # includes UnknownSKUError
        raise SystemExit(f"error: {e}")


def _run(args, parser):

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
