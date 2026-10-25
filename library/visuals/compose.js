// Compose: parts of a whole, bridges, funnels.
const L = require("../tools/lib.js");
const { C, text, rect, series, cats } = L;
const { chartIn } = require("./_kit.js");

const src = (ctx, b) => text(ctx, "Source", "Source", b.x, b.y + b.h - 0.3, b.w, 0.3, "caption", { optional: true });

module.exports = {
  family: "Compose",
  slides: [
    {
      id: "V-COM-01", name: "Waterfall bridge", category: "Compose", kind: "chart", frame: "wide",
      objective: "Break down", data_type: "Quantitative", dimensions: 1, complexity: "Medium",
      description: "Bridge from a starting total to an ending total through increases (dark) and decreases (light).",
      use_when: "Explain a variation: budget to actual, last year to this year, price walk.",
      limits: "Positive values only above zero. Fill with {\"categories\": [...], \"waterfall\": [start, +a, -b, end], \"totals\": [0, 3]}.",
      tags: "waterfall bridge walk variance contribution decomposition ebitda budget",
      related: "V-CMP-04 V-COM-02",
      fill_notes: "Chart: use the waterfall shortcut, the builder computes the hidden base.",
      draw(ctx, b) {
        const c = ["Start", "Driver 1", "Driver 2", "Driver 3", "Driver 4", "End"];
        chartIn(ctx, "Chart", "bar", series(["Base", "Total", "Increase", "Decrease"], c, [
          [0, 100, 120, 112, 112, 0], [100, 0, 0, 0, 0, 125], [0, 20, 0, 0, 13, 0], [0, 0, 8, 0, 0, 0],
        ]), b, {
          bottom: 0.35,
          extra: { barDir: "col", barGrouping: "stacked", barGapWidthPct: 40, chartColors: [C.none, C.a1, C.a3, C.a5], valGridLine: { color: C.line, size: 0.5 } },
        });
        src(ctx, b);
      },
    },
    {
      id: "V-COM-02", name: "Mix bars", category: "Compose", kind: "chart", frame: "wide",
      objective: "Break down", data_type: "Quantitative", dimensions: 2, complexity: "Low",
      description: "100% stacked horizontal bars showing the split of each item between components.",
      use_when: "Compare the mix (shares) across groups: channels by region, cost structure by unit.",
      limits: "Up to 5 components; totals are hidden, mention them in the text if they matter.",
      tags: "mix share split 100 percent stacked bars composition structure",
      related: "V-COM-03 V-COM-06",
      fill_notes: "Chart: categories = groups, one series per component (any unit, shown as %).",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "bar", series(["Component 1", "Component 2", "Component 3"], cats(5, "Group"),
          [[50, 40, 35, 30, 20], [30, 35, 40, 30, 45], [20, 25, 25, 40, 35]]), b, {
          bottom: 0.35, legend: true, values: true,
          extra: { barDir: "bar", barGrouping: "percentStacked", barGapWidthPct: 50, catAxisOrientation: "maxMin", chartColors: [C.a1, C.a3, C.a5], showValue: false },
        });
        src(ctx, b);
      },
    },
    {
      id: "V-COM-03", name: "Donut with total", category: "Compose", kind: "chart", frame: "half",
      objective: "Break down", data_type: "Quantitative", dimensions: 1, complexity: "Low",
      description: "Donut chart with the total written in the centre.",
      use_when: "Share of a total with 2 to 5 parts, when one part dominates.",
      limits: "More than 5 parts: use mix bars or ranked bars.",
      tags: "donut doughnut share split parts total proportion",
      related: "V-COM-04 V-COM-02",
      fill_notes: "Chart: categories = parts + one series. Total: text.",
      draw(ctx, b) {
        const d = Math.min(b.h - 0.5, b.w * 0.6);
        L.chart(ctx, "Chart", "doughnut", series(["Share"], ["Part 1", "Part 2", "Part 3", "Part 4"], [[45, 25, 18, 12]]),
          b.x, b.y, b.w, b.h - 0.35, { extra: { holeSize: 62, chartColors: [C.a1, C.a3, C.a4, C.a6], dataLabelColor: C.ink, dataLabelPosition: "outEnd", showPercent: true, showLabel: true, showValue: false, showLegend: false } });
        const cx = b.x + b.w / 2, cy = b.y + (b.h - 0.35) / 2;
        text(ctx, "Total", "000", cx - 0.9, cy - 0.42, 1.8, 0.55, "h3", { size: 24, align: "center", valign: "middle" });
        text(ctx, "Total label", "Total", cx - 0.9, cy + 0.12, 1.8, 0.3, "caption", { align: "center", optional: true });
        src(ctx, b);
        void d;
      },
    },
    {
      id: "V-COM-04", name: "Simple pie", category: "Compose", kind: "chart", frame: "half",
      objective: "Break down", data_type: "Quantitative", dimensions: 1, complexity: "Low",
      description: "Pie with two or three very unequal parts and their percentages.",
      use_when: "One clear majority versus the rest (\"two thirds of customers...\").",
      limits: "Two or three parts only; otherwise use a donut or bars.",
      tags: "pie share majority part proportion simple",
      related: "V-COM-03",
      fill_notes: "Chart: categories = parts + one series.",
      draw(ctx, b) {
        L.chart(ctx, "Chart", "pie", series(["Share"], ["Part 1", "Part 2"], [[68, 32]]), b.x, b.y, b.w, b.h - 0.35,
          { legend: true, legendPos: "r", extra: { chartColors: [C.a1, C.a5], showPercent: true, showValue: false, dataLabelColor: C.ink, dataLabelPosition: "outEnd", firstSliceAng: 0 } });
        src(ctx, b);
      },
    },
    {
      id: "V-COM-05", name: "Funnel", category: "Compose", kind: "diagram", frame: "wide",
      objective: "Break down", data_type: "Sequential", dimensions: 1, complexity: "Low",
      description: "Five stacked stages narrowing downwards, each with its label, value and conversion.",
      use_when: "Conversion through successive stages: marketing, sales, recruitment, validation.",
      limits: "Bar widths are decorative; the values carry the information.",
      tags: "funnel conversion stages pipeline drop off leads sales recruitment",
      related: "V-PRO-01 V-COM-02",
      fill_notes: "Text: Stage n, Value n, Rate n.",
      draw(ctx, b) {
        const n = 5, h = (b.h - 0.5) / n, wMax = b.w * 0.55;
        for (let i = 0; i < n; i++) {
          const w = wMax * (1 - i * 0.16), x = b.x + (wMax - w) / 2, y = b.y + i * h;
          rect(ctx, x, y + 0.04, w, h - 0.08, { fill: ["a1", "a2", "a3", "a4", "a5"][i], follows: `Stage ${i + 1}` });
          text(ctx, `Value ${i + 1}`, "00", x, y + 0.04, w, h - 0.08, "h3", { size: 16, align: "center", valign: "middle", color: i < 2 ? "paper" : "ink", optional: i > 2 });
          text(ctx, `Stage ${i + 1}`, `Stage ${i + 1}`, b.x + wMax + 0.3, y + 0.04, b.w * 0.25, h - 0.08, "small", { bold: true, color: "ink", valign: "middle", optional: i > 2 });
          if (i) text(ctx, `Rate ${i}`, "00%", b.x + wMax + 0.3 + b.w * 0.26, y - h / 2 + 0.04, b.w - wMax - 0.3 - b.w * 0.26, h - 0.08, "caption", { valign: "middle", optional: true });
        }
        src(ctx, b);
      },
    },
    {
      id: "V-COM-06", name: "Stacked columns", category: "Compose", kind: "chart", frame: "wide",
      objective: "Break down", data_type: "Time series", dimensions: 2, complexity: "Low",
      description: "Columns stacked by component over a few periods.",
      use_when: "Total and its composition for 3 to 8 periods (revenue by product per year).",
      limits: "Up to 4 components; keep the most important at the bottom.",
      tags: "stacked columns composition periods total breakdown years",
      related: "V-EVO-02 V-COM-02",
      fill_notes: "Chart: categories = periods, one series per component.",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "bar", series(["Component 1", "Component 2", "Component 3"], ["P1", "P2", "P3", "P4", "P5"],
          [[20, 24, 27, 31, 35], [12, 13, 15, 15, 18], [6, 8, 9, 11, 12]]), b, {
          bottom: 0.35, legend: true,
          extra: { barDir: "col", barGrouping: "stacked", barGapWidthPct: 55, chartColors: [C.a1, C.a3, C.a5] },
        });
        src(ctx, b);
      },
    },
  ],
};
