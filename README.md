# POD Smart Router

Picks Printify or Gelato for each print-on-demand order by comparing landed
cost (base + shipping + estimated customs/VAT), delivery days and whether the
partner has a factory in the destination country. Pure Python stdlib.

## Use

```bash
PYTHONPATH=src python3 -m pod_smart_router.cli route --sku ceramic_mug_15oz --country DE --qty 2 --rule balanced
PYTHONPATH=src python3 -m pod_smart_router.cli matrix          # catalog + partner costs
PYTHONPATH=src python3 -m pod_smart_router.cli dispatch --sku gildan_18000 --country GB   # prints a payload, sends nothing
PYTHONPATH=src python3 -m pod_smart_router.cli server --port 8117                          # web UI + /api/route, /api/dispatch
```

An MCP stdio server lives in `src/pod_smart_router/mcp_server.py`
(`pod_route_order` and friends).

## Routing rules

| Rule | Picks |
| --- | --- |
| `cheapest` | lowest total landed cost |
| `fastest` | fewest total delivery days (ties fall back to cost) |
| `balanced` (default) | keeps a domestic, zero-customs factory whenever either partner has one, then minimises landed cost + $0.50 per delivery day |
| `domestic_only` / `customs_avoidance` | the partner with a factory in the destination, if only one has it; otherwise cheapest |

Inputs are validated: an unknown or ambiguous SKU (`ceramic_mug` -> 11oz or
15oz?) raises `UnknownSKUError` with suggestions instead of silently routing a
different product. Countries must be ISO alpha-2 and quantity >= 1.

SKUs: `gildan_18000`, `comfort_colors_1717`, `bella_canvas_3001`,
`ceramic_mug_15oz`, `ceramic_mug_11oz`, `canvas_gallery_wrap_16x20`,
`matte_poster_18x24`, `canvas_tote_heavy`, `phone_case_tough`, `glossy_sticker_3x3`.

## Test

```bash
python3 -m pytest -q tests/
```

## Network exposure

The server binds to `127.0.0.1` by default. To reach it from other devices,
opt in explicitly with `--host 0.0.0.0` (or set `ZOTH_BIND_HOST=0.0.0.0`; an IP
in `HOST` is also honoured, a plain hostname is ignored) and only on a trusted
network.
