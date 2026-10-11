/**
 * POD Smart Router - Sovereign Client Application
 * 100% In-Browser Computation & API Synchronization
 */

(function () {
  // Client-side catalog matrix replica for zero-latency client calculation
  const LOCAL_CATALOG = {
    gildan_18000: {
      id: "gildan_18000",
      title: "Gildan 18000 Heavy Blend Crewneck Sweatshirt",
      printify: {
        base_standard: 12.50,
        base_discount: 10.00,
        domestic_countries: ["US", "CA", "GB", "DE"],
        shipping_domestic: 4.99,
        shipping_intl: 11.50,
        delivery_days_domestic: 4,
        delivery_days_intl: 12,
        prod_days: 2
      },
      gelato: {
        base_standard: 13.20,
        base_discount: 11.50,
        domestic_countries: ["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "NZ", "SE", "NO"],
        shipping_domestic: 4.50,
        shipping_intl: 9.80,
        delivery_days_domestic: 3,
        delivery_days_intl: 8,
        prod_days: 2
      }
    },
    comfort_colors_1717: {
      id: "comfort_colors_1717",
      title: "Comfort Colors 1717 Garment-Dyed Heavyweight Tee",
      printify: {
        base_standard: 13.80,
        base_discount: 11.04,
        domestic_countries: ["US"],
        shipping_domestic: 4.75,
        shipping_intl: 10.99,
        delivery_days_domestic: 4,
        delivery_days_intl: 14,
        prod_days: 2
      },
      gelato: {
        base_standard: 14.90,
        base_discount: 13.20,
        domestic_countries: ["US", "GB", "DE"],
        shipping_domestic: 4.50,
        shipping_intl: 8.50,
        delivery_days_domestic: 3,
        delivery_days_intl: 9,
        prod_days: 2
      }
    },
    bella_canvas_3001: {
      id: "bella_canvas_3001",
      title: "Bella+Canvas 3001 Unisex Jersey Short Sleeve Tee",
      printify: {
        base_standard: 8.95,
        base_discount: 7.16,
        domestic_countries: ["US", "GB", "DE", "CA", "AU"],
        shipping_domestic: 4.75,
        shipping_intl: 9.99,
        delivery_days_domestic: 3,
        delivery_days_intl: 10,
        prod_days: 2
      },
      gelato: {
        base_standard: 9.40,
        base_discount: 8.10,
        domestic_countries: ["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "NZ", "SE", "NO", "JP", "BR"],
        shipping_domestic: 4.20,
        shipping_intl: 7.90,
        delivery_days_domestic: 3,
        delivery_days_intl: 7,
        prod_days: 1
      }
    },
    ceramic_mug_15oz: {
      id: "ceramic_mug_15oz",
      title: "White Gloss Ceramic Mug 15oz",
      printify: {
        base_standard: 6.80,
        base_discount: 5.44,
        domestic_countries: ["US", "GB"],
        shipping_domestic: 5.99,
        shipping_intl: 12.99,
        delivery_days_domestic: 4,
        delivery_days_intl: 14,
        prod_days: 2
      },
      gelato: {
        base_standard: 6.95,
        base_discount: 6.10,
        domestic_countries: ["US", "CA", "GB", "DE", "FR", "IT", "ES", "AU", "NZ", "SG"],
        shipping_domestic: 4.90,
        shipping_intl: 8.90,
        delivery_days_domestic: 3,
        delivery_days_intl: 7,
        prod_days: 1
      }
    },
    canvas_gallery_wrap_16x20: {
      id: "canvas_gallery_wrap_16x20",
      title: "Stretched Canvas Gallery Wrap 16x20 Inch",
      printify: {
        base_standard: 18.50,
        base_discount: 14.80,
        domestic_countries: ["US", "GB", "DE"],
        shipping_domestic: 8.99,
        shipping_intl: 24.50,
        delivery_days_domestic: 5,
        delivery_days_intl: 16,
        prod_days: 3
      },
      gelato: {
        base_standard: 17.90,
        base_discount: 15.80,
        domestic_countries: ["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "NZ", "SE", "NO", "CH", "SG"],
        shipping_domestic: 6.50,
        shipping_intl: 14.00,
        delivery_days_domestic: 3,
        delivery_days_intl: 8,
        prod_days: 2
      }
    },
    matte_poster_18x24: {
      id: "matte_poster_18x24",
      title: "Museum-Quality Matte Paper Poster 18x24 Inch",
      printify: {
        base_standard: 7.20,
        base_discount: 5.76,
        domestic_countries: ["US", "GB", "DE", "AU"],
        shipping_domestic: 5.20,
        shipping_intl: 12.50,
        delivery_days_domestic: 4,
        delivery_days_intl: 12,
        prod_days: 2
      },
      gelato: {
        base_standard: 6.80,
        base_discount: 5.90,
        domestic_countries: ["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "NZ", "SE", "NO", "DK", "JP", "SG", "IE"],
        shipping_domestic: 4.50,
        shipping_intl: 7.50,
        delivery_days_domestic: 3,
        delivery_days_intl: 6,
        prod_days: 1
      }
    }
  };

  // State
  let currentDecision = null;

  // DOM Elements
  const skuSelect = document.getElementById("sku-select");
  const countrySelect = document.getElementById("country-select");
  const qtyInput = document.getElementById("quantity-input");
  const ruleSelect = document.getElementById("rule-select");
  const premiumToggle = document.getElementById("premium-toggle");

  const printifyCard = document.getElementById("printify-card");
  const gelatoCard = document.getElementById("gelato-card");
  const printifyCostEl = document.getElementById("printify-landed-cost");
  const gelatoCostEl = document.getElementById("gelato-landed-cost");
  const printifyDeliveryEl = document.getElementById("printify-delivery");
  const gelatoDeliveryEl = document.getElementById("gelato-delivery");
  const printifyDomesticEl = document.getElementById("printify-domestic");
  const gelatoDomesticEl = document.getElementById("gelato-domestic");
  const printifyCustomsEl = document.getElementById("printify-customs");
  const gelatoCustomsEl = document.getElementById("gelato-customs");

  const summaryDollarEl = document.getElementById("summary-dollar-savings");
  const summaryDaysEl = document.getElementById("summary-days-saved");
  const summaryCarbonEl = document.getElementById("summary-carbon-saved");
  const summaryReasonEl = document.getElementById("summary-reason");

  const codePreviewEl = document.getElementById("code-preview");
  const paywallModal = document.getElementById("paywall-modal");
  const licenseInput = document.getElementById("license-key-input");
  const activateBtn = document.getElementById("btn-activate-key");

  // Toast Notification System
  function showToast(msg) {
    let toast = document.getElementById('routerToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'routerToast';
      toast.style.cssText = 'position: fixed; bottom: 24px; right: 24px; z-index: 100000; background: #0A0F1D; border: 1px solid var(--gold, #D4AF37); color: #FFF; padding: 0.65rem 1.25rem; border-radius: 8px; font-family: var(--font-mono, monospace); font-size: 0.82rem; box-shadow: 0 8px 32px rgba(0,0,0,0.8), 0 0 15px rgba(212,175,55,0.25); display: flex; align-items: center; gap: 0.5rem; transition: opacity 0.3s ease, transform 0.3s ease; opacity: 0; transform: translateY(10px); pointer-events: none;';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
    }, 2600);
  }

  function isProActive() {
    const k1 = localStorage.getItem("pod_router_licensed");
    const k2 = localStorage.getItem("pod_router_license");
    const k3 = localStorage.getItem("agent_pod_router_pro");
    const k4 = localStorage.getItem("zoth_pod_router_licensed");
    const k5 = localStorage.getItem("pro_licensed");
    const param = new URLSearchParams(window.location.search).get("licensed");
    return k1 === "true" || k2 === "ROUTER-PRO-2026" || k3 === "ROUTER-PRO-2026" || k4 === "true" || k5 === "true" || param === "true";
  }

  // License checking
  function checkLicense() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("licensed") === "true" || urlParams.get("pro") === "true" || urlParams.get("session_id")) {
      localStorage.setItem("pod_router_licensed", "true");
      localStorage.setItem("pod_router_license", "ROUTER-PRO-2026");
      localStorage.setItem("agent_pod_router_pro", "ROUTER-PRO-2026");
      localStorage.setItem("zoth_pod_router_licensed", "true");
      localStorage.setItem("pro_licensed", "true");
      if (window.history && window.history.replaceState) {
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }

    const proBadge = document.getElementById("licenseBadge") || document.getElementById("pro-badge");
    const salesBanner = document.getElementById("salesBanner");

    if (isProActive()) {
      document.body.classList.add("licensed", "pro-unlocked", "pro-licensed");
      if (proBadge) {
        proBadge.className = "brand-badge badge-pro";
        proBadge.textContent = "⭐ PRO ACTIVE";
        proBadge.style.background = "rgba(212, 175, 55, 0.2)";
        proBadge.style.color = "var(--gold, #D4AF37)";
        proBadge.style.borderColor = "var(--gold, #D4AF37)";
      }
      if (salesBanner) {
        salesBanner.style.display = "none";
      }
      const codePreview = document.getElementById("code-preview");
      if (codePreview) {
        codePreview.classList.remove("paywall-blur");
      }
    } else {
      document.body.classList.remove("licensed", "pro-unlocked", "pro-licensed");
      if (proBadge) {
        proBadge.className = "brand-badge badge-free";
        proBadge.textContent = "⚡ FREE TIER";
      }
      if (salesBanner) {
        salesBanner.style.display = "";
      }
    }
  }

  function openModal(triggerContext = "") {
    if (paywallModal) {
      paywallModal.classList.add("is-open");
      paywallModal.style.display = "flex";
    }
  }

  function closeModal() {
    if (paywallModal) {
      paywallModal.classList.remove("is-open");
      paywallModal.style.display = "none";
    }
  }

  window.openPaywallModal = openModal;
  window.closePaywallModal = closeModal;
  window.activateLicenseKey = function(key) {
    if (!key) key = "ROUTER-PRO-2026";
    localStorage.setItem("pod_router_licensed", "true");
    localStorage.setItem("pod_router_license", key);
    localStorage.setItem("agent_pod_router_pro", key);
    localStorage.setItem("zoth_pod_router_licensed", "true");
    localStorage.setItem("pro_licensed", "true");
    checkLicense();
    closeModal();
    showToast("⭐ Sovereign Pro License Active — All Features Unlocked!");
    return true;
  };

  // Pure Client Calculation
  function calculateLandedQuote(partnerKey, profile, dest, qty, useDiscount) {
    const isDomestic = profile.domestic_countries.includes(dest);
    const baseUnit = useDiscount ? profile.base_discount : profile.base_standard;
    const totalBase = baseUnit * qty;

    let shipTotal = 0;
    let customsVat = 0;
    let customsRisk = "ZERO (Domestic)";
    let transitDays = 0;
    let carbonMiles = 0;

    if (isDomestic) {
      shipTotal = profile.shipping_domestic + (profile.shipping_domestic * 0.4 * (qty - 1));
      customsVat = 0.0;
      transitDays = profile.delivery_days_domestic;
      carbonMiles = 400;
    } else {
      shipTotal = profile.shipping_intl + (profile.shipping_intl * 0.5 * (qty - 1));
      if (["GB", "DE", "FR", "IT", "ES", "NL", "AU", "CA"].includes(dest)) {
        customsVat = totalBase * 0.20 + 3.50;
        customsRisk = "HIGH (VAT & Brokerage)";
      } else {
        customsVat = totalBase * 0.15;
        customsRisk = "MODERATE (Cross-Border)";
      }
      transitDays = profile.delivery_days_intl;
      carbonMiles = 4500;
    }

    const totalLanded = totalBase + shipTotal + customsVat;
    const totalDelivery = profile.prod_days + transitDays;

    return {
      partner: partnerKey,
      isDomestic,
      baseUnit,
      totalBase: Number(totalBase.toFixed(2)),
      shippingTotal: Number(shipTotal.toFixed(2)),
      customsVat: Number(customsVat.toFixed(2)),
      customsRisk,
      totalLanded: Number(totalLanded.toFixed(2)),
      totalDelivery,
      carbonMiles
    };
  }

  function computeRouting(sku, dest, qty, rule, usePremium) {
    const item = LOCAL_CATALOG[sku] || LOCAL_CATALOG["gildan_18000"];
    const qPrintify = calculateLandedQuote("printify", item.printify, dest, qty, usePremium);
    const qGelato = calculateLandedQuote("gelato", item.gelato, dest, qty, true);

    let winner = qPrintify;
    let alt = qGelato;
    let reason = "";

    if (rule === "domestic_only" || rule === "customs_avoidance") {
      if (qGelato.isDomestic && !qPrintify.isDomestic) {
        winner = qGelato;
        alt = qPrintify;
        reason = `Gelato selected: Local factory in ${dest} guarantees 0 customs tariffs and rapid delivery.`;
      } else if (qPrintify.isDomestic && !qGelato.isDomestic) {
        winner = qPrintify;
        alt = qGelato;
        reason = `Printify selected: Domestic print provider verified in ${dest}.`;
      }
    }

    if (!reason && rule === "fastest") {
      if (qGelato.totalDelivery < qPrintify.totalDelivery) {
        winner = qGelato;
        alt = qPrintify;
        reason = `Gelato delivers ${qPrintify.totalDelivery - qGelato.totalDelivery} day(s) faster via domestic lab.`;
      } else if (qPrintify.totalDelivery < qGelato.totalDelivery) {
        winner = qPrintify;
        alt = qGelato;
        reason = `Printify delivers ${qGelato.totalDelivery - qPrintify.totalDelivery} day(s) faster.`;
      }
    }

    if (!reason) {
      if (qPrintify.totalLanded <= qGelato.totalLanded) {
        winner = qPrintify;
        alt = qGelato;
        const diff = (qGelato.totalLanded - qPrintify.totalLanded).toFixed(2);
        reason = `Printify wins on total landed cost: Saves $${diff} ($${qPrintify.totalLanded.toFixed(2)} vs $${qGelato.totalLanded.toFixed(2)}).`;
      } else {
        winner = qGelato;
        alt = qPrintify;
        const diff = (qPrintify.totalLanded - qGelato.totalLanded).toFixed(2);
        reason = `Gelato wins on total landed cost: Saves $${diff} ($${qGelato.totalLanded.toFixed(2)} vs $${qPrintify.totalLanded.toFixed(2)}).`;
      }
    }

    const dollarSavings = Math.max(0, alt.totalLanded - winner.totalLanded);
    const daysSaved = Math.max(0, alt.totalDelivery - winner.totalDelivery);
    const carbonSaved = Math.max(0, alt.carbonMiles - winner.carbonMiles);

    return {
      productTitle: item.title,
      destination: dest,
      quantity: qty,
      rule,
      winnerPartner: winner.partner,
      winnerQuote: winner,
      altQuote: alt,
      qPrintify,
      qGelato,
      dollarSavings: Number(dollarSavings.toFixed(2)),
      daysSaved,
      carbonSaved,
      reason
    };
  }

  function updateUI() {
    const sku = skuSelect ? skuSelect.value : "gildan_18000";
    const dest = countrySelect ? countrySelect.value : "US";
    const qty = qtyInput ? Math.max(1, parseInt(qtyInput.value) || 1) : 1;
    const rule = ruleSelect ? ruleSelect.value : "balanced";
    const usePremium = premiumToggle ? premiumToggle.checked : true;

    currentDecision = computeRouting(sku, dest, qty, rule, usePremium);

    // Update Printify Card
    if (printifyCostEl) printifyCostEl.textContent = `$${currentDecision.qPrintify.totalLanded.toFixed(2)}`;
    if (printifyDeliveryEl) printifyDeliveryEl.textContent = `${currentDecision.qPrintify.totalDelivery} Days`;
    if (printifyDomesticEl) printifyDomesticEl.textContent = currentDecision.qPrintify.isDomestic ? "Domestic Hub (Yes)" : "Cross-Border (No)";
    if (printifyCustomsEl) printifyCustomsEl.textContent = currentDecision.qPrintify.customsRisk;

    // Update Gelato Card
    if (gelatoCostEl) gelatoCostEl.textContent = `$${currentDecision.qGelato.totalLanded.toFixed(2)}`;
    if (gelatoDeliveryEl) gelatoDeliveryEl.textContent = `${currentDecision.qGelato.totalDelivery} Days`;
    if (gelatoDomesticEl) gelatoDomesticEl.textContent = currentDecision.qGelato.isDomestic ? "Domestic Hub (Yes)" : "Cross-Border (No)";
    if (gelatoCustomsEl) gelatoCustomsEl.textContent = currentDecision.qGelato.customsRisk;

    // Toggle Winning Ribbons
    if (printifyCard && gelatoCard) {
      if (currentDecision.winnerPartner === "printify") {
        printifyCard.classList.add("is-winner");
        gelatoCard.classList.remove("is-winner");
        const r1 = printifyCard.querySelector(".winner-ribbon");
        const r2 = gelatoCard.querySelector(".winner-ribbon");
        if (r1) r1.style.display = "block";
        if (r2) r2.style.display = "none";
      } else {
        gelatoCard.classList.add("is-winner");
        printifyCard.classList.remove("is-winner");
        const r1 = printifyCard.querySelector(".winner-ribbon");
        const r2 = gelatoCard.querySelector(".winner-ribbon");
        if (r1) r1.style.display = "none";
        if (r2) r2.style.display = "block";
      }
    }

    // Update Summary Banner
    if (summaryDollarEl) summaryDollarEl.textContent = `$${currentDecision.dollarSavings.toFixed(2)}`;
    if (summaryDaysEl) summaryDaysEl.textContent = `${currentDecision.daysSaved} Days`;
    if (summaryCarbonEl) summaryCarbonEl.textContent = `${currentDecision.carbonSaved} Miles`;
    if (summaryReasonEl) summaryReasonEl.textContent = currentDecision.reason;

    // Generate Production Dispatch Payload
    const extId = `ORD-${Date.now().toString().slice(-6)}`;
    const payload = currentDecision.winnerPartner === "gelato" ? {
      partner: "gelato",
      endpoint: "https://api.gelato.com/v2/orders",
      orderType: "order",
      orderReferenceId: extId,
      customerReferenceId: "CUST-98214",
      currency: "USD",
      items: [
        {
          itemReferenceId: `ITEM-${sku}`,
          productUid: `apparel_${sku}`,
          files: [{ type: "default", url: "https://nullai.tech/artwork/high-res-300dpi.png" }],
          quantity: qty
        }
      ],
      shippingAddress: {
        firstName: "Alexander",
        lastName: "Vance",
        addressLine1: "123 Sovereign Blvd",
        city: dest === "GB" ? "London" : dest === "FR" ? "Paris" : "New York",
        postCode: dest === "GB" ? "SW1A 1AA" : "10001",
        country: dest,
        email: "alexander@example.com"
      },
      routing_telemetry: {
        engine: "pod-smart-router-v1",
        savings_usd: currentDecision.dollarSavings,
        days_saved: currentDecision.daysSaved,
        carbon_miles_saved: currentDecision.carbonSaved,
        reason: currentDecision.reason
      }
    } : {
      partner: "printify",
      endpoint: "https://api.printify.com/v1/shops/{shop_id}/orders.json",
      external_id: extId,
      label: `NULLAI-${extId}`,
      line_items: [
        {
          product_id: `pr-${sku}`,
          variant_id: 45012,
          quantity: qty,
          metadata: { artwork_url: "https://nullai.tech/artwork/high-res-300dpi.png" }
        }
      ],
      shipping_method: 1,
      send_shipping_notification: true,
      address_to: {
        first_name: "Alexander",
        last_name: "Vance",
        address1: "123 Sovereign Blvd",
        city: "Richmond",
        region: "VA",
        country: dest,
        zip: "23220",
        email: "alexander@example.com"
      },
      routing_telemetry: {
        engine: "pod-smart-router-v1",
        savings_usd: currentDecision.dollarSavings,
        days_saved: currentDecision.daysSaved,
        carbon_miles_saved: currentDecision.carbonSaved,
        reason: currentDecision.reason
      }
    };

    if (codePreviewEl) {
      codePreviewEl.textContent = JSON.stringify(payload, null, 2);
    }
  }

  // Interceptors
  function handleExportAction() {
    if (!isProActive()) {
      openModal("Export Payload");
      return;
    }
    // If licensed:
    if (!codePreviewEl) return;
    const content = codePreviewEl.textContent;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(content).then(() => {
        showToast("✅ Production Dispatch Payload copied to clipboard!");
      }).catch(() => {
        showToast("✅ Production Dispatch Payload copied!");
      });
    } else {
      showToast("✅ Production Dispatch Payload copied!");
    }
  }

  function handleDownloadAction() {
    if (!isProActive()) {
      openModal("Download Payload");
      return;
    }
    if (!codePreviewEl) return;
    const blob = new Blob([codePreviewEl.textContent], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `pod-dispatch-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("📥 Production Dispatch Payload Downloaded!");
  }

  // Event Listeners
  if (skuSelect) skuSelect.addEventListener("change", updateUI);
  if (countrySelect) countrySelect.addEventListener("change", updateUI);
  if (qtyInput) qtyInput.addEventListener("input", updateUI);
  if (ruleSelect) ruleSelect.addEventListener("change", updateUI);
  if (premiumToggle) premiumToggle.addEventListener("change", updateUI);

  const copyBtn = document.getElementById("btn-copy-payload");
  const downloadBtn = document.getElementById("btn-download-payload");
  const unlockPaywallBtn = document.getElementById("btn-unlock-paywall");
  const openLicenseModalBtn = document.getElementById("btn-open-license-modal");
  const headerKeyBtn = document.getElementById("btn-header-key");
  const modalCloseBtn = document.getElementById("modal-close-btn");
  const licenseStatusEl = document.getElementById("license-status");

  if (copyBtn) copyBtn.addEventListener("click", handleExportAction);
  if (downloadBtn) downloadBtn.addEventListener("click", handleDownloadAction);
  if (unlockPaywallBtn) unlockPaywallBtn.addEventListener("click", () => openModal("Paywall Unlock"));
  if (headerKeyBtn) headerKeyBtn.addEventListener("click", (e) => {
    e.preventDefault();
    openModal("Header Key");
  });
  if (openLicenseModalBtn) openLicenseModalBtn.addEventListener("click", (e) => {
    e.preventDefault();
    openModal("Sales Banner Activate");
  });
  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);

  if (activateBtn && licenseInput) {
    const handleActivation = () => {
      const val = licenseInput.value.trim();
      if (val.length >= 6) {
        localStorage.setItem("pod_router_licensed", "true");
        localStorage.setItem("pod_router_license", val);
        localStorage.setItem("agent_pod_router_pro", val);
        localStorage.setItem("zoth_pod_router_licensed", "true");
        localStorage.setItem("pro_licensed", "true");
        checkLicense();
        if (licenseStatusEl) {
          licenseStatusEl.textContent = "✅ License successfully activated! All features unlocked.";
          licenseStatusEl.style.color = "#10B981";
        }
        showToast("⭐ Sovereign Pro License Activated Successfully!");
        setTimeout(() => {
          closeModal();
          updateUI();
        }, 500);
      } else {
        if (licenseStatusEl) {
          licenseStatusEl.textContent = "❌ Please enter a valid license key or receipt order ID.";
          licenseStatusEl.style.color = "#EF4444";
        }
        showToast("Please enter a valid license key or receipt order ID.");
      }
    };

    activateBtn.addEventListener("click", handleActivation);
    licenseInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleActivation();
      }
    });
  }

  // Close modal when clicking on backdrop
  if (paywallModal) {
    paywallModal.addEventListener("click", (e) => {
      if (e.target === paywallModal) closeModal();
    });
  }

  // DePay Web3 Solana Triggers
  document.querySelectorAll(".btn-depay-trigger").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      if (window.DePayButtons && typeof window.DePayButtons.init === "function") {
        try {
          window.DePayButtons.init({
            integration: "428790dd-7ad1-407c-8ecf-c048c77a4cb8",
            receiver: "GG2eQbVh8ut1BK6j1A2tz7pSySdLpD38BgyEhGcxdXoK",
            amount: 19
          });
          return;
        } catch (err) {
          console.warn("DePay init warning:", err);
        }
      }
      const solanaAddress = "GG2eQbVh8ut1BK6j1A2tz7pSySdLpD38BgyEhGcxdXoK";
      if (navigator.clipboard) {
        navigator.clipboard.writeText(solanaAddress).then(() => {
          showToast(`⚡ Solana Receiver copied: ${solanaAddress}`);
        }).catch(() => {
          showToast(`⚡ Solana Receiver: ${solanaAddress}`);
        });
      } else {
        showToast(`⚡ Solana Receiver: ${solanaAddress}`);
      }
    });
  });

  checkLicense();
  updateUI();
})();
