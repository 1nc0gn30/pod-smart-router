"""Normalized Cross-Partner Catalog Matrix for Printify vs Gelato.

Contains side-by-side base costs, domestic production hubs, and shipping profiles.
100% Python Standard Library.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PartnerProductProfile:
    partner: str  # "printify" or "gelato"
    partner_sku: str
    base_cost_standard: float
    base_cost_discount: float  # Printify Premium (20% off) or Gelato Club
    primary_countries: List[str]  # Countries where local production exists
    domestic_shipping: float
    international_shipping: float
    avg_production_days: int
    avg_delivery_days_domestic: int
    avg_delivery_days_intl: int
    supports_branding: bool


@dataclass
class CatalogItem:
    id: str
    title: str
    category: str
    recommended_retail: float
    printify: PartnerProductProfile
    gelato: PartnerProductProfile


# Normalized Catalog of Top 10 High-Volume POD Products
CATALOG_MATRIX: Dict[str, CatalogItem] = {
    "gildan_18000": CatalogItem(
        id="gildan_18000",
        title="Gildan 18000 Heavy Blend Crewneck Sweatshirt",
        category="Apparel",
        recommended_retail=34.99,
        printify=PartnerProductProfile(
            partner="printify",
            partner_sku="pr-sweatshirt-18000",
            base_cost_standard=12.50,
            base_cost_discount=10.00,  # Printify Premium (20% off)
            primary_countries=["US", "CA", "GB", "DE"],
            domestic_shipping=4.99,
            international_shipping=11.50,
            avg_production_days=2,
            avg_delivery_days_domestic=4,
            avg_delivery_days_intl=12,
            supports_branding=True,
        ),
        gelato=PartnerProductProfile(
            partner="gelato",
            partner_sku="apparel-sweatshirt-gildan18000",
            base_cost_standard=13.20,
            base_cost_discount=11.50,
            primary_countries=["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "NZ", "SE", "NO"],
            domestic_shipping=4.50,
            international_shipping=9.80,
            avg_production_days=2,
            avg_delivery_days_domestic=3,
            avg_delivery_days_intl=8,
            supports_branding=False,
        ),
    ),
    "comfort_colors_1717": CatalogItem(
        id="comfort_colors_1717",
        title="Comfort Colors 1717 Garment-Dyed Heavyweight Tee",
        category="Apparel",
        recommended_retail=28.99,
        printify=PartnerProductProfile(
            partner="printify",
            partner_sku="pr-cc-1717",
            base_cost_standard=13.80,
            base_cost_discount=11.04,
            primary_countries=["US"],
            domestic_shipping=4.75,
            international_shipping=10.99,
            avg_production_days=2,
            avg_delivery_days_domestic=4,
            avg_delivery_days_intl=14,
            supports_branding=True,
        ),
        gelato=PartnerProductProfile(
            partner="gelato",
            partner_sku="apparel-tee-comfortcolors1717",
            base_cost_standard=14.90,
            base_cost_discount=13.20,
            primary_countries=["US", "GB", "DE"],
            domestic_shipping=4.50,
            international_shipping=8.50,
            avg_production_days=2,
            avg_delivery_days_domestic=3,
            avg_delivery_days_intl=9,
            supports_branding=False,
        ),
    ),
    "bella_canvas_3001": CatalogItem(
        id="bella_canvas_3001",
        title="Bella+Canvas 3001 Unisex Jersey Short Sleeve Tee",
        category="Apparel",
        recommended_retail=24.99,
        printify=PartnerProductProfile(
            partner="printify",
            partner_sku="pr-bc-3001",
            base_cost_standard=8.95,
            base_cost_discount=7.16,
            primary_countries=["US", "GB", "DE", "CA", "AU"],
            domestic_shipping=4.75,
            international_shipping=9.99,
            avg_production_days=2,
            avg_delivery_days_domestic=3,
            avg_delivery_days_intl=10,
            supports_branding=True,
        ),
        gelato=PartnerProductProfile(
            partner="gelato",
            partner_sku="apparel-tee-bc3001",
            base_cost_standard=9.40,
            base_cost_discount=8.10,
            primary_countries=["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "NZ", "SE", "NO", "JP", "BR"],
            domestic_shipping=4.20,
            international_shipping=7.90,
            avg_production_days=1,
            avg_delivery_days_domestic=3,
            avg_delivery_days_intl=7,
            supports_branding=False,
        ),
    ),
    "ceramic_mug_15oz": CatalogItem(
        id="ceramic_mug_15oz",
        title="White Gloss Ceramic Mug 15oz",
        category="Home & Living",
        recommended_retail=21.99,
        printify=PartnerProductProfile(
            partner="printify",
            partner_sku="pr-mug-15oz",
            base_cost_standard=6.80,
            base_cost_discount=5.44,
            primary_countries=["US", "GB"],
            domestic_shipping=5.99,
            international_shipping=12.99,
            avg_production_days=2,
            avg_delivery_days_domestic=4,
            avg_delivery_days_intl=14,
            supports_branding=False,
        ),
        gelato=PartnerProductProfile(
            partner="gelato",
            partner_sku="drinkware-mug-ceramic-15oz",
            base_cost_standard=6.95,
            base_cost_discount=6.10,
            primary_countries=["US", "CA", "GB", "DE", "FR", "IT", "ES", "AU", "NZ", "SG"],
            domestic_shipping=4.90,
            international_shipping=8.90,
            avg_production_days=1,
            avg_delivery_days_domestic=3,
            avg_delivery_days_intl=7,
            supports_branding=False,
        ),
    ),
    "ceramic_mug_11oz": CatalogItem(
        id="ceramic_mug_11oz",
        title="Classic Ceramic Coffee Mug 11oz",
        category="Home & Living",
        recommended_retail=17.99,
        printify=PartnerProductProfile(
            partner="printify",
            partner_sku="pr-mug-11oz",
            base_cost_standard=4.95,
            base_cost_discount=3.96,
            primary_countries=["US", "GB", "DE", "AU"],
            domestic_shipping=5.49,
            international_shipping=11.99,
            avg_production_days=2,
            avg_delivery_days_domestic=4,
            avg_delivery_days_intl=12,
            supports_branding=False,
        ),
        gelato=PartnerProductProfile(
            partner="gelato",
            partner_sku="drinkware-mug-ceramic-11oz",
            base_cost_standard=5.20,
            base_cost_discount=4.60,
            primary_countries=["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "NZ", "SE", "NO", "DK", "JP"],
            domestic_shipping=4.50,
            international_shipping=7.80,
            avg_production_days=1,
            avg_delivery_days_domestic=2,
            avg_delivery_days_intl=6,
            supports_branding=False,
        ),
    ),
    "canvas_gallery_wrap_16x20": CatalogItem(
        id="canvas_gallery_wrap_16x20",
        title="Stretched Canvas Gallery Wrap 16x20 Inch",
        category="Wall Art",
        recommended_retail=54.99,
        printify=PartnerProductProfile(
            partner="printify",
            partner_sku="pr-canvas-16x20",
            base_cost_standard=18.50,
            base_cost_discount=14.80,
            primary_countries=["US", "GB", "DE"],
            domestic_shipping=8.99,
            international_shipping=24.50,
            avg_production_days=3,
            avg_delivery_days_domestic=5,
            avg_delivery_days_intl=16,
            supports_branding=False,
        ),
        gelato=PartnerProductProfile(
            partner="gelato",
            partner_sku="wall-art-canvas-slim-16x20",
            base_cost_standard=17.90,
            base_cost_discount=15.80,
            primary_countries=["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "NZ", "SE", "NO", "CH", "SG"],
            domestic_shipping=6.50,
            international_shipping=14.00,
            avg_production_days=2,
            avg_delivery_days_domestic=3,
            avg_delivery_days_intl=8,
            supports_branding=False,
        ),
    ),
    "matte_poster_18x24": CatalogItem(
        id="matte_poster_18x24",
        title="Museum-Quality Matte Paper Poster 18x24 Inch",
        category="Wall Art",
        recommended_retail=29.99,
        printify=PartnerProductProfile(
            partner="printify",
            partner_sku="pr-poster-18x24",
            base_cost_standard=7.20,
            base_cost_discount=5.76,
            primary_countries=["US", "GB", "DE", "AU"],
            domestic_shipping=5.20,
            international_shipping=12.50,
            avg_production_days=2,
            avg_delivery_days_domestic=4,
            avg_delivery_days_intl=12,
            supports_branding=False,
        ),
        gelato=PartnerProductProfile(
            partner="gelato",
            partner_sku="wall-art-poster-matte-18x24",
            base_cost_standard=6.80,
            base_cost_discount=5.90,
            primary_countries=["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "NZ", "SE", "NO", "DK", "JP", "SG", "IE"],
            domestic_shipping=4.50,
            international_shipping=7.50,
            avg_production_days=1,
            avg_delivery_days_domestic=3,
            avg_delivery_days_intl=6,
            supports_branding=False,
        ),
    ),
    "canvas_tote_heavy": CatalogItem(
        id="canvas_tote_heavy",
        title="Heavyweight 100% Cotton Canvas Market Tote",
        category="Accessories",
        recommended_retail=24.99,
        printify=PartnerProductProfile(
            partner="printify",
            partner_sku="pr-tote-heavy",
            base_cost_standard=7.20,
            base_cost_discount=5.76,
            primary_countries=["US", "GB"],
            domestic_shipping=4.49,
            international_shipping=9.99,
            avg_production_days=2,
            avg_delivery_days_domestic=4,
            avg_delivery_days_intl=12,
            supports_branding=True,
        ),
        gelato=PartnerProductProfile(
            partner="gelato",
            partner_sku="bags-tote-organic-cotton",
            base_cost_standard=7.90,
            base_cost_discount=6.90,
            primary_countries=["US", "CA", "GB", "DE", "FR", "AU"],
            domestic_shipping=4.20,
            international_shipping=7.80,
            avg_production_days=2,
            avg_delivery_days_domestic=3,
            avg_delivery_days_intl=7,
            supports_branding=False,
        ),
    ),
    "phone_case_tough": CatalogItem(
        id="phone_case_tough",
        title="Impact Dual-Layer Tough Phone Case (iPhone/Samsung)",
        category="Accessories",
        recommended_retail=27.99,
        printify=PartnerProductProfile(
            partner="printify",
            partner_sku="pr-case-tough",
            base_cost_standard=11.20,
            base_cost_discount=8.96,
            primary_countries=["US", "GB", "DE", "AU"],
            domestic_shipping=4.29,
            international_shipping=8.99,
            avg_production_days=2,
            avg_delivery_days_domestic=4,
            avg_delivery_days_intl=11,
            supports_branding=False,
        ),
        gelato=PartnerProductProfile(
            partner="gelato",
            partner_sku="cases-tough-phone-case",
            base_cost_standard=10.90,
            base_cost_discount=9.40,
            primary_countries=["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "NZ", "JP", "KR"],
            domestic_shipping=3.90,
            international_shipping=6.50,
            avg_production_days=1,
            avg_delivery_days_domestic=2,
            avg_delivery_days_intl=6,
            supports_branding=False,
        ),
    ),
    "glossy_sticker_3x3": CatalogItem(
        id="glossy_sticker_3x3",
        title="Die-Cut Waterproof Vinyl Glossy Sticker 3x3 Inch",
        category="Stationery",
        recommended_retail=5.99,
        printify=PartnerProductProfile(
            partner="printify",
            partner_sku="pr-sticker-3x3",
            base_cost_standard=1.80,
            base_cost_discount=1.44,
            primary_countries=["US", "GB"],
            domestic_shipping=3.49,
            international_shipping=6.99,
            avg_production_days=2,
            avg_delivery_days_domestic=4,
            avg_delivery_days_intl=12,
            supports_branding=False,
        ),
        gelato=PartnerProductProfile(
            partner="gelato",
            partner_sku="stationery-stickers-diecut-3x3",
            base_cost_standard=1.95,
            base_cost_discount=1.65,
            primary_countries=["US", "CA", "GB", "DE", "FR", "IT", "ES", "AU", "NZ", "SE", "NO", "JP"],
            domestic_shipping=2.90,
            international_shipping=4.90,
            avg_production_days=1,
            avg_delivery_days_domestic=2,
            avg_delivery_days_intl=5,
            supports_branding=False,
        ),
    ),
}


def get_all_products() -> List[Dict]:
    """Return dictionary list of all catalog matrix products."""
    result = []
    for item in CATALOG_MATRIX.values():
        result.append({
            "id": item.id,
            "title": item.title,
            "category": item.category,
            "recommended_retail": item.recommended_retail,
            "printify": {
                "base_standard": item.printify.base_cost_standard,
                "base_discount": item.printify.base_cost_discount,
                "domestic_countries": item.printify.primary_countries,
                "shipping_domestic": item.printify.domestic_shipping,
                "shipping_intl": item.printify.international_shipping,
                "delivery_days_domestic": item.printify.avg_delivery_days_domestic,
                "delivery_days_intl": item.printify.avg_delivery_days_intl,
            },
            "gelato": {
                "base_standard": item.gelato.base_cost_standard,
                "base_discount": item.gelato.base_cost_discount,
                "domestic_countries": item.gelato.primary_countries,
                "shipping_domestic": item.gelato.domestic_shipping,
                "shipping_intl": item.gelato.international_shipping,
                "delivery_days_domestic": item.gelato.avg_delivery_days_domestic,
                "delivery_days_intl": item.gelato.avg_delivery_days_intl,
            },
        })
    return result
