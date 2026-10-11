"""POD Smart Routing Engine — Multi-Partner Optimization (Printify vs Gelato).

Computes optimal fulfillment route based on landed cost, local factory proximity,
delivery speed, and cross-border customs elimination.
100% Python Standard Library.
"""

from __future__ import annotations

import difflib
import secrets
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .catalog_matrix import CATALOG_MATRIX, CatalogItem, PartnerProductProfile, get_all_products


@dataclass
class PartnerQuote:
    partner: str
    product_sku: str
    is_domestic_factory: bool
    base_item_cost: float
    total_base_cost: float
    shipping_cost: float
    estimated_customs_vat: float
    total_landed_cost: float
    production_days: int
    transit_days: int
    total_delivery_days: int
    carbon_freight_miles: int
    customs_risk_level: str  # "ZERO (Domestic)", "MODERATE", "HIGH"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RoutingDecision:
    routing_id: str
    timestamp: str
    product_id: str
    product_title: str
    destination_country: str
    quantity: int
    priority_rule: str
    recommended_partner: str  # "printify" or "gelato"
    winner_quote: PartnerQuote
    alternative_quote: PartnerQuote
    dollar_savings: float
    percent_savings: float
    days_saved: int
    carbon_miles_saved: int
    customs_avoided_amount: float
    decision_reason: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["winner"] = self.recommended_partner
        data["savings_usd"] = self.dollar_savings
        return data


VALID_RULES = ("cheapest", "fastest", "balanced", "domestic_only", "customs_avoidance")

# Value of one day of delivery time when trading cost against speed ("balanced").
BALANCED_USD_PER_DAY = 0.50


class UnknownSKUError(ValueError):
    """Raised when a SKU cannot be matched to the catalog (never silently substituted)."""


class SmartRouter:
    """Evaluates landed costs, manufacturing hubs, and delivery timelines."""

    def __init__(self):
        self.routing_history: List[RoutingDecision] = []
        self.cumulative_savings: float = 0.0
        self.domestic_routes_count: int = 0
        self.total_routes_count: int = 0

    @classmethod
    def normalize_sku(cls, raw_sku: str) -> str:
        """Map a SKU to a catalog key. Accepts exact keys and unambiguous partial
        matches; raises UnknownSKUError instead of guessing a different product."""
        s = str(raw_sku or "").lower().replace("-", "_").replace(" ", "_").strip()
        if not s:
            raise UnknownSKUError("SKU is required")
        if s in CATALOG_MATRIX:
            return s
        partial = [k for k in CATALOG_MATRIX if (k in s or s in k)]
        if len(s) >= 4 and len(partial) == 1:
            return partial[0]
        hints = partial or difflib.get_close_matches(s, list(CATALOG_MATRIX), n=3, cutoff=0.5)
        msg = f"Unknown SKU {raw_sku!r}"
        if hints:
            msg += f" (ambiguous or close to: {', '.join(hints)})"
        raise UnknownSKUError(msg + f". Valid SKUs: {', '.join(CATALOG_MATRIX)}")

    def route_order(
        self,
        product_id: str,
        destination_country: str = "US",
        quantity: int = 1,
        shipping_priority: str = "cheapest",
        use_printify_premium: bool = True,
    ) -> RoutingDecision:
        """Evaluate order and compute optimal POD partner."""
        dest = destination_country.upper().strip()
        if not (len(dest) == 2 and dest.isalpha()):
            raise ValueError(f"destination_country must be an ISO-3166 alpha-2 code, got {destination_country!r}")
        qty = int(quantity)
        if qty < 1:
            raise ValueError("quantity must be >= 1")
        priority = (shipping_priority or "balanced").lower().strip()
        if priority not in VALID_RULES:
            raise ValueError(f"Unknown routing rule {shipping_priority!r}. Use one of: {', '.join(VALID_RULES)}")

        # Lookup catalog item (raises UnknownSKUError rather than substituting)
        item = CATALOG_MATRIX[self.normalize_sku(product_id)]

        # 1. Quote Printify
        quote_pr = self._calculate_quote(
            profile=item.printify,
            dest_country=dest,
            qty=qty,
            use_discount=use_printify_premium,
        )

        # 2. Quote Gelato
        quote_gel = self._calculate_quote(
            profile=item.gelato,
            dest_country=dest,
            qty=qty,
            use_discount=True,  # Gelato Club rates
        )

        # 3. Determine Winner Based on Rule
        winner, alt, reason = self._select_winner(quote_pr, quote_gel, priority, dest)

        dollar_savings = round(max(0.0, alt.total_landed_cost - winner.total_landed_cost), 2)
        pct_savings = round((dollar_savings / alt.total_landed_cost) * 100.0, 1) if alt.total_landed_cost > 0 else 0.0
        days_saved = max(0, alt.total_delivery_days - winner.total_delivery_days)
        carbon_saved = max(0, alt.carbon_freight_miles - winner.carbon_freight_miles)
        customs_avoided = round(max(0.0, alt.estimated_customs_vat - winner.estimated_customs_vat), 2)

        decision = RoutingDecision(
            routing_id=f"route_{secrets.token_hex(6)}",
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            product_id=item.id,
            product_title=item.title,
            destination_country=dest,
            quantity=qty,
            priority_rule=priority,
            recommended_partner=winner.partner,
            winner_quote=winner,
            alternative_quote=alt,
            dollar_savings=dollar_savings,
            percent_savings=pct_savings,
            days_saved=days_saved,
            carbon_miles_saved=carbon_saved,
            customs_avoided_amount=customs_avoided,
            decision_reason=reason,
        )

        # Update telemetry
        self.routing_history.append(decision)
        if len(self.routing_history) > 500:
            self.routing_history = self.routing_history[-500:]
        self.cumulative_savings += dollar_savings
        self.total_routes_count += 1
        if winner.is_domestic_factory:
            self.domestic_routes_count += 1

        return decision

    @classmethod
    def route(
        cls,
        sku: str = "gildan_18000",
        destination_country: str = "US",
        quantity: int = 1,
        rule: str = "balanced",
        printify_premium: bool = True
    ) -> RoutingDecision:
        """Class method convenience wrapper."""
        router = _get_default_router()
        return router.route_order(
            product_id=sku,
            destination_country=destination_country,
            quantity=quantity,
            shipping_priority=rule,
            use_printify_premium=printify_premium
        )

    def _calculate_quote(
        self,
        profile: PartnerProductProfile,
        dest_country: str,
        qty: int,
        use_discount: bool,
    ) -> PartnerQuote:
        is_domestic = dest_country in profile.primary_countries
        base_item = profile.base_cost_discount if use_discount else profile.base_cost_standard
        total_base = round(base_item * qty, 2)

        # Shipping Calculation
        if is_domestic:
            ship_first = profile.domestic_shipping
            ship_add = round(profile.domestic_shipping * 0.4, 2)
            customs_vat = 0.0
            customs_risk = "ZERO (Domestic)"
            transit_days = profile.avg_delivery_days_domestic
            carbon_miles = 400
        else:
            ship_first = profile.international_shipping
            ship_add = round(profile.international_shipping * 0.5, 2)
            # Estimate cross-border import VAT / customs fees (approx 20% on value + carrier brokerage)
            if dest_country in ("GB", "DE", "FR", "IT", "ES", "NL", "AU", "CA"):
                customs_vat = round(total_base * 0.20 + 3.50, 2)
                customs_risk = "HIGH (VAT & Brokerage)"
            else:
                customs_vat = round(total_base * 0.15, 2)
                customs_risk = "MODERATE (Cross-Border)"
            transit_days = profile.avg_delivery_days_intl
            carbon_miles = 4500

        total_shipping = round(ship_first + ship_add * (qty - 1), 2)
        total_landed = round(total_base + total_shipping + customs_vat, 2)
        total_delivery = profile.avg_production_days + transit_days

        return PartnerQuote(
            partner=profile.partner,
            product_sku=profile.partner_sku,
            is_domestic_factory=is_domestic,
            base_item_cost=base_item,
            total_base_cost=total_base,
            shipping_cost=total_shipping,
            estimated_customs_vat=customs_vat,
            total_landed_cost=total_landed,
            production_days=profile.avg_production_days,
            transit_days=transit_days,
            total_delivery_days=total_delivery,
            carbon_freight_miles=carbon_miles,
            customs_risk_level=customs_risk,
        )

    def _select_winner(
        self,
        q_printify: PartnerQuote,
        q_gelato: PartnerQuote,
        priority: str,
        dest_country: str,
    ) -> Tuple[PartnerQuote, PartnerQuote, str]:
        # Rule A: Domestic Only / Customs Avoidance
        if priority in ("domestic_only", "customs_avoidance"):
            if q_gelato.is_domestic_factory and not q_printify.is_domestic_factory:
                return q_gelato, q_printify, f"Gelato selected: Local factory in {dest_country} guarantees zero customs duty and faster delivery."
            if q_printify.is_domestic_factory and not q_gelato.is_domestic_factory:
                return q_printify, q_gelato, f"Printify selected: Domestic factory active in {dest_country}."

        # Rule: Balanced = keep domestic (zero customs) when any partner has it,
        # then minimise landed cost + time value of delivery days.
        if priority == "balanced":
            pool = [q for q in (q_printify, q_gelato) if q.is_domestic_factory] or [q_printify, q_gelato]
            score = lambda q: q.total_landed_cost + BALANCED_USD_PER_DAY * q.total_delivery_days
            winner = min(pool, key=lambda q: (score(q), q.total_landed_cost))
            alt = q_gelato if winner is q_printify else q_printify
            why = (f"{winner.partner.title()} selected (balanced): ${winner.total_landed_cost:.2f} landed, "
                   f"{winner.total_delivery_days}d delivery vs {alt.partner.title()} ${alt.total_landed_cost:.2f}, {alt.total_delivery_days}d")
            if winner.is_domestic_factory:
                why += f"; domestic factory in {dest_country}, zero customs."
            else:
                why += "; no domestic factory available for this destination."
            return winner, alt, why

        # Rule B: Fastest Delivery
        if priority == "fastest":
            if q_gelato.total_delivery_days < q_printify.total_delivery_days:
                diff = q_printify.total_delivery_days - q_gelato.total_delivery_days
                return q_gelato, q_printify, f"Gelato delivers {diff} day(s) faster via localized routing ({q_gelato.total_delivery_days}d vs {q_printify.total_delivery_days}d)."
            elif q_printify.total_delivery_days < q_gelato.total_delivery_days:
                diff = q_gelato.total_delivery_days - q_printify.total_delivery_days
                return q_printify, q_gelato, f"Printify delivers {diff} day(s) faster ({q_printify.total_delivery_days}d vs {q_gelato.total_delivery_days}d)."

        # Rule C: Cheapest / Landed Cost
        if q_printify.total_landed_cost < q_gelato.total_landed_cost:
            diff = round(q_gelato.total_landed_cost - q_printify.total_landed_cost, 2)
            reason = f"Printify wins on total landed cost: Saves ${diff:.2f} ({q_printify.partner.title()} ${q_printify.total_landed_cost:.2f} vs {q_gelato.partner.title()} ${q_gelato.total_landed_cost:.2f})."
            if q_printify.is_domestic_factory:
                reason += f" Domestic hub verified in {dest_country}."
            return q_printify, q_gelato, reason
        else:
            diff = round(q_printify.total_landed_cost - q_gelato.total_landed_cost, 2)
            reason = f"Gelato wins on total landed cost: Saves ${diff:.2f} ({q_gelato.partner.title()} ${q_gelato.total_landed_cost:.2f} vs {q_printify.partner.title()} ${q_printify.total_landed_cost:.2f})."
            if q_gelato.is_domestic_factory and not q_printify.is_domestic_factory:
                reason += f" Eliminates cross-border customs/VAT fees to {dest_country}."
            return q_gelato, q_printify, reason


_DEFAULT_ROUTER: Optional[SmartRouter] = None

def _get_default_router() -> SmartRouter:
    global _DEFAULT_ROUTER
    if _DEFAULT_ROUTER is None:
        _DEFAULT_ROUTER = SmartRouter()
    return _DEFAULT_ROUTER
