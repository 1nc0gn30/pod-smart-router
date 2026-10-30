<div align="center">
  <img src="assets/banner.png" alt="POD Smart Router — Sovereign Architecture Banner" width="100%" />
</div>

<br />

<div align="center">
  <a href="https://zoth.nullai.tech/tools/pod-smart-router"><img src="https://img.shields.io/badge/Zoth_Studio_v2-Workspace-D4AF37?style=for-the-badge&logo=sparkles&logoColor=black" alt="Zoth Studio Workspace" /></a>
  <a href="http://127.0.0.1:8117"><img src="https://img.shields.io/badge/ZothOS_v3.3-Port_:8117-38BDF8?style=for-the-badge&logo=linux&logoColor=black" alt="Port :8117" /></a>
  <a href="https://nullai.tech"><img src="https://img.shields.io/badge/Security-100%25_Zero--Egress-10B981?style=for-the-badge&logo=shield&logoColor=black" alt="Zero Egress" /></a>
  <a href="https://buy.stripe.com/3cIfZg27PdKo2D64Ocfw40X"><img src="https://img.shields.io/badge/☕_Buy_Us_a_Coffee-Stripe-D4AF37?style=for-the-badge" alt="Buy Us a Coffee" /></a>
</div>

# ⚡ POD Smart Router (v2.5.0)

> **Autonomous multi-channel Print-on-Demand order router dynamically evaluating Printify (:8115) vs Gelato (:8116) on landed cost, domestic proximity, delivery speed, and tariff avoidance.**

---

## 🏛️ Architectural Overview

**POD Smart Router** is a core commercial sovereignty engine in the **[Zoth Studio v2](https://zoth.nullai.tech)** arsenal and **[ZothOS Linux 3.3](https://zothos.nullai.tech)** ecosystem, engineered by **Neal Frazier Tech ([@1nc0gn30](https://github.com/1nc0gn30))**.

| Property | Specification |
| :--- | :--- |
| **Tool ID** | `pod-smart-router` |
| **Category** | `Commerce & MCP` |
| **Local Port** | `http://127.0.0.1:8117` |
| **Execution Mode** | Native Python Daemon & Browser Client |
| **Zoth Studio Route** | `http://127.0.0.1:3000/tools/pod-smart-router` |
| **License** | 100% Free & Open Access (Zero Paywalls) |

---

## 💎 What It Does & How It Works

- **Dynamic Cross-Provider Optimization**: Analyzes order SKUs against the combined catalog matrices of Printify and Gelato to identify lowest wholesale cost, fastest transit time, and zero-duty local fulfillment hubs across 32 countries.
- **Rules-Based Routing Engine**:
  - `cheapest`: Maximum margin via lowest landed cost (base cost + shipping + tariffs).
  - `fastest`: Minimizes customer delivery days using proximate domestic labs.
  - `balanced`: Default sovereign heuristic guaranteeing domestic fulfillment and zero customer import tariffs.
  - `domestic_only`: Enforces domestic fulfillment within the customer's country.
  - `customs_avoidance`: Rejects cross-border dispatches that incur import VAT or clearance delays.
- **Production API Dispatch Payloads**: Emits ready-to-transmit JSON payloads for Printify Order API and Gelato Order API with address normalization.
- **Zero-Egress Sovereign Privacy**: Operates entirely on loopback (`127.0.0.1:8117`) without sending private customer addresses or billing telemetry to third-party tracking services.

---

## 🚀 Quick Start

```bash
# Clone and launch the standalone daemon on port 8117
git clone https://github.com/1nc0gn30/pod-smart-router.git
cd pod-smart-router
python3 server.py --port 8117

# In another terminal, query the API or CLI
curl -s http://127.0.0.1:8117/health
curl -s http://127.0.0.1:8117/api/catalog/matrix
```

---

## 💻 ZothOS CLI & MCP Commands

The sovereign binary `pod-smart-router` is pre-installed in `/usr/local/bin` and `~/.local/bin`:

```bash
# Check status and version
pod-smart-router --version
pod-smart-router --status
pod-smart-router --json

# Calculate optimal routing decision
pod-smart-router route --sku gildan_18000 --country US --qty 2 --rule balanced
pod-smart-router route --sku bella_canvas_3001 --country GB --rule fastest --json

# Inspect cross-provider catalog matrix
pod-smart-router matrix
pod-smart-router matrix --json

# Generate production API dispatch payload
pod-smart-router dispatch --sku comfort_colors_1717 --country DE --artwork "https://example.com/art.png"

# Launch local HTTP daemon
pod-smart-router server --port 8117
```

---

## ☕ 100% Free & Open-Access Support Architecture

Every tool engineered by Neal Frazier Tech is **100% free, open, and unlocked by default**. There are zero paywalls, zero license locks, and zero feature gates.

If this tool empowers your business or automates your print fleet, consider supporting development:

- **☕ Buy Us a Coffee (Stripe)**: [https://buy.stripe.com/3cIfZg27PdKo2D64Ocfw40X](https://buy.stripe.com/3cIfZg27PdKo2D64Ocfw40X)
- **◎ Solana Tip Address**: `GG2eQbVh8ut1BK6j1A2tz7pSySdLpD38BgyEhGcxdXoK`

---

<div align="center">
  <sub>Engineered by <b>Neal Frazier Tech</b> (<a href="https://github.com/1nc0gn30">@1nc0gn30</a>) &bull; <a href="https://nullai.tech">NullAI Platform</a> &bull; <a href="https://zoth.nullai.tech">Zoth Studio v2</a></sub>
</div>
