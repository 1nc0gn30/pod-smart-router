"""Unit Tests for POD Smart Router.

100% Python Standard Library (unittest).
Zero external test framework dependencies.
"""

import os
import sys
import unittest

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from pod_smart_router.catalog_matrix import CATALOG_MATRIX, get_all_products
from pod_smart_router.router import SmartRouter, RoutingDecision
from pod_smart_router.payload_gen import DispatchPayloadGenerator

class TestPODSmartRouter(unittest.TestCase):

    def setUp(self):
        self.router = SmartRouter()

    def test_catalog_matrix_integrity(self):
        """Verify all 10 core products exist with complete partner profiles."""
        self.assertGreaterEqual(len(CATALOG_MATRIX), 10)
        products = get_all_products()
        self.assertEqual(len(products), len(CATALOG_MATRIX))

        for p in products:
            self.assertIn("id", p)
            self.assertIn("title", p)
            self.assertIn("recommended_retail", p)
            self.assertGreater(p["printify"]["base_standard"], 0)
            self.assertGreater(p["gelato"]["base_standard"], 0)
            self.assertGreater(len(p["gelato"]["domestic_countries"]), 0)
            self.assertGreater(len(p["printify"]["domestic_countries"]), 0)

    def test_us_domestic_routing_cheapest(self):
        """In the US, Printify with Premium should win on base landed cost for Gildan 18000."""
        decision = self.router.route_order(
            product_id="gildan_18000",
            destination_country="US",
            quantity=1,
            shipping_priority="cheapest",
            use_printify_premium=True
        )
        self.assertEqual(decision.recommended_partner, "printify")
        self.assertTrue(decision.winner_quote.is_domestic_factory)
        self.assertEqual(decision.winner_quote.customs_risk_level, "ZERO (Domestic)")
        self.assertGreater(decision.dollar_savings, 0.0)

    def test_eu_customs_avoidance_routing(self):
        """Routing Bella Canvas 3001 to France with customs_avoidance must select Gelato."""
        decision = self.router.route_order(
            product_id="bella_canvas_3001",
            destination_country="FR",
            quantity=1,
            shipping_priority="customs_avoidance"
        )
        self.assertEqual(decision.recommended_partner, "gelato")
        self.assertTrue(decision.winner_quote.is_domestic_factory)
        self.assertEqual(decision.winner_quote.customs_risk_level, "ZERO (Domestic)")
        self.assertGreater(decision.days_saved, 0)
        self.assertGreater(decision.carbon_miles_saved, 0)

    def test_fastest_delivery_rule(self):
        """Fastest priority selects partner with lowest total delivery days."""
        decision = self.router.route_order(
            product_id="matte_poster_18x24",
            destination_country="DE",
            quantity=1,
            shipping_priority="fastest"
        )
        winner_days = decision.winner_quote.total_delivery_days
        alt_days = decision.alternative_quote.total_delivery_days
        self.assertLessEqual(winner_days, alt_days)

    def test_dispatch_payload_generation_gelato(self):
        """Verify Gelato order payload structure conforms to Gelato API v2."""
        decision = self.router.route_order(
            product_id="bella_canvas_3001",
            destination_country="FR",
            quantity=2,
            shipping_priority="customs_avoidance"
        )
        address = {
            "first_name": "Pierre",
            "last_name": "Dubois",
            "address1": "14 Rue de Rivoli",
            "city": "Paris",
            "postal_code": "75001",
            "country": "FR",
            "email": "pierre@example.com"
        }
        payload = DispatchPayloadGenerator.generate(
            decision=decision,
            customer_address=address,
            artwork_url="https://nullai.tech/art/france-edition.png",
            external_order_id="ORD-TEST-1234"
        )
        self.assertEqual(payload["partner"], "gelato")
        self.assertEqual(payload["orderType"], "order")
        self.assertEqual(payload["orderReferenceId"], "ORD-TEST-1234")
        self.assertEqual(payload["items"][0]["quantity"], 2)
        self.assertEqual(payload["shippingAddress"]["city"], "Paris")
        self.assertEqual(payload["shippingAddress"]["country"], "FR")
        self.assertIn("routing_telemetry", payload)

    def test_dispatch_payload_generation_printify(self):
        """Verify Printify order payload structure conforms to Printify API v1."""
        decision = self.router.route_order(
            product_id="gildan_18000",
            destination_country="US",
            quantity=1,
            shipping_priority="cheapest"
        )
        address = {
            "first_name": "Sarah",
            "last_name": "Connor",
            "address1": "450 Olympic Blvd",
            "city": "Los Angeles",
            "state": "CA",
            "postal_code": "90015",
            "country": "US",
            "email": "sarah@example.com"
        }
        payload = DispatchPayloadGenerator.generate(
            decision=decision,
            customer_address=address,
            artwork_url="https://nullai.tech/art/synth-wave.png",
            external_order_id="ORD-PRINTIFY-789"
        )
        self.assertEqual(payload["partner"], "printify")
        self.assertEqual(payload["external_id"], "ORD-PRINTIFY-789")
        self.assertEqual(payload["line_items"][0]["quantity"], 1)
        self.assertEqual(payload["address_to"]["city"], "Los Angeles")
        self.assertEqual(payload["address_to"]["country"], "US")
        self.assertIn("routing_telemetry", payload)

    def test_telemetry_accumulation(self):
        """Verify cumulative routing stats update properly across calls."""
        router = SmartRouter()
        self.assertEqual(router.total_routes_count, 0)
        self.assertEqual(router.cumulative_savings, 0.0)

        router.route_order("gildan_18000", "US", 1)
        router.route_order("bella_canvas_3001", "FR", 1)

        self.assertEqual(router.total_routes_count, 2)
        self.assertGreater(router.cumulative_savings, 0.0)
        self.assertEqual(len(router.routing_history), 2)

if __name__ == "__main__":
    unittest.main()
