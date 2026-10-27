// Time: milestones, roadmaps, schedules.
const L = require("../tools/lib.js");
const { C, text, rect, ellipse, path, line, hrule, vrule, series } = L;

module.exports = {
  family: "Time",
  slides: [
    {
      id: "V-TIM-01", name: "Milestone timeline", category: "Time", kind: "timeline", frame: "full",
      objective: "Plan", data_type: "Sequential", dimensions: 1, complexity: "Low",
      description: "Horizontal line with six milestones alternating above and below, each with date and label.",
      use_when: "Key dates of a project, a history, a launch plan.",
      limits: "Equal spacing; delete unused milestones with null.",
      tags: "timeline milestones dates history chronology key dates",
      related: "V-TIM-02 V-PRO-01",
      fill_notes: "Date n, Milestone n.",
      draw(ctx, b) {
        const n = 6, cy = b.y + b.h / 2, step = b.w / n;
        hrule(ctx, b.x, cy, b.w, { color: "ink", w: 1.5 });
        for (let i = 0; i < n; i++) {
          const x = b.x + step * i + step / 2, up = i % 2 === 0;
          ellipse(ctx, x - 0.11, cy - 0.11, 0.22, 0.22, { fill: i === n - 1 ? "paper" : "ink", line: "ink", lw: 1.5, follows: `Milestone ${i + 1}` });
          vrule(ctx, x, up ? cy - 0.75 : cy + 0.11, 0.64, { color: "line", follows: `Milestone ${i + 1}`, markN: " stem" });
          text(ctx, `Date ${i + 1}`, "Date", x - step / 2 + 0.05, up ? cy - 1.25 : cy + 0.8, step - 0.1, 0.35, "label", { color: "ink", align: "center", optional: i > 2 });
          text(ctx, `Milestone ${i + 1}`, "Milestone", x - step / 2 + 0.05, up ? cy - 2.0 : cy + 1.15, step - 0.1, 0.75, "caption", { color: "ink2", align: "center", valign: up ? "bottom" : "top", optional: i > 2 });
        }
      },
    },
    {
      id: "V-TIM-02", name: "Roadmap by lanes", category: "Time", kind: "timeline", frame: "full",
      objective: "Plan", data_type: "Sequential", dimensions: 2, complexity: "Medium",
      description: "Workstreams in rows, four periods in columns; each cell holds the work planned.",
      use_when: "Multi-stream roadmap over quarters or years.",
      limits: "Cells are text; delete empty cells with null to leave the lane blank there.",
      tags: "roadmap lanes workstreams quarters plan streams programme",
      related: "V-TIM-03 V-TIM-05",
      fill_notes: "Period n, Lane n, Cell r-c.",
      draw(ctx, b) {
        const lanes = 4, per = 4, labW = 2.1, cw = (b.w - labW) / per, rh = (b.h - 0.5) / lanes;
        for (let p = 0; p < per; p++) text(ctx, `Period ${p + 1}`, `Period ${p + 1}`, b.x + labW + p * cw, b.y, cw, 0.35, "label", { color: "ink", align: "center" });
        hrule(ctx, b.x, b.y + 0.42, b.w, { color: "ink", w: 1.25 });
        for (let l = 0; l < lanes; l++) {
          const y = b.y + 0.5 + l * rh;
          text(ctx, `Lane ${l + 1}`, `Workstream ${l + 1}`, b.x, y, labW - 0.15, rh, "small", { bold: true, color: "ink", valign: "middle", optional: l > 1 });
          for (let p = 0; p < per; p++) {
            text(ctx, `Cell ${l + 1}-${p + 1}`, "Deliverable", b.x + labW + p * cw + 0.06, y + 0.1, cw - 0.12, rh - 0.2, "caption",
              { fill: (l + p) % 3 === 0 ? "a1" : "surface", color: (l + p) % 3 === 0 ? "paper" : "ink", align: "center", valign: "middle", inset: 0.05, optional: true });
          }
        }
      },
    },
    {
      id: "V-TIM-03", name: "Gantt chart", category: "Time", kind: "chart", frame: "full",
      objective: "Plan", data_type: "Time series", dimensions: 2, complexity: "Medium",
      description: "Tasks as horizontal bars positioned on a time axis (native chart, editable).",
      use_when: "Detailed schedule with tasks and durations.",
      limits: "Fill with {\"categories\": [tasks], \"gantt\": [[start, duration], ...]} in weeks or months from 0.",
      tags: "gantt schedule tasks durations planning project timeline bars",
      related: "V-TIM-02 V-TIM-01",
      fill_notes: "Chart: gantt shortcut; the builder fills the hidden Start series.",
      draw(ctx, b) {
        L.chart(ctx, "Chart", "bar", series(["Start", "Duration"], ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6"],
          [[0, 2, 4, 5, 8, 10], [3, 4, 3, 5, 3, 2]]), b.x, b.y, b.w, b.h - 0.35, {
          extra: { barDir: "bar", barGrouping: "stacked", barGapWidthPct: 45, catAxisOrientation: "maxMin", chartColors: [C.none, C.a1], valAxisMajorUnit: 1 },
        });
        text(ctx, "Note", "Time unit: weeks", b.x, b.y + b.h - 0.3, b.w, 0.3, "caption", { optional: true, keep: true });
      },
    },
    {
      id: "V-TIM-04", name: "Three horizons", category: "Time", kind: "diagram", frame: "full",
      objective: "Plan", data_type: "Sequential", dimensions: 2, complexity: "Medium",
      description: "Three overlapping blocks rising over time: core today, emerging next, future options.",
      use_when: "Balance short-term performance with mid- and long-term growth (portfolio, innovation).",
      limits: "Three horizons; a few words per block.",
      tags: "three horizons h1 h2 h3 innovation growth portfolio future core",
      related: "V-TIM-05 V-STR-08",
      fill_notes: "Horizon n, Horizon n text, X axis, Y axis.",
      draw(ctx, b) {
        const w = b.w / 2.2, h = (b.h - 0.6) / 2.2;
        [[0, 2], [1, 1], [2, 0]].forEach(([k, lev], i) => {
          const x = b.x + 0.45 + k * (w * 0.6), y = b.y + lev * (h * 0.6);
          rect(ctx, x, y, w, h, { fill: ["a1", "a3", "a5"][i], transparency: 0 });
          text(ctx, `Horizon ${i + 1}`, `Horizon ${i + 1}`, x + 0.2, y + 0.15, w - 0.4, 0.4, "small", { bold: true, color: i < 1 ? "paper" : "ink" });
          text(ctx, `Horizon ${i + 1} text`, "What this horizon covers", x + 0.2, y + 0.55, w - 0.4, h - 0.7, "caption", { color: i < 1 ? "a6" : i === 1 ? "ink" : "ink2", optional: true });
        });
        line(ctx, b.x + 0.3, b.y + b.h - 0.4, b.x + b.w, b.y + b.h - 0.4, { color: "ink", w: 1, end: "triangle" });
        line(ctx, b.x + 0.3, b.y + b.h - 0.4, b.x + 0.3, b.y, { color: "ink", w: 1, end: "triangle" });
        text(ctx, "X axis", "Time", b.x + b.w - 2.5, b.y + b.h - 0.32, 2.5, 0.3, "caption", { align: "right", keep: true });
        text(ctx, "Y axis", "Value", b.x + 0.12 - 0.6, b.y + 0.6 - 0.15, 1.2, 0.3, "caption", { rotate: 270, align: "right", keep: true });
      },
    },
    {
      id: "V-TIM-05", name: "Now, next, later", category: "Time", kind: "timeline", frame: "full",
      objective: "Plan", data_type: "Sequential", dimensions: 1, complexity: "Low",
      description: "Three columns from dark to light: what we do now, next and later, as short lists.",
      use_when: "Product or programme roadmap without committed dates.",
      limits: "Three to five items per column.",
      tags: "now next later roadmap product priorities horizon backlog",
      related: "V-TIM-02 V-TIM-04",
      fill_notes: "Column n heading, Column n items (bullets).",
      draw(ctx, b) {
        const gap = 0.25, w = (b.w - 2 * gap) / 3;
        ["Now", "Next", "Later"].forEach((n, i) => {
          const x = b.x + i * (w + gap), fill = ["a1", "a3", "a6"][i];
          text(ctx, `Column ${i + 1} heading`, n, x, b.y, w, 0.6, "h3", { fill, color: i < 1 ? "paper" : "ink", inset: 0.15, valign: "middle", keep: true });
          rect(ctx, x, b.y + 0.6, w, b.h - 0.6, { fill: "surface" });
          text(ctx, `Column ${i + 1} items`, ["Item", "Item", "Item"], x + 0.2, b.y + 0.8, w - 0.4, b.h - 1.0, "small", { bullets: true });
        });
      },
    },
    {
      id: "V-TIM-06", name: "Serpentine timeline", category: "Time", kind: "timeline", frame: "full",
      objective: "Plan", data_type: "Sequential", dimensions: 1, complexity: "Low",
      description: "Eight numbered steps on a path that snakes across three rows, each with a label above and a short text below.",
      use_when: "A long sequence that a single line would cram: a programme of six to eight phases, a history, an onboarding path.",
      limits: "Six to eight steps (steps 7 and 8 can be deleted with null); a few words per label.",
      tags: "serpentine snake s path timeline steps phases sequence journey long process roadmap",
      related: "V-TIM-01 V-PRO-01",
      fill_notes: "Step n (label), Step n text (optional). Steps read left to right, then right to left, then left to right.",
      draw(ctx, b) {
        const gap = 1.42, r = gap / 2, ys = [0, 1, 2].map((k) => b.y + 0.95 + k * gap);
        const xl = b.x + r + 0.05, xr = b.x + b.w - r - 0.05, len = xr - xl, rel = (x, y) => ({ x: x - b.x, y: y - b.y });
        const arc = (x, y, st, sw) => Object.assign(rel(x, y), { curve: { type: "arc", wR: r, hR: r, stAng: st, swAng: sw } });
        path(ctx, b.x, b.y, b.w, b.h, [
          rel(b.x, ys[0]), rel(xr, ys[0]), arc(xr, ys[1], 270, 180),
          rel(xl, ys[1]), arc(xl, ys[2], 270, -180), rel(b.x + b.w, ys[2]),
        ], { line: "a5", lw: 9 });
        const at = [[0, 1], [0, 3], [0, 5], [1, 4], [1, 2], [2, 1], [2, 3], [2, 5]];
        at.forEach(([row, f], i) => {
          const x = xl + (len * f) / 6, y = ys[row], d = 0.46, w = 1.7;
          text(ctx, `Step ${i + 1} number`, String(i + 1), x - d / 2, y - d / 2, d, d, "small", {
            shape: "ellipse", fill: "a1", line: "paper", lw: 1.5, color: "paper", bold: true, align: "center", valign: "middle", follows: `Step ${i + 1}`, limit: 2,
          });
          text(ctx, `Step ${i + 1}`, "Step", x - w / 2, y - 0.83, w, 0.5, "small", { bold: true, color: "ink", align: "center", valign: "bottom", optional: i > 5 });
          text(ctx, `Step ${i + 1} text`, "What happens", x - w / 2, y + 0.3, w, 0.45, "caption", { color: "ink2", align: "center", optional: true });
        });
      },
    },
  ],
};
