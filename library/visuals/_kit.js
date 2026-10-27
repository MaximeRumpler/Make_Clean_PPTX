// Helpers shared by the visual components. A component is drawn inside a box
// {x, y, w, h}; post.py groups everything into one shape named after its id.
const L = require("../tools/lib.js");
const { C, text, rect, ellipse, line, chart } = L;

// Native chart filling the box (minus room for a legend or a note).
function chartIn(ctx, name, type, data, b, o = {}) {
  const top = o.legendRow ? 0.4 : 0;
  chart(ctx, name, type, data, b.x, b.y + top, b.w, b.h - top - (o.bottom || 0), o);
}

// Legend drawn as fields (the chart's own legend is off): swatch + label.
function legend(ctx, labels, x, y, colors, o = {}) {
  let cx = x;
  labels.forEach((lab, i) => {
    rect(ctx, cx, y + 0.08, 0.16, 0.16, { fill: colors[i] });
    const w = o.w || 1.6;
    text(ctx, `Legend ${i + 1}`, lab, cx + 0.24, y, w, 0.3, "caption", { color: "ink2", valign: "middle" });
    cx += w + 0.45;
  });
}

// Area used to position items with {"at": [x%, y%]} (0,0 = bottom left).
function plot(ctx, x, y, w, h, o = {}) {
  rect(ctx, x, y, w, h, { fill: o.fill, line: o.line, name: "Plot Area", role: "frame" });
  ctx.field({ name: "Plot Area", type: "plot", x, y, w, h, placeholder: "Reference for item positions", optional: true, role: "frame" });
}

// Numbered item marker (moved with "at", tinted with "fill").
function marker(ctx, i, cx, cy, o = {}) {
  const d = o.d || 0.42;
  text(ctx, `Item ${i}`, L.num(i), cx - d / 2, cy - d / 2, d, d, "small", {
    shape: "ellipse", fill: o.fill || "a1", role: "label", color: "paper", bold: true, align: "center", valign: "middle", size: 11,
    optional: true, limit: 3, keep: false,
  });
}

// Key that explains numbered markers: "1  Item name".
function key(ctx, n, x, y, w, o = {}) {
  const step = o.step || 0.42;
  for (let i = 1; i <= n; i++) {
    text(ctx, `Key ${i} number`, L.num(i), x, y + (i - 1) * step, 0.3, 0.3, "small", { bold: true, color: "ink", valign: "middle", follows: `Key ${i}` });
    text(ctx, `Key ${i}`, "Item name", x + 0.35, y + (i - 1) * step, w - 0.35, 0.3, "small", { valign: "middle", optional: true });
  }
}

const arrow = (ctx, x1, y1, x2, y2, o = {}) => line(ctx, x1, y1, x2, y2, Object.assign({ color: "ink", w: 1, end: "triangle" }, o));

// Box with a heading and a text, used by diagrams and frameworks.
function card(ctx, prefix, x, y, w, h, o = {}) {
  rect(ctx, x, y, w, h, { fill: o.fill || "surface", line: o.line, role: "card", for: `${prefix} heading` });
  const dark = o.fill === "a1" || o.fill === "ink" || o.fill === "a2";
  text(ctx, `${prefix} heading`, o.heading || "Heading", x + 0.15, y + 0.12, w - 0.3, o.headH || 0.35, o.headStyle || "small",
    { bold: true, color: dark ? "paper" : "ink", align: o.align, optional: o.optional, keep: !!o.heading });
  if (o.body !== false) {
    text(ctx, `${prefix} text`, o.ph || "Short text", x + 0.15, y + 0.12 + (o.headH || 0.35) + 0.05, w - 0.3,
      h - (o.headH || 0.35) - 0.3, o.bodyStyle || "caption", { color: dark ? "a5" : "ink2", align: o.align, optional: true });
  }
}

module.exports = { chartIn, legend, plot, marker, key, arrow, card };
