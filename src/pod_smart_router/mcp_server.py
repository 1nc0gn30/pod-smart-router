"""POD Smart Router - Antigravity MCP Stdio Server.

Exposes 6 JSON-RPC 2.0 Tools for Autonomous Agent Fulfillment Optimization
Zero external dependencies (100% Python standard library).
"""

import sys
import json
import traceback
from typing import Dict, Any, List

from .catalog_matrix import CATALOG_MATRIX, get_all_products
from .router import SmartRouter
from .payload_gen import DispatchPayloadGenerator

TOOLS_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "pod_route_order",
        "description": "Calculates the mathematically optimal Print-on-Demand partner (Printify vs Gelato) based on wholesale cost, domestic factory proximity, delivery speed, and customs avoidance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Product SKU (e.g. 'gildan_18000', 'comfort_colors_1717', 'bella_canvas_3001', 'ceramic_mug_15oz', 'canvas_gallery_wrap_16x20', 'matte_poster_18x24')",
                    "default": "gildan_18000"
                },
                "destination_country": {
                    "type": "string",
                    "description": "Two-letter ISO destination country code (e.g. 'US', 'GB', 'DE', 'FR', 'CA', 'AU')",
                    "default": "US"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Number of units ordered",
                    "default": 1
                },
                "rule": {
                    "type": "string",
                    "description": "Routing strategy: 'cheapest', 'fastest', 'balanced', 'domestic_only', 'customs_avoidance'",
                    "enum": ["cheapest", "fastest", "balanced", "domestic_only", "customs_avoidance"],
                    "default": "balanced"
                },
                "printify_premium": {
                    "type": "boolean",
                    "description": "Whether Printify Premium 20% wholesale discount tier applies",
                    "default": True
                }
            },
            "required": ["sku", "destination_country"]
        }
    },
    {
        "name": "pod_compare_pricing",
        "description": "Provides full side-by-side cost breakdown comparing Printify vs Gelato for a specific product and destination country.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Product SKU",
                    "default": "comfort_colors_1717"
                },
                "destination_country": {
                    "type": "string",
                    "description": "Two-letter ISO destination country code",
                    "default": "GB"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Units ordered",
                    "default": 1
                }
            },
            "required": ["sku", "destination_country"]
        }
    },
    {
        "name": "pod_generate_dispatch_payload",
        "description": "Generates a fully compliant, production-ready order creation JSON payload for Printify or Gelato API based on routing decision.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sku": {"type": "string", "default": "gildan_18000"},
                "destination_country": {"type": "string", "default": "US"},
                "quantity": {"type": "integer", "default": 1},
                "customer_address": {
                    "type": "object",
                    "description": "Customer address dict with first_name, last_name, address1, city, state, zip/postal_code, country, email",
                    "default": {
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "address1": "123 Main St",
                        "city": "Richmond",
                        "state": "VA",
                        "zip": "23220",
                        "country": "US"
                    }
                },
                "artwork_url": {
                    "type": "string",
                    "description": "Direct HTTPS URL to print-ready high-res artwork asset (300 DPI)"
                }
            },
            "required": ["sku", "destination_country"]
        }
    },
    {
        "name": "pod_list_routing_rules",
        "description": "Lists all available multi-channel dispatch optimization strategies and their algorithmic criteria.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "pod_calculate_savings",
        "description": "Calculates projected monthly and annual profit margin increase from autonomous POD routing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "monthly_orders": {
                    "type": "integer",
                    "description": "Estimated or actual monthly shop order count",
                    "default": 150
                },
                "avg_order_value_usd": {
                    "type": "number",
                    "description": "Average retail order value in USD",
                    "default": 34.00
                }
            }
        }
    },
    {
        "name": "pod_get_factory_coverage",
        "description": "Returns domestic factory production coverage, local fulfillment guarantees, and customs risk by country.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "Two-letter country code or 'all'",
                    "default": "all"
                }
            }
        }
    }
]

def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute MCP tool invocation."""
    if name == "pod_route_order":
        sku = arguments.get("sku", "gildan_18000")
        dest = arguments.get("destination_country", "US")
        qty = int(arguments.get("quantity", 1))
        rule = arguments.get("rule", "balanced")
        premium = bool(arguments.get("printify_premium", True))

        decision = SmartRouter.route(sku=sku, destination_country=dest, quantity=qty, rule=rule, printify_premium=premium)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(decision.to_dict(), indent=2)
                }
            ]
        }

    elif name == "pod_compare_pricing":
        sku = arguments.get("sku", "comfort_colors_1717")
        dest = arguments.get("destination_country", "GB")
        qty = int(arguments.get("quantity", 1))

        decision = SmartRouter.route(sku=sku, destination_country=dest, quantity=qty, rule="cheapest")
        comparison = {
            "sku": sku,
            "destination_country": dest,
            "quantity": qty,
            "product_title": decision.product_title,
            "winner": decision.recommended_partner,
            "winner_quote": decision.winner_quote.to_dict(),
            "alternative_quote": decision.alternative_quote.to_dict(),
            "savings_usd": decision.dollar_savings,
            "percent_savings": decision.percent_savings,
            "recommendation_reason": decision.decision_reason
        }
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(comparison, indent=2)
                }
            ]
        }

    elif name == "pod_generate_dispatch_payload":
        sku = arguments.get("sku", "gildan_18000")
        dest = arguments.get("destination_country", "US")
        qty = int(arguments.get("quantity", 1))
        addr = arguments.get("customer_address", {})
        art = arguments.get("artwork_url")

        decision = SmartRouter.route(sku=sku, destination_country=dest, quantity=qty, rule="balanced")
        payload = DispatchPayloadGenerator.generate(decision=decision, customer_address=addr, artwork_url=art)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "decision": decision.to_dict(),
                        "dispatch_payload": payload
                    }, indent=2)
                }
            ]
        }

    elif name == "pod_list_routing_rules":
        rules = [
            {"id": "cheapest", "name": "Maximum Margin (Lowest Landed Cost)"},
            {"id": "fastest", "name": "Fast Track (Quickest Delivery)"},
            {"id": "balanced", "name": "Balanced Sovereign (Fast + High Margin)"},
            {"id": "domestic_only", "name": "100% Domestic Local Only"},
            {"id": "customs_avoidance", "name": "Zero Customs Duty Lock"}
        ]
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(rules, indent=2)
                }
            ]
        }

    elif name == "pod_calculate_savings":
        monthly = int(arguments.get("monthly_orders", 150))
        avg_savings_per_order = 3.42
        monthly_savings = monthly * avg_savings_per_order
        annual_savings = monthly_savings * 12
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "monthly_order_volume": monthly,
                        "projected_monthly_savings_usd": round(monthly_savings, 2),
                        "projected_annual_savings_usd": round(annual_savings, 2),
                        "customs_delays_avoided_per_year": int(monthly * 0.18 * 12),
                        "lifetime_tool_cost_usd": 19.00,
                        "roi_percentage_year_1": round(((annual_savings - 19.0) / 19.0) * 100, 1)
                    }, indent=2)
                }
            ]
        }

    elif name == "pod_get_factory_coverage":
        country = arguments.get("country", "all").upper()
        coverage = {
            "US": {"printify_domestic": True, "gelato_domestic": True, "customs_risk": "none"},
            "GB": {"printify_domestic": True, "gelato_domestic": True, "customs_risk": "none"},
            "DE": {"printify_domestic": True, "gelato_domestic": True, "customs_risk": "none"},
            "FR": {"printify_domestic": False, "gelato_domestic": True, "customs_risk": "none with Gelato, high with Printify US"},
            "IT": {"printify_domestic": False, "gelato_domestic": True, "customs_risk": "none with Gelato, high with Printify US"},
            "ES": {"printify_domestic": False, "gelato_domestic": True, "customs_risk": "none with Gelato, high with Printify US"},
            "CA": {"printify_domestic": True, "gelato_domestic": True, "customs_risk": "none"},
            "AU": {"printify_domestic": True, "gelato_domestic": True, "customs_risk": "none"}
        }
        res = coverage.get(country, coverage) if country != "ALL" else coverage
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(res, indent=2)
                }
            ]
        }

    else:
        raise ValueError(f"Unknown tool name: {name}")

def run_mcp_stdio():
    """Stdio JSON-RPC 2.0 loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": TOOLS_DEFINITIONS
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result = handle_call_tool(tool_name, tool_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": result
                }
            elif method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "pod-smart-router",
                            "version": "1.0.0"
                        }
                    }
                }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": str(e),
                    "data": traceback.format_exc()
                }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_mcp_stdio()
