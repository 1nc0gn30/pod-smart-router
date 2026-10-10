/**
 * POD Smart Router - Kinetic Hero Canvas ("The Global Routing Astrolabe")
 * Pure HTML5 Canvas 60fps interactive visualizer with zero external dependencies.
 */

(function () {
  const canvas = document.getElementById("hero-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  let width, height;
  let animationFrameId;
  let mouse = { x: -1000, y: -1000, active: false };

  // Hub nodes representing distributed print networks
  const HUBS = [
    { id: "US-EAST", label: "US East (Printify/Gelato)", xRel: 0.28, yRel: 0.42, color: "#10B981", radius: 5.5 },
    { id: "US-WEST", label: "US West (Printify)", xRel: 0.18, yRel: 0.46, color: "#F59E0B", radius: 4.5 },
    { id: "UK", label: "London Hub (Gelato/Printify)", xRel: 0.48, yRel: 0.32, color: "#10B981", radius: 5.0 },
    { id: "DE", label: "Frankfurt Hub (Gelato)", xRel: 0.54, yRel: 0.35, color: "#3B82F6", radius: 5.0 },
    { id: "FR", label: "Paris Hub (Gelato Local)", xRel: 0.51, yRel: 0.38, color: "#10B981", radius: 4.5 },
    { id: "AU", label: "Sydney Hub (Gelato/Printify)", xRel: 0.85, yRel: 0.75, color: "#10B981", radius: 4.5 },
    { id: "JP", label: "Tokyo Hub (Gelato)", xRel: 0.82, yRel: 0.44, color: "#EC4899", radius: 4.5 },
  ];

  // Packets travelling between consumer pins and hubs
  const PACKETS = [];
  const MAX_PACKETS = 14;

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    width = canvas.width = rect.width;
    height = canvas.height = Math.max(280, rect.height || 360);
  }

  function createPacket() {
    const sourceIdx = Math.floor(Math.random() * HUBS.length);
    let targetIdx = Math.floor(Math.random() * HUBS.length);
    while (targetIdx === sourceIdx) {
      targetIdx = Math.floor(Math.random() * HUBS.length);
    }
    return {
      from: HUBS[sourceIdx],
      to: HUBS[targetIdx],
      progress: Math.random(),
      speed: 0.004 + Math.random() * 0.006,
      size: 2.2 + Math.random() * 1.5,
      hue: Math.random() > 0.5 ? "#10B981" : "#D4AF37"
    };
  }

  for (let i = 0; i < MAX_PACKETS; i++) {
    PACKETS.push(createPacket());
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);

    const time = performance.now() * 0.001;

    // Draw background orbital coordinate rings (Astrolabe circles)
    ctx.save();
    ctx.strokeStyle = "rgba(212, 175, 55, 0.08)";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 6]);

    const centerX = width * 0.5;
    const centerY = height * 0.5;
    const maxRadius = Math.min(width, height) * 0.46;

    for (let r = 0.3; r <= 1.0; r += 0.35) {
      ctx.beginPath();
      ctx.arc(centerX, centerY, maxRadius * r, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.restore();

    // Draw connection arcs between print hubs
    ctx.save();
    ctx.lineWidth = 1;
    for (let i = 0; i < HUBS.length; i++) {
      for (let j = i + 1; j < HUBS.length; j++) {
        const h1 = HUBS[i];
        const h2 = HUBS[j];
        const x1 = h1.xRel * width;
        const y1 = h1.yRel * height;
        const x2 = h2.xRel * width;
        const y2 = h2.yRel * height;

        ctx.strokeStyle = "rgba(255, 223, 112, 0.06)";
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.quadraticCurveTo((x1 + x2) / 2, (y1 + y2) / 2 - 25, x2, y2);
        ctx.stroke();
      }
    }
    ctx.restore();

    // Update and draw packets (routed orders)
    for (let p of PACKETS) {
      p.progress += p.speed;
      if (p.progress >= 1) {
        Object.assign(p, createPacket(), { progress: 0 });
      }

      const x1 = p.from.xRel * width;
      const y1 = p.from.yRel * height;
      const x2 = p.to.xRel * width;
      const y2 = p.to.yRel * height;
      const cx = (x1 + x2) / 2;
      const cy = (y1 + y2) / 2 - 25;

      const t = p.progress;
      const invT = 1 - t;
      const px = invT * invT * x1 + 2 * invT * t * cx + t * t * x2;
      const py = invT * invT * y1 + 2 * invT * t * cy + t * t * y2;

      ctx.save();
      ctx.fillStyle = p.hue;
      ctx.shadowColor = p.hue;
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.arc(px, py, p.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // Draw Hub Nodes
    let hoveredHub = null;
    for (let hub of HUBS) {
      const x = hub.xRel * width;
      const y = hub.yRel * height;
      const dist = Math.hypot(mouse.x - x, mouse.y - y);
      const isHovered = dist < 25;
      if (isHovered) hoveredHub = hub;

      const pulse = Math.sin(time * 3 + hub.xRel * 10) * 1.5;
      const r = hub.radius + (isHovered ? 2 : 0);

      // Glow halo
      ctx.save();
      ctx.fillStyle = hub.color;
      ctx.globalAlpha = 0.18;
      ctx.beginPath();
      ctx.arc(x, y, r + 7 + pulse, 0, Math.PI * 2);
      ctx.fill();

      // Node core
      ctx.globalAlpha = 0.95;
      ctx.shadowColor = hub.color;
      ctx.shadowBlur = isHovered ? 14 : 6;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      // Node label
      ctx.save();
      ctx.fillStyle = isHovered ? "#FFFFFF" : "rgba(226, 232, 240, 0.7)";
      ctx.font = isHovered ? "bold 11px 'Space Grotesk', sans-serif" : "10px 'Space Grotesk', sans-serif";
      ctx.fillText(hub.id, x + 8, y + 3);
      ctx.restore();
    }

    if (hoveredHub) {
      canvas.style.cursor = "pointer";
    } else {
      canvas.style.cursor = "default";
    }

    animationFrameId = requestAnimationFrame(draw);
  }

  window.addEventListener("resize", resize);
  canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
    mouse.active = true;
  });
  canvas.addEventListener("mouseleave", () => {
    mouse.x = -1000;
    mouse.y = -1000;
    mouse.active = false;
  });

  resize();
  draw();
})();
