// Relate: distributions, correlations, concentrations.
const L = require("../tools/lib.js");
const { C, text, rect, series } = L;
const { chartIn } = require("./_kit.js");

const src = (ctx, b) => text(ctx, "Source", "Source", b.x, b.y + b.h - 0.3, b.w, 0.3, "caption", { optional: true });

module.exports = {
  family: "Relate",
  slides: [
    {
      id: "V-REL-01", name: "Scatter plot", category: "Relate", kind: "chart", frame: "wide",
      objective: "Show relationship", data_type: "Quantitative", dimensions: 2, complexity: "Medium",
      description: "Points placed by two measures, to reveal a correlation or outliers.",
      use_when: "Is X linked to Y? Price and volume, effort and result, size and growth.",
      limits: "Correlation is not causation; name both axes in the note.",
      tags: "scatter correlation relationship two measures outliers dots xy",
      related: "V-REL-02 V-MAT-06",
      fill_notes: "Chart: scatter data, first series = X values, next series = Y values.",
      draw(ctx, b) {
        const xs = [2, 3, 3.5, 4, 5, 5.5, 6, 7, 7.5, 8, 9];
        chartIn(ctx, "Chart", "scatter", [{ name: "X", values: xs }, { name: "Y", values: [3, 4, 3.6, 5, 5.2, 6.4, 6, 7.4, 6.8, 8.1, 8.5] }], b, {
          bottom: 0.35, extra: { lineSize: 0, lineDataSymbol: "circle", lineDataSymbolSize: 9, chartColors: [C.a1], valGridLine: { color: C.line, size: 0.5 } },
        });
        text(ctx, "Note", "X axis: measure 1 · Y axis: measure 2", b.x, b.y + b.h - 0.3, b.w, 0.3, "caption", { optional: true });
      },
    },
    {
      id: "V-REL-02", name: "Bubble portfolio", category: "Relate", kind: "chart", frame: "wide",
      objective: "Prioritise", data_type: "Quantitative", dimensions: 3, complexity: "High",
      description: "Bubbles placed on two axes, bubble size for a third measure (portfolio view).",
      use_when: "Portfolio of products, projects or markets: attractiveness, position and size.",
      limits: "Up to 12 bubbles; explain what the size means in the note.",
      tags: "bubble portfolio three measures bcg size attractiveness position",
      related: "V-REL-01 V-MAT-01",
      fill_notes: "Chart: bubble data, series X, then Y with sizes.",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "bubble", [
          { name: "X", values: [2, 4, 5, 7, 8] },
          { name: "Y", values: [6, 3, 7, 5, 8], sizes: [4, 8, 5, 10, 3] },
        ], b, { bottom: 0.35, extra: { chartColors: [C.a3], chartColorsOpacity: 70 } });
        text(ctx, "Note", "X: measure 1 · Y: measure 2 · size: measure 3", b.x, b.y + b.h - 0.3, b.w, 0.3, "caption", { optional: true });
      },
    },
    {
      id: "V-REL-03", name: "Histogram", category: "Relate", kind: "chart", frame: "wide",
      objective: "Show distribution", data_type: "Quantitative", dimensions: 1, complexity: "Medium",
      description: "Adjacent columns counting how many values fall in each range.",
      use_when: "How values are spread: delays, order sizes, ages, scores.",
      limits: "Ranges must be equal and contiguous; give the unit in the categories.",
      tags: "histogram distribution spread frequency ranges bins dispersion",
      related: "V-REL-01 V-COM-06",
      fill_notes: "Chart: categories = ranges + one series of counts.",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "bar", series(["Count"], ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70"], [[3, 8, 15, 22, 14, 7, 2]]), b, {
          bottom: 0.35, extra: { barDir: "col", barGapWidthPct: 6, chartColors: [C.a2] },
        });
        src(ctx, b);
      },
    },
    {
      id: "V-REL-04", name: "Heatmap grid", category: "Relate", kind: "table", frame: "full",
      objective: "Show distribution", data_type: "Quantitative", dimensions: 2, complexity: "Medium",
      description: "Grid of cells, rows by columns, each cell shaded by its value and showing the number.",
      use_when: "Intensity across two dimensions: activity by day and hour, sales by product and region, cohort retention.",
      limits: "Shade cells with {\"text\": \"42\", \"fill\": \"a1\"} (high) to \"a6\" (low); dark cells need light text, the builder handles it.",
      tags: "heatmap grid intensity matrix cohort retention shading cells two dimensions",
      related: "V-CMP-06 V-MAT-04",
      fill_notes: "Text: Row n, Column n. Cells: Cell r-c as {\"text\", \"fill\"}.",
      draw(ctx, b) {
        const nR = 5, nC = 6, labW = 2.2, cw = (b.w - labW) / nC, rh = (b.h - 0.75) / nR;
        const shade = ["a1", "a2", "a3", "a4", "a5", "a6"];
        for (let c = 0; c < nC; c++) text(ctx, `Column ${c + 1}`, `Column ${c + 1}`, b.x + labW + c * cw, b.y, cw, 0.35, "caption", { align: "center", color: "ink2", optional: c > 1 });
        for (let r = 0; r < nR; r++) {
          const y = b.y + 0.4 + r * rh;
          text(ctx, `Row ${r + 1}`, `Row ${r + 1}`, b.x, y, labW - 0.15, rh, "small", { valign: "middle", optional: r > 1 });
          for (let c = 0; c < nC; c++) {
            const s = shade[Math.min(5, Math.abs(r - c) + (r % 2))];
            text(ctx, `Cell ${r + 1}-${c + 1}`, "00", b.x + labW + c * cw + 0.02, y + 0.02, cw - 0.04, rh - 0.04, "caption",
              { fill: s, color: ["a1", "a2"].includes(s) ? "paper" : "ink", align: "center", valign: "middle", optional: true, limit: 6 });
          }
        }
        src(ctx, b);
      },
    },
    {
      id: "V-REL-05", name: "Pareto", category: "Relate", kind: "chart", frame: "wide",
      objective: "Prioritise", data_type: "Quantitative", dimensions: 2, complexity: "Medium",
      description: "Sorted columns with a cumulative percentage line on a second axis.",
      use_when: "Find the few causes that explain most of the effect (80/20).",
      limits: "Sort categories descending; cumulative line in % from 0 to 100.",
      tags: "pareto 80 20 causes concentration cumulative quality priorities",
      related: "V-CMP-01 V-EVO-03",
      fill_notes: "Chart: categories + series Count (columns) and Cumulative % (line).",
      draw(ctx, b) {
        const cats = ["Cause 1", "Cause 2", "Cause 3", "Cause 4", "Cause 5", "Cause 6"];
        ctx.s.addChart(
          [
            { type: L.pres.ChartType.bar, data: [{ name: "Count", labels: cats, values: [42, 26, 14, 9, 6, 3] }], options: { chartColors: [C.a2], barGapWidthPct: 20 } },
            { type: L.pres.ChartType.line, data: [{ name: "Cumulative %", labels: cats, values: [42, 68, 82, 91, 97, 100] }], options: { chartColors: [C.a1], lineSize: 2, lineDataSymbol: "circle", secondaryValAxis: true, secondaryCatAxis: true } },
          ],
          {
            x: b.x, y: b.y, w: b.w, h: b.h - 0.35, objectName: ctx.name("Chart"),
            catAxisLabelFontFace: L.FONT.body, valAxisLabelFontFace: L.FONT.body, legendFontFace: L.FONT.body,
            catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, legendFontSize: 10, catAxisLabelColor: C.muted, legendColor: C.ink2,
            valGridLine: { color: C.line, size: 0.5 }, showLegend: true, legendPos: "t",
            valAxes: [{ valAxisLabelColor: C.muted }, { valAxisMaxVal: 100, valAxisMinVal: 0, valGridLine: { style: "none" }, valAxisLabelColor: C.muted }],
            catAxes: [{ catAxisTitle: "" }, { catAxisHidden: true }],
          }
        );
        ctx.field({ name: "Chart", type: "chart", hint: "combo bar+line", x: b.x, y: b.y, w: b.w, h: b.h - 0.35, placeholder: "Chart data" });
        src(ctx, b);
        void rect;
      },
    },
  ],
};
