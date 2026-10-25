// Evolve: change over time.
const L = require("../tools/lib.js");
const { C, text, hrule, series } = L;
const { chartIn } = require("./_kit.js");

const src = (ctx, b) => text(ctx, "Source", "Source", b.x, b.y + b.h - 0.3, b.w, 0.3, "caption", { optional: true });
const periods = (n) => Array.from({ length: n }, (_, i) => `P${i + 1}`);

module.exports = {
  family: "Evolve",
  slides: [
    {
      id: "V-EVO-01", name: "Line with annotation", category: "Evolve", kind: "chart", frame: "wide",
      objective: "Show change", data_type: "Time series", dimensions: 1, complexity: "Low",
      description: "One bold line over time with a callout explaining the key moment.",
      use_when: "A trend and the event that explains it (launch, crisis, policy change).",
      limits: "One or two series; move the callout next to the moment it explains.",
      tags: "line trend evolution time series annotation event over time",
      related: "V-EVO-04 V-EVO-06",
      fill_notes: "Chart: categories = periods + one series. Callout: text.",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "line", series(["Value"], periods(12), [[20, 22, 21, 25, 27, 26, 30, 36, 41, 43, 46, 50]]), b, {
          bottom: 0.35, extra: { lineSize: 2.5, lineDataSymbol: "none", chartColors: [C.a1] },
        });
        hrule(ctx, b.x + b.w * 0.55, b.y + 0.35, 0.5, { color: "ink", w: 1.5 });
        text(ctx, "Callout", "What happened at this point", b.x + b.w * 0.55, b.y + 0.45, b.w * 0.3, 0.6, "small", { optional: true });
        src(ctx, b);
      },
    },
    {
      id: "V-EVO-02", name: "Stacked area", category: "Evolve", kind: "chart", frame: "wide",
      objective: "Show change", data_type: "Time series", dimensions: 2, complexity: "Medium",
      description: "Stacked areas showing how a total and its components evolve.",
      use_when: "Growth of a total and the changing weight of 2 to 4 components.",
      limits: "Only the bottom layer reads accurately; keep the key component at the bottom.",
      tags: "stacked area composition over time mix evolution total components",
      related: "V-COM-06 V-EVO-03",
      fill_notes: "Chart: categories = periods + one series per component.",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "area", series(["Component 1", "Component 2", "Component 3"], periods(8),
          [[20, 22, 25, 27, 30, 33, 35, 38], [12, 13, 14, 16, 17, 18, 20, 21], [6, 7, 7, 8, 9, 10, 10, 11]]), b, {
          bottom: 0.35, legend: true, extra: { barGrouping: "stacked", chartColors: [C.a1, C.a3, C.a5] },
        });
        src(ctx, b);
      },
    },
    {
      id: "V-EVO-03", name: "Columns and line", category: "Evolve", kind: "chart", frame: "wide",
      objective: "Show change", data_type: "Time series", dimensions: 2, complexity: "Medium",
      description: "Columns for a volume, a line on a second axis for a rate.",
      use_when: "Volume and ratio together: revenue and margin, users and conversion.",
      limits: "Two different units; label both axes in the note.",
      tags: "combo columns line dual axis volume rate margin",
      related: "V-EVO-01 V-REL-05",
      fill_notes: "Chart: categories + series Volume (columns) and Rate (line).",
      draw(ctx, b) {
        const cats = periods(6);
        const top = 0.0;
        ctx.s.addChart(
          [
            { type: L.pres.ChartType.bar, data: [{ name: "Volume", labels: cats, values: [30, 34, 33, 40, 44, 50] }], options: { chartColors: [C.a4], barGapWidthPct: 60 } },
            { type: L.pres.ChartType.line, data: [{ name: "Rate", labels: cats, values: [12, 13, 11, 15, 17, 18] }], options: { chartColors: [C.a1], lineSize: 2.5, lineDataSymbol: "circle", secondaryValAxis: true, secondaryCatAxis: true } },
          ],
          Object.assign({}, {
            x: b.x, y: b.y + top, w: b.w, h: b.h - 0.35, objectName: ctx.name("Chart"),
            catAxisLabelFontFace: L.FONT.body, valAxisLabelFontFace: L.FONT.body, legendFontFace: L.FONT.body,
            catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, legendFontSize: 10,
            catAxisLabelColor: C.muted, valAxisLabelColor: C.muted, legendColor: C.ink2,
            valGridLine: { color: C.line, size: 0.5 }, showLegend: true, legendPos: "t",
            valAxes: [{ showValAxisTitle: false, valAxisLabelColor: C.muted }, { showValAxisTitle: false, valGridLine: { style: "none" }, valAxisLabelColor: C.muted }],
            catAxes: [{ catAxisTitle: "" }, { catAxisHidden: true }],
          })
        );
        ctx.field({ name: "Chart", type: "chart", hint: "combo bar+line", x: b.x, y: b.y, w: b.w, h: b.h - 0.35, placeholder: "Chart data" });
        src(ctx, b);
      },
    },
    {
      id: "V-EVO-04", name: "Plan versus actual", category: "Evolve", kind: "chart", frame: "wide",
      objective: "Track performance", data_type: "Time series", dimensions: 2, complexity: "Low",
      description: "Cumulative plan as a light line, actual as a bold line that stops at today.",
      use_when: "Project progress, budget burn, cumulative sales against plan (S-curve).",
      limits: "Leave future actual values empty so the line stops at today.",
      tags: "plan actual s curve cumulative progress budget burn tracking forecast",
      related: "V-CMP-03 V-EVO-01",
      fill_notes: "Chart: categories = periods + series Plan and Actual.",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "line", series(["Plan", "Actual"], periods(10),
          [[5, 12, 22, 35, 50, 64, 76, 86, 94, 100], [4, 10, 18, 29, 41, 52, null, null, null, null]]), b, {
          bottom: 0.35, legend: true, extra: { lineSize: 2.5, lineDataSymbol: "none", chartColors: [C.a4, C.a1] },
        });
        src(ctx, b);
      },
    },
    {
      id: "V-EVO-05", name: "Trend table", category: "Evolve", kind: "chart", frame: "wide",
      objective: "Track performance", data_type: "Time series", dimensions: 2, complexity: "Medium",
      description: "Four rows: indicator name, current value and a small trend line.",
      use_when: "Several indicators whose direction matters more than their detail.",
      limits: "Each mini chart is filled separately (Trend 1 to Trend 4).",
      tags: "sparklines trend table indicators small lines monitoring",
      related: "V-KPI-03 V-EVO-06",
      fill_notes: "Text: Indicator n, Value n. Charts: Trend n (categories + one series).",
      draw(ctx, b) {
        const rowH = (b.h - 0.6) / 4;
        text(ctx, "Header 1", "Indicator", b.x, b.y, b.w * 0.4, 0.3, "label", { keep: true });
        text(ctx, "Header 2", "Current", b.x + b.w * 0.4, b.y, b.w * 0.2, 0.3, "label", { keep: true });
        text(ctx, "Header 3", "Trend", b.x + b.w * 0.62, b.y, b.w * 0.38, 0.3, "label", { keep: true });
        hrule(ctx, b.x, b.y + 0.35, b.w, { color: "ink", w: 1.25 });
        for (let i = 0; i < 4; i++) {
          const y = b.y + 0.4 + i * rowH;
          text(ctx, `Indicator ${i + 1}`, "Indicator name", b.x, y, b.w * 0.38, rowH, "small", { valign: "middle", optional: i > 1 });
          text(ctx, `Value ${i + 1}`, "00", b.x + b.w * 0.4, y, b.w * 0.2, rowH, "h3", { size: 20, valign: "middle", optional: i > 1 });
          L.chart(ctx, `Trend ${i + 1}`, "line", series(["Value"], periods(8), [[3, 4, 3, 5, 6, 5, 7, 8].map((v) => v + i)]),
            b.x + b.w * 0.62, y + 0.08, b.w * 0.38, rowH - 0.16, {
              optional: i > 1,
              extra: { lineSize: 1.75, lineDataSymbol: "none", chartColors: [C.a1], valAxisHidden: true, catAxisHidden: true, valGridLine: { style: "none" }, catAxisLineShow: false },
            });
          hrule(ctx, b.x, y + rowH, b.w, { color: "line", follows: `Indicator ${i + 1}` });
        }
      },
    },
    {
      id: "V-EVO-06", name: "Small multiples", category: "Evolve", kind: "chart", frame: "full",
      objective: "Show change", data_type: "Time series", dimensions: 3, complexity: "Medium",
      description: "Three small line charts on the same scale, side by side, each with its own heading.",
      use_when: "The same trend for several segments; avoids a tangle of lines on one chart.",
      limits: "Keep the same axis scale in all three for a fair comparison.",
      tags: "small multiples segments panels trends comparison lines facets",
      related: "V-EVO-01 V-EVO-05",
      fill_notes: "Heading n + Panel n (chart: categories + one series) for n = 1..3.",
      draw(ctx, b) {
        const gap = 0.35, w = (b.w - 2 * gap) / 3;
        for (let i = 0; i < 3; i++) {
          const x = b.x + i * (w + gap);
          text(ctx, `Heading ${i + 1}`, `Segment ${i + 1}`, x, b.y, w, 0.35, "small", { bold: true, color: "ink", optional: i > 1 });
          hrule(ctx, x, b.y + 0.4, w, { color: "ink", w: 1 });
          L.chart(ctx, `Panel ${i + 1}`, "line", series(["Value"], periods(8), [[10, 12, 13, 15, 14, 17, 19, 21].map((v) => v + i * 4 - (i === 2 ? 8 : 0))]),
            x, b.y + 0.5, w, b.h - 0.85, { optional: i > 1, extra: { lineSize: 2, lineDataSymbol: "none", chartColors: [C.a1], valAxisMinVal: 0, valAxisMaxVal: 30 } });
        }
        src(ctx, b);
      },
    },
  ],
};
