// Frameworks: classic management canvases.
const L = require("../tools/lib.js");
const { C, text, rect, line, hrule, vrule } = L;
const { card, arrow } = require("./_kit.js");

module.exports = {
  family: "Frameworks",
  slides: [
    {
      id: "V-FRM-01", name: "Business model canvas", category: "Frameworks", kind: "diagram", frame: "full",
      objective: "Describe a structure", data_type: "Qualitative", dimensions: 9, complexity: "Medium",
      description: "The nine blocks of the business model canvas in their standard arrangement.",
      use_when: "Describe or compare business models.",
      limits: "A few words per block; the canvas is dense by nature.",
      tags: "business model canvas bmc value proposition segments revenue costs osterwalder",
      related: "V-FRM-06 V-STR-04",
      fill_notes: "Block n text (headings are the standard block names).",
      draw(ctx, b) {
        const c5 = b.w / 5, top = (b.h - 0.08) * 0.68, bot = b.h - top - 0.08, half = (top - 0.08) / 2;
        const blocks = [
          ["Key partners", 0, 0, 1, top], ["Key activities", 1, 0, 1, half], ["Key resources", 1, half + 0.08, 1, half],
          ["Value propositions", 2, 0, 1, top], ["Customer relationships", 3, 0, 1, half], ["Channels", 3, half + 0.08, 1, half],
          ["Customer segments", 4, 0, 1, top],
        ];
        blocks.forEach(([n, cx, y, cw, h], i) => card(ctx, `Block ${i + 1}`, b.x + cx * c5 + 0.04, b.y + y, cw * c5 - 0.08, h, { heading: n, fill: n === "Value propositions" ? "a1" : "surface" }));
        card(ctx, "Block 8", b.x + 0.04, b.y + top + 0.08, b.w / 2 - 0.08, bot, { heading: "Cost structure" });
        card(ctx, "Block 9", b.x + b.w / 2 + 0.04, b.y + top + 0.08, b.w / 2 - 0.08, bot, { heading: "Revenue streams" });
      },
    },
    {
      id: "V-FRM-02", name: "Five forces", category: "Frameworks", kind: "diagram", frame: "full",
      objective: "Diagnose", data_type: "Qualitative", dimensions: 5, complexity: "Medium",
      description: "Industry rivalry in the centre, the four outside forces around it with arrows pointing inwards.",
      use_when: "Assess the attractiveness of an industry or segment.",
      limits: "Rate each force in its text (low, medium, high).",
      tags: "five forces porter industry rivalry suppliers buyers substitutes entrants competition",
      related: "V-MAT-02 V-FRM-03",
      fill_notes: "Force n text (headings are the standard forces).",
      draw(ctx, b) {
        const w = 3.3, h = 1.25, cx = b.x + b.w / 2, cy = b.y + b.h / 2;
        card(ctx, "Force 1", cx - w / 2, cy - h / 2, w, h, { heading: "Industry rivalry", fill: "a1" });
        const pos = [["Threat of new entrants", cx - w / 2, b.y], ["Bargaining power of suppliers", b.x, cy - h / 2], ["Bargaining power of buyers", b.x + b.w - w, cy - h / 2], ["Threat of substitutes", cx - w / 2, b.y + b.h - h]];
        pos.forEach(([n, x, y], i) => card(ctx, `Force ${i + 2}`, x, y, w, h, { heading: n }));
        arrow(ctx, cx, b.y + h, cx, cy - h / 2 - 0.05);
        arrow(ctx, cx, b.y + b.h - h, cx, cy + h / 2 + 0.05);
        arrow(ctx, b.x + w, cy, cx - w / 2 - 0.05, cy);
        arrow(ctx, b.x + b.w - w, cy, cx + w / 2 + 0.05, cy);
      },
    },
    {
      id: "V-FRM-03", name: "PESTEL", category: "Frameworks", kind: "diagram", frame: "full",
      objective: "Diagnose", data_type: "Qualitative", dimensions: 6, complexity: "Low",
      description: "Six columns for political, economic, social, technological, environmental and legal factors.",
      use_when: "Scan the external environment before a strategy or a market entry.",
      limits: "Two or three factors per column.",
      tags: "pestel pestle macro environment political economic social technological environmental legal",
      related: "V-MAT-02 V-FRM-02",
      fill_notes: "Factor n (bullets).",
      draw(ctx, b) {
        const names = ["Political", "Economic", "Social", "Technological", "Environmental", "Legal"];
        const gap = 0.12, w = (b.w - gap * 5) / 6;
        names.forEach((n, i) => {
          const x = b.x + i * (w + gap);
          text(ctx, `Letter ${i + 1}`, n[0], x, b.y, w, 0.9, "display", { size: 40, fill: "a1", role: "keyfigure", color: "paper", align: "center", valign: "middle", keep: true });
          text(ctx, `Heading ${i + 1}`, n, x, b.y + 0.95, w, 0.4, "small", { bold: true, color: "ink", align: "center", keep: true });
          rect(ctx, x, b.y + 1.4, w, b.h - 1.4, { fill: "surface", role: "card", for: `Factor ${i + 1}` });
          text(ctx, `Factor ${i + 1}`, ["Factor", "Factor"], x + 0.12, b.y + 1.55, w - 0.24, b.h - 1.7, "caption", { bullets: true, color: "ink2" });
        });
      },
    },
    {
      id: "V-FRM-04", name: "RACI matrix", category: "Frameworks", kind: "table", frame: "full",
      objective: "Describe a structure", data_type: "Relational", dimensions: 2, complexity: "Medium",
      description: "Activities in rows, roles in columns, R, A, C or I in each cell; R and A shaded darker.",
      use_when: "Clarify who is responsible, accountable, consulted and informed.",
      limits: "One A per row. Use {\"text\": \"A\", \"fill\": \"a1\"} to shade a cell.",
      tags: "raci responsibility accountable consulted informed roles governance matrix",
      related: "V-PRO-03 V-STR-01",
      fill_notes: "Role n, Activity n, Cell r-c (R/A/C/I, optional fill).",
      draw(ctx, b) {
        const nR = 6, nC = 5, labW = 3.8, cw = (b.w - labW) / nC, rh = (b.h - 0.85) / nR;
        const letters = ["R", "A", "C", "I", "", "C"];
        for (let c = 0; c < nC; c++) text(ctx, `Role ${c + 1}`, `Role ${c + 1}`, b.x + labW + c * cw, b.y, cw, 0.5, "small", { bold: true, color: "ink", align: "center", valign: "bottom", optional: c > 1 });
        hrule(ctx, b.x, b.y + 0.55, b.w, { color: "ink", w: 1.25 });
        for (let r = 0; r < nR; r++) {
          const y = b.y + 0.6 + r * rh;
          text(ctx, `Activity ${r + 1}`, `Activity ${r + 1}`, b.x, y, labW - 0.2, rh, "small", { valign: "middle", optional: r > 1 });
          for (let c = 0; c < nC; c++) {
            const t = letters[(r + c) % letters.length], strong = t === "A" || t === "R";
            text(ctx, `Cell ${r + 1}-${c + 1}`, t || " ", b.x + labW + c * cw + 0.08, y + 0.05, cw - 0.16, rh - 0.1, "small",
              { fill: t === "A" ? "a1" : t === "R" ? "a2" : "surface", color: strong ? "paper" : "ink", bold: true, align: "center", valign: "middle", optional: true, limit: 2 });
          }
        }
        text(ctx, "Note", "R responsible · A accountable · C consulted · I informed", b.x, b.y + b.h - 0.25, b.w, 0.25, "caption", { optional: true, keep: true });
      },
    },
    {
      id: "V-FRM-05", name: "OKR tree", category: "Frameworks", kind: "diagram", frame: "full",
      objective: "Track performance", data_type: "Hierarchical", dimensions: 2, complexity: "Low",
      description: "One objective on top, three key results below, each with its target and progress.",
      use_when: "Present objectives and key results, or any goal with measurable outcomes.",
      limits: "One objective per component; three key results.",
      tags: "okr objectives key results goals targets measurable outcomes",
      related: "V-STR-02 V-KPI-02",
      fill_notes: "Objective, Key result n, Target n, Progress n.",
      draw(ctx, b) {
        text(ctx, "Objective label", "Objective", b.x, b.y, 2, 0.3, "label", { keep: true });
        text(ctx, "Objective", "Qualitative, inspiring objective", b.x, b.y + 0.35, b.w, 0.9, "h3", { size: 20, fill: "a1", role: "callout", color: "paper", inset: 0.2, valign: "middle" });
        const gap = 0.3, w = (b.w - 2 * gap) / 3;
        for (let i = 0; i < 3; i++) {
          const x = b.x + i * (w + gap), y = b.y + 1.65;
          vrule(ctx, x + w / 2, b.y + 1.25, 0.4, { color: "ink" });
          rect(ctx, x, y, w, b.h - 1.65, { fill: "surface", role: "card", for: `Key result ${i + 1}` });
          text(ctx, `Key result ${i + 1} label`, `Key result ${i + 1}`, x + 0.2, y + 0.2, w - 0.4, 0.3, "label", { color: "ink", keep: true });
          text(ctx, `Key result ${i + 1}`, "Measurable result", x + 0.2, y + 0.55, w - 0.4, 0.9, "small", { bold: true, color: "ink" });
          text(ctx, `Target ${i + 1}`, "Target", x + 0.2, y + 1.5, w - 0.4, 0.35, "caption", { optional: true });
          text(ctx, `Progress ${i + 1}`, "00%", x + 0.2, y + 1.9, w - 0.4, 0.7, "number", { size: 30, optional: true });
        }
      },
    },
    {
      id: "V-FRM-06", name: "Value chain", category: "Frameworks", kind: "diagram", frame: "full",
      objective: "Describe a process", data_type: "Sequential", dimensions: 2, complexity: "Medium",
      description: "Support activities as bars on top, five primary activities as chevrons below, margin at the end.",
      use_when: "Where value is created in a company; locate costs, strengths or improvements.",
      limits: "Standard Porter structure; rename activities to fit the business.",
      tags: "value chain porter primary support activities margin operations",
      related: "V-PRO-01 V-FRM-01",
      fill_notes: "Support n, Primary n, Margin.",
      draw(ctx, b) {
        const mw = 1.2, aw = b.w - mw, sh = (b.h * 0.5 - 0.2) / 4;
        ["Firm infrastructure", "People", "Technology", "Procurement"].forEach((n, i) =>
          text(ctx, `Support ${i + 1}`, n, b.x, b.y + i * (sh + 0.05), aw - 0.1, sh, "small", { fill: i % 2 ? "a6" : "surface", role: "card", color: "ink", valign: "middle", inset: 0.15, keep: true }));
        const py = b.y + b.h * 0.5 + 0.05, ph = b.h * 0.5 - 0.05, n = 5, ov = 0.2, w = (aw + ov * (n - 1)) / n;
        ["Inbound", "Operations", "Outbound", "Marketing and sales", "Service"].forEach((nm, i) =>
          text(ctx, `Primary ${i + 1}`, nm, b.x + i * (w - ov), py, w, ph, "small", { shape: i === 0 ? "homePlate" : "chevron", fill: "a2", color: "paper", bold: true, align: "center", valign: "middle", inset: 0.08, keep: true }));
        text(ctx, "Margin", "Margin", b.x + aw, b.y, mw, b.h, "small", { shape: "homePlate", fill: "a1", color: "paper", bold: true, align: "center", valign: "middle", keep: true });
      },
    },
  ],
};
