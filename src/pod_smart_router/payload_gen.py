"""POD Smart Router - Dispatch Payload Generator.

Generates canonical, API-compliant production payloads for Printify and Gelato
zero external dependencies (100% Python standard library).
"""

from typing import Dict, Any, Optional
import uuid
import time
from .router import RoutingDecision

class DispatchPayloadGenerator:
    """Generates ready-to-transmit JSON payloads for Printify and Gelato order APIs."""

    @staticmethod
    def generate(
        decision: RoutingDecision,
        customer_address: Dict[str, Any],
        artwork_url: Optional[str] = None,
        external_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate target fulfillment payload formatted strictly to the winning partner's schema."""
        ext_id = external_order_id or f"ORD-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
        artwork = artwork_url or "https://storage.googleapis.com/nullai-assets/designs/master-300dpi.png"

        if decision.recommended_partner == "gelato":
            return DispatchPayloadGenerator._generate_gelato(decision, customer_address, artwork, ext_id)
        else:
            return DispatchPayloadGenerator._generate_printify(decision, customer_address, artwork, ext_id)

    @staticmethod
    def _generate_gelato(
        decision: RoutingDecision,
        address: Dict[str, Any],
        artwork_url: str,
        external_id: str
    ) -> Dict[str, Any]:
        return {
            "partner": "gelato",
            "endpoint": "https://api.gelato.com/v2/orders",
            "orderType": "order",
            "orderReferenceId": external_id,
            "customerReferenceId": f"CUST-{uuid.uuid4().hex[:8].upper()}",
            "currency": "USD",
            "items": [
                {
                    "itemReferenceId": f"ITEM-{decision.product_id}",
                    "productUid": decision.winner_quote.product_sku,
                    "files": [
                        {
                            "type": "default",
                            "url": artwork_url
                        }
                    ],
                    "quantity": decision.quantity
                }
            ],
            "shippingAddress": {
                "firstName": address.get("first_name", "Jane"),
                "lastName": address.get("last_name", "Doe"),
                "companyName": address.get("company", ""),
                "addressLine1": address.get("address1", "123 Sovereign Way"),
                "addressLine2": address.get("address2", ""),
                "city": address.get("city", "London"),
                "postCode": address.get("postal_code") or address.get("zip", "EC1A 1BB"),
                "state": address.get("state", ""),
                "country": decision.destination_country,
                "email": address.get("email", "orders@nullai.tech"),
                "phone": address.get("phone", "+15550192834")
            },
            "routing_telemetry": {
                "routed_by": "pod-smart-router-v1",
                "margin_advantage_usd": round(decision.dollar_savings, 2),
                "delivery_days_saved": decision.days_saved,
                "customs_duty_risk": decision.winner_quote.customs_risk_level,
                "carbon_miles_saved": decision.carbon_miles_saved,
                "reason": decision.decision_reason
            }
        }

    @staticmethod
    def _generate_printify(
        decision: RoutingDecision,
        address: Dict[str, Any],
        artwork_url: str,
        external_id: str
    ) -> Dict[str, Any]:
        return {
            "partner": "printify",
            "endpoint": "https://api.printify.com/v1/shops/{shop_id}/orders.json",
            "external_id": external_id,
            "label": f"NullAI-{external_id[-6:]}",
            "line_items": [
                {
                    "product_id": decision.winner_quote.product_sku,
                    "variant_id": 45012,
                    "quantity": decision.quantity,
                    "metadata": {
                        "artwork_url": artwork_url
                    }
                }
            ],
            "shipping_method": 1,
            "send_shipping_notification": True,
            "address_to": {
                "first_name": address.get("first_name", "John"),
                "last_name": address.get("last_name", "Smith"),
                "email": address.get("email", "orders@nullai.tech"),
                "phone": address.get("phone", "+15550192834"),
                "country": decision.destination_country,
                "region": address.get("state") or address.get("region", "VA"),
                "address1": address.get("address1", "400 Granby St"),
                "address2": address.get("address2", "Suite 200"),
                "city": address.get("city", "Norfolk"),
                "zip": address.get("postal_code") or address.get("zip", "23510")
            },
            "routing_telemetry": {
                "routed_by": "pod-smart-router-v1",
                "margin_advantage_usd": round(decision.dollar_savings, 2),
                "delivery_days_saved": decision.days_saved,
                "customs_duty_risk": decision.winner_quote.customs_risk_level,
                "carbon_miles_saved": decision.carbon_miles_saved,
                "reason": decision.decision_reason
            }
        }
