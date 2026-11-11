<p align="center">
  <img src="assets/banner.png" alt="POD Smart Router: Autonomous Print-on-Demand order routing engine across Printify and Gelato" width="100%" />
</p>

# POD Smart Router

Zero-dependency Python 3.10+ order routing engine and domestic cost optimizer for print-on-demand sellers: automated carrier and production partner routing (Printify vs. Gelato), multi-currency landed cost optimization, customs tariff avoidance, production API dispatch payload generation, loopback HTTP workstation, and a 4-tool MCP stdio server.

- Zoth Studio v2 dossier: https://zoth.nullai.tech/tools/pod-smart-router
- Local workstation: `http://127.0.0.1:8117`
- Runtime dependencies: none (Python standard library only)
- License: MIT

## What It Does

- **Multi-partner routing**: Dynamically evaluates wholesale pricing, regional manufacturing hubs, shipping lead times, and customs borders across Printify and Gelato to pick the optimal supplier.
- **Rule-based decision policies**:
  - `balanced`: Blends landed wholesale cost, shipping speed, and customs avoidance.
  - `cheapest`: Prioritizes lowest absolute landed wholesale plus carrier cost.
  - `fastest`: Prioritizes shortest delivery window.
  - `domestic_only`: Enforces domestic fulfillment inside the recipient's country.
  - `customs_avoidance`: Avoids cross-border customs declarations and tariffs.
- **Catalog benchmark matrix**: Side-by-side pricing, domestic hub counts, and lead times across 10 benchmark apparel, drinkware, and home decor products.
- **Dispatch payload generator**: Compiles verified production API request JSON for Printify v1 orders and Gelato v2 orders.
- **Environmental savings**: Quantifies estimated ground versus air transit miles saved by domestic fulfillment.

## How It Works

```text
src/pod_smart_router/
├── catalog_matrix.py   # Benchmark product specs and regional hub availability
├── router.py           # Core routing decision engine and scoring algorithms
├── payload_gen.py      # Production API dispatch payload generators (Printify & Gelato)
├── partner_client.py   # Partner API client abstraction
├── mcp_server.py       # MCP stdio server (JSON-RPC 2.0: initialize, tools/list, tools/call)
├── server.py           # Loopback HTTP API + static workstation from public/
└── cli.py              # `pod-smart-router` entry point
bin/pod-smart-router         # Runs the CLI from checkout
public/                      # Browser workstation (routing playground and dispatch preview)
```

The HTTP server only accepts browser requests from `localhost` / `127.0.0.1` / `[::1]` origins and binds to `127.0.0.1` by default.

## Install

```bash
git clone https://github.com/1nc0gn30/pod-smart-router.git
cd pod-smart-router
pip install -e .
```

Or run directly without installation via the runner script:

```bash
./bin/pod-smart-router --help
```

## Configuration

The core routing engine and catalog benchmarks run completely offline with no API keys or environment variables required.

Optional environment variables:
- `POD_ROUTER_PORT`: Custom listening port for the HTTP daemon (default: `8117`).
- `ZOTH_BIND_HOST`: Custom bind interface (default: `127.0.0.1`).
- `PRINTIFY_API_TOKEN`: Printify API token for live shop queries.
- `GELATO_API_KEY`: Gelato API key for live order submission.

## CLI reference

```bash
# Check service status and routing rules
pod-smart-router status
pod-smart-router --json

# Calculate optimal route for a Gildan 18000 sweatshirt shipped to the UK
pod-smart-router route --sku gildan_18000 --country GB --rule balanced

# View side-by-side catalog matrix across Printify and Gelato
pod-smart-router matrix

# Generate production API dispatch payload
pod-smart-router dispatch --sku gildan_18000 --country GB

# Launch local HTTP workstation
pod-smart-router server --port 8117
```

## MCP/REST reference

### MCP stdio tools

When registered in an MCP host (such as Antigravity or Claude Desktop):
- `route_order`: Calculates optimal fulfillment partner, landed costs, savings, and delivery estimate.
- `get_catalog_matrix`: Returns side-by-side product pricing and regional hub availability.
- `generate_dispatch_payload`: Constructs production-ready Printify or Gelato API request bodies.
- `evaluate_destination_hubs`: Analyzes local manufacturing presence for a given destination country code.

### REST endpoints

- `GET /health` - Service health and partner availability status.
- `GET /api/catalog/matrix` - Benchmark product catalog.
- `GET /api/destinations` - Supported destination country codes.
- `GET /api/rules` - Supported decision policies.
- `POST /api/route` - Order routing request JSON payload.
- `POST /api/dispatch` - Production dispatch JSON generator.

## Port

Default HTTP port: `8117`.

## License

MIT License. Engineered by [1nc0gn30](https://1nc0gn30.si) • [NullAI Platform](https://nullai.tech). 100% Free and Open-Source.
Optional tip link: [Buy Us a Coffee](https://buy.stripe.com/3cIfZg27PdKo2D64Ocfw40X).
