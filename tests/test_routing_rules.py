"""Rule semantics, input validation and money invariants for the smart router."""
import os, sys, subprocess, unittest
SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC)

from pod_smart_router.catalog_matrix import CATALOG_MATRIX
from pod_smart_router.router import SmartRouter, UnknownSKUError, VALID_RULES, BALANCED_USD_PER_DAY

COUNTRIES = ["US", "GB", "DE", "FR", "AU", "CA", "JP", "BR"]


class TestSkuNormalization(unittest.TestCase):
    def test_exact_and_dashed(self):
        self.assertEqual(SmartRouter.normalize_sku("Gildan-18000"), "gildan_18000")
        self.assertEqual(SmartRouter.normalize_sku("ceramic mug 15oz"), "ceramic_mug_15oz")

    def test_unknown_sku_raises_not_substitutes(self):
        with self.assertRaises(UnknownSKUError):
            SmartRouter.normalize_sku("wool_beanie")
        with self.assertRaises(UnknownSKUError):
            SmartRouter.normalize_sku("")

    def test_ambiguous_partial_raises(self):
        with self.assertRaises(UnknownSKUError) as cm:
            SmartRouter.normalize_sku("ceramic_mug")  # 11oz or 15oz?
        self.assertIn("ceramic_mug_11oz", str(cm.exception))


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.r = SmartRouter()

    def test_bad_inputs(self):
        for kw in ({"destination_country": "USA"}, {"quantity": 0}, {"shipping_priority": "yolo"}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.r.route_order("gildan_18000", **kw)


class TestRuleSemantics(unittest.TestCase):
    def setUp(self):
        self.r = SmartRouter()

    def _all(self, rule):
        for sku in CATALOG_MATRIX:
            for c in COUNTRIES:
                yield sku, c, self.r.route_order(sku, c, 2, rule)

    def test_cheapest_never_picks_more_expensive(self):
        for sku, c, d in self._all("cheapest"):
            self.assertLessEqual(d.winner_quote.total_landed_cost, d.alternative_quote.total_landed_cost, (sku, c))

    def test_fastest_never_picks_slower(self):
        for sku, c, d in self._all("fastest"):
            self.assertLessEqual(d.winner_quote.total_delivery_days, d.alternative_quote.total_delivery_days, (sku, c))

    def test_balanced_prefers_domestic_and_scores(self):
        for sku, c, d in self._all("balanced"):
            w, a = d.winner_quote, d.alternative_quote
            if a.is_domestic_factory:
                self.assertTrue(w.is_domestic_factory, (sku, c))
            if w.is_domestic_factory == a.is_domestic_factory:
                sc = lambda q: q.total_landed_cost + BALANCED_USD_PER_DAY * q.total_delivery_days
                self.assertLessEqual(sc(w), sc(a) + 1e-9, (sku, c))
            self.assertIn("balanced", d.decision_reason)

    def test_domestic_rules_pick_domestic_when_possible(self):
        for rule in ("domestic_only", "customs_avoidance"):
            for sku, c, d in self._all(rule):
                if d.alternative_quote.is_domestic_factory:
                    self.assertTrue(d.winner_quote.is_domestic_factory, (rule, sku, c))

    def test_money_invariants(self):
        for rule in VALID_RULES:
            for sku, c, d in self._all(rule):
                for q in (d.winner_quote, d.alternative_quote):
                    self.assertAlmostEqual(q.total_landed_cost, q.total_base_cost + q.shipping_cost + q.estimated_customs_vat, places=2)
                    if q.is_domestic_factory:
                        self.assertEqual(q.estimated_customs_vat, 0.0)
                self.assertGreaterEqual(d.dollar_savings, 0.0)

    def test_quantity_scales_cost(self):
        one = self.r.route_order("ceramic_mug_11oz", "US", 1, "cheapest").winner_quote
        five = self.r.route_order("ceramic_mug_11oz", "US", 5, "cheapest").winner_quote
        self.assertGreater(five.total_landed_cost, one.total_landed_cost)


class TestCli(unittest.TestCase):
    def test_cli_unknown_sku_is_clean_error(self):
        env = dict(os.environ, PYTHONPATH=SRC)
        p = subprocess.run([sys.executable, "-m", "pod_smart_router.cli", "route", "--sku", "wool_beanie"],
                           capture_output=True, text=True, env=env)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Unknown SKU", p.stderr)
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
