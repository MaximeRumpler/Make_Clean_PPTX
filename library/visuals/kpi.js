// KPI: figures, progress, status.
const L = require("../tools/lib.js");
const { C, text, rect, ellipse, hrule, series } = L;

const periods = (n) => Array.from({ length: n }, (_, i) => `P${i + 1}`);

module.exports = {
  family: "KPI",
  slides: [
    {
      id: "V-KPI-01", name: "KPI cards with change", category: "KPI", kind: "diagram", frame: "wide",
      objective: "Track performance", data_type: "Quantitative", dimensions: 2, complexity: "Low",
      description: "Three cards with a figure, its label and the change against a reference.",
      use_when: "A compact scorecard inside a slide that also carries text or a chart.",
      limits: "Three figures; for more use layout L-39.",
      tags: "kpi cards figures change delta variation scorecard metrics",
      related: "V-KPI-03 V-KPI-02",
      fill_notes: "Text: Value n, Label n, Change n.",
      draw(ctx, b) {
        const gap = 0.25, w = (b.w - 2 * gap) / 3, h = Math.min(b.h, 2.4);
        for (let i = 0; i < 3; i++) {
          const x = b.x + i * (w + gap);
          rect(ctx, x, b.y, w, h, { fill: "surface" });
          rect(ctx, x, b.y, w, 0.06, { fill: i === 0 ? "a1" : "a4" });
          text(ctx, `Value ${i + 1}`, "00", x + 0.25, b.y + 0.3, w - 0.5, 0.9, "number", { size: 40, optional: i > 0 });
          text(ctx, `Label ${i + 1}`, "What is measured", x + 0.25, b.y + 1.25, w - 0.5, 0.45, "small", { bold: true, color: "ink", optional: i > 0 });
          text(ctx, `Change ${i + 1}`, "+0% vs reference", x + 0.25, b.y + 1.7, w - 0.5, 0.45, "caption", { optional: true });
        }
      },
    },
    {
      id: "V-KPI-02", name: "Progress rings", category: "KPI", kind: "chart", frame: "wide",
      objective: "Track performance", data_type: "Quantitative", dimensions: 1, complexity: "Low",
      description: "Three rings, each filled to a percentage, with the figure in the centre and a label below.",
      use_when: "Completion or achievement rates (percent of target, percent done).",
      limits: "Percentages only. Fill each ring with {\"categories\": [\"Done\", \"Left\"], \"series\": {\"Rate\": [72, 28]}}.",
      tags: "progress rings completion rate percentage achievement donut gauge",
      related: "V-KPI-05 V-CMP-03",
      fill_notes: "Ring n (chart: two values summing to 100), Value n, Label n.",
      draw(ctx, b) {
        const gap = 0.3, w = (b.w - 2 * gap) / 3, d = Math.min(w, b.h - 0.9);
        [72, 48, 90].forEach((v, i) => {
          const x = b.x + i * (w + gap) + (w - d) / 2;
          L.chart(ctx, `Ring ${i + 1}`, "doughnut", series(["Rate"], ["Done", "Left"], [[v, 100 - v]]), x, b.y, d, d,
            { optional: i > 0, extra: { holeSize: 75, chartColors: [C.a1, C.a6], showValue: false, showPercent: false, showLegend: false, firstSliceAng: 0 } });
          text(ctx, `Value ${i + 1}`, "00%", x, b.y + d / 2 - 0.3, d, 0.6, "h3", { size: 22, align: "center", valign: "middle", optional: i > 0 });
          text(ctx, `Label ${i + 1}`, "What is measured", b.x + i * (w + gap), b.y + d + 0.1, w, 0.6, "small", { align: "center", optional: i > 0 });
        });
      },
    },
    {
      id: "V-KPI-03", name: "Figure with trend", category: "KPI", kind: "chart", frame: "half",
      objective: "Track performance", data_type: "Time series", dimensions: 1, complexity: "Low",
      description: "One large figure with its label, change and a small area chart of its recent trend.",
      use_when: "The headline figure of a slide, with just enough history to show the direction.",
      limits: "One indicator per component.",
      tags: "kpi figure trend sparkline headline number history",
      related: "V-KPI-01 V-EVO-05",
      fill_notes: "Text: Value, Label, Change. Chart: categories + one series.",
      draw(ctx, b) {
        text(ctx, "Value", "00", b.x, b.y, b.w, 1.1, "display", { size: 60 });
        text(ctx, "Label", "What is measured", b.x, b.y + 1.15, b.w, 0.4, "body", { bold: true, color: "ink" });
        text(ctx, "Change", "+0% vs reference", b.x, b.y + 1.55, b.w, 0.35, "caption", { optional: true });
        L.chart(ctx, "Chart", "area", series(["Value"], periods(12), [[12, 14, 13, 15, 16, 15, 18, 19, 21, 20, 23, 25]]),
          b.x, b.y + 2.0, b.w, b.h - 2.0, { extra: { chartColors: [C.a5], valAxisHidden: true, catAxisHidden: true, valGridLine: { style: "none" }, catAxisLineShow: false } });
      },
    },
    {
      id: "V-KPI-04", name: "Status list", category: "KPI", kind: "table", frame: "wide",
      objective: "Track performance", data_type: "Ordinal", dimensions: 2, complexity: "Low",
      description: "Rows with a status dot, an item name, a short comment and an owner.",
      use_when: "Project or programme status report (on track, at risk, late).",
      limits: "Status is shown by shade: {\"text\": \"\", \"fill\": \"a1\"} late, \"a3\" at risk, \"a5\" on track; explain the code in the note.",
      tags: "status rag traffic light project report on track at risk late",
      related: "V-FRM-04 V-TIM-03",
      fill_notes: "Status n as {\"text\":\"\",\"fill\":...}; Item n, Comment n, Owner n as text.",
      draw(ctx, b) {
        const n = 6, rh = (b.h - 0.75) / n;
        text(ctx, "Header item", "Item", b.x + 0.5, b.y, b.w * 0.35, 0.3, "label", { keep: true });
        text(ctx, "Header comment", "Comment", b.x + 0.5 + b.w * 0.36, b.y, b.w * 0.4, 0.3, "label", { keep: true });
        text(ctx, "Header owner", "Owner", b.x + b.w * 0.8, b.y, b.w * 0.2, 0.3, "label", { keep: true });
        hrule(ctx, b.x, b.y + 0.35, b.w, { color: "ink", w: 1.25 });
        for (let i = 0; i < n; i++) {
          const y = b.y + 0.4 + i * rh;
          text(ctx, `Status ${i + 1}`, " ", b.x + 0.05, y + rh / 2 - 0.13, 0.26, 0.26, "caption", { shape: "ellipse", fill: ["a5", "a5", "a3", "a5", "a1", "a5"][i], optional: true, limit: 2 });
          text(ctx, `Item ${i + 1}`, "Item", b.x + 0.5, y, b.w * 0.35, rh, "small", { bold: true, color: "ink", valign: "middle", optional: i > 1 });
          text(ctx, `Comment ${i + 1}`, "Short comment", b.x + 0.5 + b.w * 0.36, y, b.w * 0.42, rh, "caption", { color: "ink2", valign: "middle", optional: true });
          text(ctx, `Owner ${i + 1}`, "Owner", b.x + b.w * 0.8, y, b.w * 0.2, rh, "caption", { valign: "middle", optional: true });
          hrule(ctx, b.x, y + rh, b.w, { color: "line", follows: `Item ${i + 1}` });
        }
        text(ctx, "Note", "Black: late · grey: at risk · light: on track", b.x, b.y + b.h - 0.3, b.w, 0.3, "caption", { optional: true, keep: true });
      },
    },
    {
      id: "V-KPI-05", name: "Gauge", category: "KPI", kind: "chart", frame: "half",
      objective: "Track performance", data_type: "Quantitative", dimensions: 1, complexity: "Low",
      description: "Half-ring gauge filled to a percentage, figure in the centre, scale ends below.",
      use_when: "One rate against its maximum: capacity used, satisfaction score, budget consumed.",
      limits: "One value; never use several gauges to compare (use bars). Fill {\"categories\": [\"Value\", \"Rest\", \"Hidden\"], \"series\": {\"Gauge\": [v, 100 - v, 100]}}.",
      tags: "gauge meter dial half donut rate capacity score",
      related: "V-KPI-02",
      fill_notes: "Chart: three values (value, remainder, 100 hidden). Value, Label: text.",
      draw(ctx, b) {
        const d = Math.min(b.w, (b.h - 0.6) * 2);
        const x = b.x + (b.w - d) / 2;
        L.chart(ctx, "Chart", "doughnut", series(["Gauge"], ["Value", "Rest", "Hidden"], [[65, 35, 100]]), x, b.y, d, d,
          { extra: { holeSize: 65, chartColors: [C.a1, C.a6, C.none], firstSliceAng: 270, showValue: false, showLegend: false } });
        text(ctx, "Value", "00%", x, b.y + d / 2 - 0.85, d, 0.8, "display", { size: 40, align: "center", valign: "bottom" });
        text(ctx, "Label", "What is measured", x, b.y + d / 2 + 0.05, d, 0.45, "small", { align: "center" });
        void rect; void ellipse;
      },
    },
  ],
};
