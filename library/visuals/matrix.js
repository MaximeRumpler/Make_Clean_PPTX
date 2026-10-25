// Matrix: two-axis positioning, prioritisation, risk.
const L = require("../tools/lib.js");
const { C, text, rect, line, hrule, vrule } = L;
const { plot, marker, key, arrow } = require("./_kit.js");

// Axis titles around a plot area
function axes(ctx, px, py, pw, ph, xPh = "Horizontal axis", yPh = "Vertical axis") {
  arrow(ctx, px, py + ph, px + pw + 0.05, py + ph, { w: 1 });
  arrow(ctx, px, py + ph, px, py - 0.05, { w: 1 });
  const keep = xPh !== "Horizontal axis";
  text(ctx, "X axis", xPh, px, py + ph + 0.08, pw, 0.3, "caption", { align: "right", color: "ink2", keep });
  text(ctx, "Y axis", yPh, px - 0.23 - ph / 2, py + ph / 2 - 0.15, ph, 0.3, "caption", { color: "ink2", align: "right", rotate: 270, valign: "middle", keep });
}

function quadrants(ctx, px, py, pw, ph, names, o = {}) {
  const fills = o.fills || ["surface", "a6", "a6", "surface"];
  const qw = pw / 2, qh = ph / 2;
  [[0, 0], [1, 0], [0, 1], [1, 1]].forEach(([cx, cy], i) => {
    rect(ctx, px + cx * qw + 0.03, py + cy * qh + 0.03, qw - 0.06, qh - 0.06, { fill: fills[i] });
    text(ctx, `Quadrant ${i + 1}`, names[i], px + cx * qw + 0.18, py + cy * qh + 0.15, qw - 0.4, 0.35, "label", { color: "ink", keep: !names[i].startsWith("Quadrant") });
    if (o.texts) text(ctx, `Quadrant ${i + 1} text`, "What to do here", px + cx * qw + 0.18, py + cy * qh + 0.5, qw - 0.4, qh - 0.7, "caption", { optional: true });
  });
}

module.exports = {
  family: "Matrix",
  slides: [
    {
      id: "V-MAT-01", name: "Two-by-two matrix", category: "Matrix", kind: "matrix", frame: "full",
      objective: "Prioritise", data_type: "Ordinal", dimensions: 2, complexity: "Medium",
      description: "Four named quadrants on two axes, numbered markers placed inside, and a key on the right.",
      use_when: "Position up to eight items on two criteria (value and feasibility, urgency and importance).",
      limits: "Place markers with {\"text\": \"1\", \"at\": [x%, y%]} (0,0 = bottom left of the Plot Area).",
      tags: "2x2 matrix quadrants positioning two criteria prioritisation grid",
      related: "V-MAT-03 V-MAT-06 V-REL-02",
      fill_notes: "Quadrant n, X axis, Y axis: text. Item n: {\"text\", \"at\"}. Key n: names.",
      draw(ctx, b) {
        const px = b.x + 0.45, py = b.y, pw = b.w * 0.62, ph = b.h - 0.45;
        plot(ctx, px, py, pw, ph);
        quadrants(ctx, px, py, pw, ph, ["Quadrant 1", "Quadrant 2", "Quadrant 3", "Quadrant 4"]);
        axes(ctx, px, py, pw, ph);
        [[0.7, 0.75], [0.3, 0.8], [0.8, 0.3], [0.55, 0.6], [0.2, 0.2], [0.4, 0.35]].forEach(([fx, fy], i) =>
          marker(ctx, i + 1, px + fx * pw, py + (1 - fy) * ph));
        text(ctx, "Key label", "Key", px + pw + 0.5, py, b.w - pw - 1.0, 0.3, "label", { keep: true });
        key(ctx, 6, px + pw + 0.5, py + 0.4, b.w - pw - 1.0);
      },
    },
    {
      id: "V-MAT-02", name: "SWOT", category: "Matrix", kind: "matrix", frame: "full",
      objective: "Diagnose", data_type: "Qualitative", dimensions: 2, complexity: "Low",
      description: "Strengths, weaknesses, opportunities and threats in four blocks, internal above, external below.",
      use_when: "Summarise a diagnosis before choosing a strategy.",
      limits: "Five points per block at most; follow with the options it implies.",
      tags: "swot strengths weaknesses opportunities threats diagnosis strategy",
      related: "V-FRM-03 V-FRM-02",
      fill_notes: "Text: Block n (bullets). Headings are fixed but editable.",
      draw(ctx, b) {
        const gap = 0.12, w = (b.w - gap) / 2, h = (b.h - gap) / 2;
        const names = ["Strengths", "Weaknesses", "Opportunities", "Threats"];
        const fills = ["a1", "surface", "surface", "a6"];
        names.forEach((n, i) => {
          const x = b.x + (i % 2) * (w + gap), y = b.y + Math.floor(i / 2) * (h + gap);
          const dark = fills[i] === "a1";
          rect(ctx, x, y, w, h, { fill: fills[i] });
          text(ctx, `Heading ${i + 1}`, n, x + 0.25, y + 0.18, w - 0.5, 0.4, "h3", { color: dark ? "paper" : "ink", keep: true });
          text(ctx, `Block ${i + 1}`, ["Point", "Point", "Point"], x + 0.25, y + 0.65, w - 0.5, h - 0.8, "small", { bullets: true, color: dark ? "a6" : "ink2" });
        });
      },
    },
    {
      id: "V-MAT-03", name: "Impact and effort", category: "Matrix", kind: "matrix", frame: "full",
      objective: "Prioritise", data_type: "Ordinal", dimensions: 2, complexity: "Low",
      description: "Impact on the vertical axis, effort on the horizontal; quick wins, big bets, fill-ins and time sinks.",
      use_when: "Choose which initiatives to launch first.",
      limits: "Scores are relative; place markers with \"at\".",
      tags: "impact effort prioritisation quick wins initiatives backlog choose",
      related: "V-MAT-01 V-REL-02",
      fill_notes: "Item n: {\"text\", \"at\"}; Key n: initiative names.",
      draw(ctx, b) {
        const px = b.x + 0.45, py = b.y, pw = b.w * 0.62, ph = b.h - 0.45;
        plot(ctx, px, py, pw, ph);
        quadrants(ctx, px, py, pw, ph, ["Quick wins", "Big bets", "Fill-ins", "Time sinks"], { fills: ["a5", "a6", "surface", "surface"], texts: true });
        axes(ctx, px, py, pw, ph, "Effort", "Impact");
        [[0.2, 0.8], [0.7, 0.85], [0.3, 0.3], [0.8, 0.2], [0.4, 0.65]].forEach(([fx, fy], i) => marker(ctx, i + 1, px + fx * pw, py + (1 - fy) * ph));
        text(ctx, "Key label", "Initiatives", px + pw + 0.5, py, b.w - pw - 1.0, 0.3, "label", { keep: true });
        key(ctx, 5, px + pw + 0.5, py + 0.4, b.w - pw - 1.0);
      },
    },
    {
      id: "V-MAT-04", name: "Risk matrix", category: "Matrix", kind: "matrix", frame: "full",
      objective: "Assess risk", data_type: "Ordinal", dimensions: 2, complexity: "Medium",
      description: "Five-by-five grid of likelihood and impact, shaded from light to dark, with numbered risks placed in it.",
      use_when: "Risk register summary for a project, a programme or a decision.",
      limits: "Place risks with \"at\" (cell centres are at 10, 30, 50, 70, 90%).",
      tags: "risk matrix likelihood impact probability heat criticality register",
      related: "V-CMP-04 V-REL-04",
      fill_notes: "Item n: {\"text\", \"at\"}; Key n: risk names.",
      draw(ctx, b) {
        const px = b.x + 0.45, py = b.y, ph = b.h - 0.45, pw = Math.min(b.w * 0.62, ph * 1.6);
        plot(ctx, px, py, pw, ph);
        const cw = pw / 5, ch = ph / 5;
        for (let r = 0; r < 5; r++) for (let c = 0; c < 5; c++) {
          const score = (4 - r) + c; // 0..8
          const fill = score >= 7 ? "a2" : score >= 5 ? "a4" : score >= 3 ? "a5" : "a6";
          rect(ctx, px + c * cw + 0.02, py + r * ch + 0.02, cw - 0.04, ch - 0.04, { fill });
        }
        axes(ctx, px, py, pw, ph, "Impact", "Likelihood");
        [[0.9, 0.7], [0.5, 0.9], [0.7, 0.5], [0.3, 0.3], [0.1, 0.5]].forEach(([fx, fy], i) => marker(ctx, i + 1, px + fx * pw, py + (1 - fy) * ph, { fill: "ink" }));
        text(ctx, "Key label", "Risks", px + pw + 0.5, py, b.w - pw - 1.0, 0.3, "label", { keep: true });
        key(ctx, 5, px + pw + 0.5, py + 0.4, b.w - pw - 1.0);
      },
    },
    {
      id: "V-MAT-05", name: "Nine-box grid", category: "Matrix", kind: "matrix", frame: "full",
      objective: "Segment", data_type: "Ordinal", dimensions: 2, complexity: "Medium",
      description: "Three-by-three grid with a name and a short text in each box; darker towards the top right.",
      use_when: "Segment people, products or markets on two three-level scales (performance and potential).",
      limits: "Keep box texts to a few words or names.",
      tags: "nine box 9 box grid talent performance potential segmentation 3x3 ge mckinsey",
      related: "V-MAT-01 V-CMP-06",
      fill_notes: "Box n heading and text; X axis, Y axis.",
      draw(ctx, b) {
        const px = b.x + 0.45, py = b.y, pw = b.w - 0.45, ph = b.h - 0.45, cw = pw / 3, ch = ph / 3;
        for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
          const s = (2 - r) + c, i = r * 3 + c + 1;
          const fill = s >= 4 ? "a1" : s === 3 ? "a3" : s === 2 ? "a5" : "surface";
          const dark = fill === "a1";
          rect(ctx, px + c * cw + 0.04, py + r * ch + 0.04, cw - 0.08, ch - 0.08, { fill });
          text(ctx, `Box ${i} heading`, `Box ${i}`, px + c * cw + 0.2, py + r * ch + 0.15, cw - 0.4, 0.35, "small", { bold: true, color: dark ? "paper" : "ink" });
          text(ctx, `Box ${i} text`, "Short text", px + c * cw + 0.2, py + r * ch + 0.5, cw - 0.4, ch - 0.7, "caption", { color: dark ? "a6" : "ink2", optional: true });
        }
        axes(ctx, px, py, pw, ph);
      },
    },
    {
      id: "V-MAT-06", name: "Positioning map", category: "Matrix", kind: "matrix", frame: "full",
      objective: "Compare", data_type: "Ordinal", dimensions: 2, complexity: "Medium",
      description: "Two crossing axes with labelled ends; numbered markers place each player or offer.",
      use_when: "Competitive positioning, perception maps, where we stand against alternatives.",
      limits: "Place markers with \"at\"; highlight yourself with {\"fill\": \"ink\"}.",
      tags: "positioning map perception competitors axes market landscape",
      related: "V-MAT-01 V-REL-01",
      fill_notes: "Axis end labels: text. Item n: {\"text\", \"at\", \"fill\"}; Key n: names.",
      draw(ctx, b) {
        const px = b.x, py = b.y, pw = b.w * 0.68, ph = b.h;
        plot(ctx, px, py, pw, ph);
        line(ctx, px, py + ph / 2, px + pw, py + ph / 2, { color: "ink", w: 1 });
        line(ctx, px + pw / 2, py, px + pw / 2, py + ph, { color: "ink", w: 1 });
        text(ctx, "Left end", "Low on axis 1", px, py + ph / 2 + 0.05, 2.2, 0.3, "caption", { color: "ink2" });
        text(ctx, "Right end", "High on axis 1", px + pw - 2.2, py + ph / 2 + 0.05, 2.2, 0.3, "caption", { color: "ink2", align: "right" });
        text(ctx, "Top end", "High on axis 2", px + pw / 2 + 0.1, py, 2.4, 0.3, "caption", { color: "ink2" });
        text(ctx, "Bottom end", "Low on axis 2", px + pw / 2 + 0.1, py + ph - 0.3, 2.4, 0.3, "caption", { color: "ink2" });
        [[0.75, 0.8], [0.3, 0.7], [0.6, 0.35], [0.2, 0.25], [0.85, 0.55]].forEach(([fx, fy], i) =>
          marker(ctx, i + 1, px + fx * pw, py + (1 - fy) * ph, { fill: i === 0 ? "ink" : "a2" }));
        text(ctx, "Key label", "Players", px + pw + 0.5, py, b.w - pw - 0.5, 0.3, "label", { keep: true });
        key(ctx, 5, px + pw + 0.5, py + 0.4, b.w - pw - 0.5);
        void hrule; void vrule;
      },
    },
  ],
};
