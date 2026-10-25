// Compare: rank, compare periods, gaps to target, sensitivities, scores.
const L = require("../tools/lib.js");
const { C, text, rect, hrule, series, cats } = L;
const { chartIn } = require("./_kit.js");

const src = (ctx, b) => text(ctx, "Source", "Source", b.x, b.y + b.h - 0.3, b.w, 0.3, "caption", { optional: true });

module.exports = {
  family: "Compare",
  slides: [
    {
      id: "V-CMP-01", name: "Ranked bars", category: "Compare", kind: "chart", frame: "wide",
      objective: "Compare", data_type: "Quantitative", dimensions: 1, complexity: "Low",
      description: "Horizontal bars sorted from largest to smallest, values at the end of each bar.",
      use_when: "Rank items on one measure (regions, products, causes). Best with 3 to 12 items.",
      limits: "One measure only; sort the data before filling.",
      tags: "ranking bars horizontal sorted top leaderboard compare items",
      related: "V-CMP-02 V-COM-02",
      fill_notes: "Chart: categories + one series, sorted descending.",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "bar", series(["Value"], cats(6, "Item"), [[42, 36, 31, 24, 18, 12]]), b, {
          bottom: 0.35, values: true,
          extra: { barDir: "bar", catAxisOrientation: "maxMin", valAxisHidden: true, valGridLine: { style: "none" }, barGapWidthPct: 55, chartColors: [C.a1] },
        });
        src(ctx, b);
      },
    },
    {
      id: "V-CMP-02", name: "Two periods", category: "Compare", kind: "chart", frame: "wide",
      objective: "Compare", data_type: "Quantitative", dimensions: 2, complexity: "Low",
      description: "Clustered columns: previous period in grey, current period in black, values on top.",
      use_when: "Same items measured at two moments (year on year, before and after).",
      limits: "Up to 8 categories; for more periods use a line chart.",
      tags: "compare periods year on year before after columns clustered two series",
      related: "V-CMP-05 V-EVO-03",
      fill_notes: "Chart: categories + two series (previous, current).",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "bar", series(["Previous", "Current"], cats(5), [[30, 42, 25, 18, 36], [36, 40, 31, 24, 44]]), b, {
          bottom: 0.35, values: true, legend: true,
          extra: { barDir: "col", barGapWidthPct: 70, chartColors: [C.a4, C.a1], valAxisHidden: true, valGridLine: { style: "none" } },
        });
        src(ctx, b);
      },
    },
    {
      id: "V-CMP-03", name: "Progress to target", category: "Compare", kind: "chart", frame: "wide",
      objective: "Track performance", data_type: "Quantitative", dimensions: 2, complexity: "Low",
      description: "For each item a light bar shows the target and a dark bar over it shows the actual value.",
      use_when: "Achievement against objectives for several teams, projects or indicators.",
      limits: "Actual above target hides the light bar; say so in the text.",
      tags: "target objective achievement progress actual versus goal bullet",
      related: "V-KPI-02 V-CMP-01",
      fill_notes: "Chart: categories + series Target then Actual (same unit).",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "bar", series(["Target", "Actual"], cats(5, "Item"), [[100, 100, 100, 100, 100], [92, 78, 64, 55, 40]]), b, {
          bottom: 0.35, legend: true,
          extra: { barDir: "bar", barOverlapPct: 100, barGapWidthPct: 60, catAxisOrientation: "maxMin", chartColors: [C.a6, C.a1] },
        });
        src(ctx, b);
      },
    },
    {
      id: "V-CMP-04", name: "Sensitivity tornado", category: "Compare", kind: "chart", frame: "wide",
      objective: "Assess risk", data_type: "Quantitative", dimensions: 2, complexity: "Medium",
      description: "Bars extending left (downside) and right (upside) of a central axis, largest effect on top.",
      use_when: "Which assumptions move the result most: sensitivity analysis, risk drivers.",
      limits: "Enter downside values as negative numbers; sort by total swing.",
      tags: "tornado sensitivity upside downside risk drivers assumptions swing",
      related: "V-COM-01 V-MAT-04",
      fill_notes: "Chart: categories + series Downside (negative) and Upside (positive).",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "bar", series(["Downside", "Upside"], cats(5, "Driver"), [[-30, -22, -16, -10, -6], [26, 20, 14, 12, 5]]), b, {
          bottom: 0.35, legend: true, values: true,
          extra: { barDir: "bar", barOverlapPct: 100, barGapWidthPct: 45, catAxisOrientation: "maxMin", catAxisLabelPos: "low", chartColors: [C.a4, C.a1] },
        });
        src(ctx, b);
      },
    },
    {
      id: "V-CMP-05", name: "Slope chart", category: "Compare", kind: "chart", frame: "half",
      objective: "Compare", data_type: "Quantitative", dimensions: 2, complexity: "Low",
      description: "Lines joining each item's value at two moments; the slope shows who gains and who loses.",
      use_when: "Change in ranking or value between two dates for 3 to 7 items.",
      limits: "Two moments only; more than 7 lines becomes hard to read.",
      tags: "slope before after change ranking two points lines gainers losers",
      related: "V-CMP-02 V-EVO-01",
      fill_notes: "Chart: categories = the two moments, one series per item.",
      draw(ctx, b) {
        chartIn(ctx, "Chart", "line", series(["Item 1", "Item 2", "Item 3", "Item 4"], ["Before", "After"], [[40, 52], [35, 30], [22, 34], [15, 12]]), b, {
          bottom: 0.35, legend: true, legendPos: "r", values: true,
          extra: { lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 8, valAxisHidden: true, valGridLine: { style: "none" }, chartColors: [C.a1, C.a3, C.a2, C.a4] },
        });
        src(ctx, b);
      },
    },
    {
      id: "V-CMP-06", name: "Scored comparison", category: "Compare", kind: "table", frame: "full",
      objective: "Decide", data_type: "Ordinal", dimensions: 2, complexity: "Medium",
      description: "Options in columns, criteria in rows, a shaded dot per cell from light (weak) to black (strong).",
      use_when: "Compare 2 to 4 options on 3 to 6 qualitative criteria; supplier or scenario choice.",
      limits: "Scores are relative; give the scale in the note. Shade a dot with {\"fill\": \"a1\"} (strong) to \"a5\" (weak).",
      tags: "scoring comparison options criteria harvey balls evaluation matrix decision",
      related: "V-FRM-04 V-MAT-05",
      fill_notes: "Text fields for headers and criteria; dots: {\"text\": \"\", \"fill\": \"a1|a2|a3|a4|a5\"}.",
      draw(ctx, b) {
        const nC = 4, nR = 5, labW = 3.6, colW = (b.w - labW) / nC, rowH = (b.h - 0.9) / nR;
        for (let c = 0; c < nC; c++) {
          text(ctx, `Option ${c + 1}`, `Option ${String.fromCharCode(65 + c)}`, b.x + labW + c * colW, b.y, colW, 0.45, "small", { bold: true, color: "ink", align: "center", valign: "bottom", optional: c > 1 });
        }
        hrule(ctx, b.x, b.y + 0.55, b.w, { color: "ink", w: 1.25 });
        for (let r = 0; r < nR; r++) {
          const y = b.y + 0.6 + r * rowH;
          text(ctx, `Criterion ${r + 1}`, `Criterion ${r + 1}`, b.x, y, labW - 0.2, rowH, "small", { valign: "middle", optional: r > 1 });
          for (let c = 0; c < nC; c++) {
            const d = Math.min(0.38, rowH * 0.6);
            text(ctx, `Score ${r + 1}-${c + 1}`, " ", b.x + labW + c * colW + colW / 2 - d / 2, y + rowH / 2 - d / 2, d, d, "caption",
              { shape: "ellipse", fill: ["a1", "a3", "a5", "a2"][(r + c) % 4], optional: true, limit: 2 });
          }
          hrule(ctx, b.x, y + rowH, b.w, { color: "line", follows: `Criterion ${r + 1}` });
        }
        text(ctx, "Note", "Scale: black = strong, light grey = weak", b.x, b.y + b.h - 0.28, b.w, 0.28, "caption", { optional: true, keep: true });
      },
    },
  ],
};
