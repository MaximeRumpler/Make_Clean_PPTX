// Expressive: compositions with a strong shape, for the one slide that should stand out.
// Opt-in only: every row is tagged `expressive`, which read_index.py leaves out of
// free-text search unless asked for (references/index-schema.md), like `signature`.
//
// Orbital diagrams: a centre and the things around it. The geometry is computed here,
// never drawn by hand: satellite i sits at start + i x 360/n on the orbit, the start
// angle keeps every satellite off 12 and 6 o'clock (so each text goes beside its
// satellite, outside the ring), and one slide is built per count so that positions
// stay exact. Every composition is checked when it is built: no text box overlaps
// another shape or crosses a ring, everything stays inside the frame.
const L = require("../tools/lib.js");
const { text, ellipse, path, line, hrule } = L;

const DEG = Math.PI / 180;
const GAP = 0.06; // minimum clearance between two shapes, inches

// First satellite after 12 o'clock: half a step for an even count, a quarter step for
// an odd one, so the satellites are symmetric about the horizontal axis.
const startDeg = (n) => -90 + (n % 2 ? 90 / n : 180 / n);
const angles = (n, start = startDeg(n)) => Array.from({ length: n }, (_, i) => (start + (i * 360) / n) * DEG);

// ---------------------------------------------------------------- geometry checks
const inEllipse = (px, py, o, m = 0) => ((px - o.cx) / (o.rx + m)) ** 2 + ((py - o.cy) / (o.ry + m)) ** 2;
function rectPoints(r, k = 24) {
  const pts = [];
  for (let i = 0; i <= k; i++) {
    const t = i / k;
    pts.push([r.x + t * r.w, r.y], [r.x + t * r.w, r.y + r.h], [r.x, r.y + t * r.h], [r.x + r.w, r.y + t * r.h]);
  }
  return pts;
}
// A box is clear of an orbit when it lies wholly outside it (with a margin).
const clearOfOrbit = (r, o, m = GAP) => rectPoints(r).every(([px, py]) => inEllipse(px, py, o, m) > 1);

function dist(a, b) {
  if (a.r !== undefined && b.r !== undefined) return Math.hypot(a.cx - b.cx, a.cy - b.cy) - a.r - b.r;
  if (a.r !== undefined) return dist(b, a);
  if (b.r !== undefined) {
    const nx = Math.max(a.x, Math.min(b.cx, a.x + a.w)), ny = Math.max(a.y, Math.min(b.cy, a.y + a.h));
    return Math.hypot(b.cx - nx, b.cy - ny) - b.r;
  }
  const dx = Math.max(a.x - (b.x + b.w), b.x - (a.x + a.w), 0), dy = Math.max(a.y - (b.y + b.h), b.y - (a.y + a.h), 0);
  return dx || dy ? Math.hypot(dx, dy) : -Math.min(a.x + a.w - b.x, b.x + b.w - a.x, a.y + a.h - b.y, b.y + b.h - a.y);
}
const bbox = (s) => (s.r !== undefined ? { x: s.cx - s.r, y: s.cy - s.r, w: 2 * s.r, h: 2 * s.r } : s);

// Throws when two shapes touch, a text box crosses an orbit, or a shape leaves the frame.
function check(id, b, shapes, orbits) {
  for (let i = 0; i < shapes.length; i++) {
    const r = bbox(shapes[i]);
    if (r.x < b.x - 1e-6 || r.y < b.y - 1e-6 || r.x + r.w > b.x + b.w + 1e-6 || r.y + r.h > b.y + b.h + 1e-6) {
      throw new Error(`${id}: ${shapes[i].name} leaves the frame`);
    }
    for (let j = i + 1; j < shapes.length; j++) {
      if (dist(shapes[i], shapes[j]) < GAP) throw new Error(`${id}: ${shapes[i].name} overlaps ${shapes[j].name}`);
    }
    if (shapes[i].text) {
      orbits.forEach((o) => { if (!clearOfOrbit(r, o)) throw new Error(`${id}: ${shapes[i].name} crosses an orbit`); });
    }
  }
}

// Text box beside a satellite, on its side of the centre, pushed outwards until it clears every orbit.
function besideBox(s, o, orbits, tw, th) {
  const right = s.cx >= o.cx, dir = s.cy < o.cy ? -1 : 1;
  const r = { x: right ? s.cx + s.r + 0.12 : s.cx - s.r - 0.12 - tw, y: s.cy - th / 2, w: tw, h: th, right };
  for (let k = 0; k < 60 && !orbits.every((q) => clearOfOrbit(r, q)); k++) {
    if (Math.abs(s.cy - o.cy) < 0.01) r.x += right ? 0.02 : -0.02;
    else r.y += dir * 0.02;
  }
  return r;
}

// ---------------------------------------------------------------- drawing
function centre(ctx, o, d, labelStyle) {
  const c = { name: "Centre", cx: o.cx, cy: o.cy, r: d / 2 };
  ellipse(ctx, o.cx - d / 2, o.cy - d / 2, d, d, { fill: "a1", role: "callout", for: "Centre" });
  const w = d * 0.76;
  text(ctx, "Centre", "Centre", o.cx - w / 2, o.cy - d * 0.3, w, d * 0.3 - 0.02, labelStyle, {
    bold: true, color: "paper", align: "center", valign: "bottom", limit: 18,
  });
  text(ctx, "Centre text", "What sits at the core", o.cx - w / 2, o.cy + 0.03, w, d * 0.27, "caption", {
    color: "a5", align: "center", valign: "top", limit: 30, optional: true,
  });
  return c;
}

// A satellite disc with its label inside (a box inscribed in the circle: 0.8 x 0.6 of the diameter).
function satellite(ctx, name, s, o = {}) {
  const d = 2 * s.r;
  ellipse(ctx, s.cx - s.r, s.cy - s.r, d, d, { fill: o.fill || "paper", line: o.line, lw: 1, role: "label", for: name });
  text(ctx, name, o.ph || "Satellite name", s.cx - d * 0.4, s.cy - d * 0.3, d * 0.8, d * 0.6, "caption", {
    bold: true, color: o.color || "ink", align: "center", valign: "middle", limit: 16,
  });
}

function sideText(ctx, name, r) {
  text(ctx, name, "Short text about this satellite", r.x, r.y, r.w, r.h, "caption", {
    color: "ink2", align: r.right ? "left" : "right", valign: "middle", limit: 40, optional: true,
  });
}

function orbitRing(ctx, o) {
  ellipse(ctx, o.cx - o.rx, o.cy - o.ry, 2 * o.rx, 2 * o.ry, { line: "line", lw: 1.25 });
}

// Short accent rule and a takeaway in the bottom-left corner of the frame.
// The first free corner, bottom left first; a wide box (three lines), then a narrow one (four).
const TAKE = [[2.3, 0.6], [1.7, 0.85]];
function takeawayBox(id, b, others, orbits) {
  for (const [cxr, top] of [[0, 0], [1, 0], [0, 1], [1, 1]]) {
    for (const [w, h] of TAKE) {
      const r = { name: "Takeaway", x: cxr ? b.x + b.w - w : b.x, y: top ? b.y + 0.1 : b.y + b.h - h, w, h, text: true };
      if (others.every((q) => dist(r, q) >= GAP) && orbits.every((o) => clearOfOrbit(r, o))) return r;
    }
  }
  throw new Error(`${id}: no free corner for the takeaway`);
}
function takeaway(ctx, r) {
  hrule(ctx, r.x, r.y - 0.06, 0.5, { color: "a1", w: 2, follows: "Takeaway" });
  text(ctx, "Takeaway", "What the picture says", r.x, r.y, r.w, r.h, "small", { bold: true, color: "ink", valign: "bottom", optional: true });
}

// ---------------------------------------------------------------- V-ORB-01: one orbit
// Satellite diameter shrinks with the count, the ring grows as far as the frame allows.
const SINGLE = { 3: 1.2, 4: 1.15, 5: 1.1, 6: 1.08, 7: 1.04, 8: 1.0 };
const TW = 2.0, TH = 0.42;

function singleOrbit(n) {
  return (ctx, b) => {
    const d = SINGLE[n], cd = 1.7, a = angles(n);
    const reach = Math.max(...a.map((t) => Math.abs(Math.sin(t)))); // vertical extent per unit of radius
    const R = Math.min(1.85, (b.h / 2 - d / 2 - 0.02) / reach);
    const o = { cx: b.x + b.w / 2, cy: b.y + b.h / 2, rx: R, ry: R };
    const sats = a.map((t, i) => ({ name: `Satellite ${i + 1}`, cx: o.cx + R * Math.cos(t), cy: o.cy + R * Math.sin(t), r: d / 2 }));
    const boxes = sats.map((s, i) => Object.assign(besideBox(s, o, [o], TW, TH), { name: `Satellite ${i + 1} text`, text: true }));
    const shapes = [{ name: "Centre", cx: o.cx, cy: o.cy, r: cd / 2 }, ...sats, ...boxes];
    const take = takeawayBox(ctx.prefix, b, shapes, [o]);
    check(ctx.prefix, b, [...shapes, take], [o]);

    orbitRing(ctx, o);
    sats.forEach((s) => {
      const u = { x: (s.cx - o.cx) / R, y: (s.cy - o.cy) / R };
      line(ctx, o.cx + u.x * (cd / 2), o.cy + u.y * (cd / 2), s.cx - u.x * s.r, s.cy - u.y * s.r, { color: "line", w: 1 });
    });
    centre(ctx, o, cd, "body");
    sats.forEach((s, i) => {
      satellite(ctx, s.name, s, { line: "a3" });
      sideText(ctx, `${s.name} text`, boxes[i]);
    });
    takeaway(ctx, take);
  };
}

// ---------------------------------------------------------------- V-ORB-02: two orbits
// Two flattened orbits (the frame is wide, not tall). The outer satellites keep the
// standard start angle; the inner start is chosen at build time to sit as far as
// possible from the outer satellites, still clockwise from 12 o'clock.
function twoOrbits(ni, no) {
  return (ctx, b) => {
    const cd = 1.45, di = 0.94, dd = 1.0;
    const cx = b.x + b.w / 2, cy = b.y + b.h / 2;
    const ao = angles(no), reach = Math.max(...ao.map((t) => Math.abs(Math.sin(t))));
    const outer = { cx, cy, rx: 3.3, ry: Math.min(1.95, (b.h / 2 - dd / 2 - 0.02) / reach) };
    const inner = { cx, cy, rx: 1.85, ry: 1.06 };
    const outs = ao.map((t, i) => ({ name: `Outer ${i + 1}`, cx: cx + outer.rx * Math.cos(t), cy: cy + outer.ry * Math.sin(t), r: dd / 2 }));
    const boxes = outs.map((s, i) => Object.assign(besideBox(s, outer, [outer, inner], TW, TH), { name: `Outer ${i + 1} text`, text: true }));
    const c = { name: "Centre", cx, cy, r: cd / 2 };
    const take = takeawayBox(ctx.prefix, b, [c, ...outs, ...boxes], [outer, inner]);
    const fixed = [c, ...outs, ...boxes, take];
    const innerAt = (start) => angles(ni, start).map((t, i) => ({ name: `Inner ${i + 1}`, cx: cx + inner.rx * Math.cos(t), cy: cy + inner.ry * Math.sin(t), r: di / 2 }));
    let best = null;
    for (let k = 1; k <= 360 / ni; k++) {
      const ins = innerAt(-90 + k);
      // the inner discs must not touch the outer ring either
      const ringGap = Math.min(...ins.map((s) => {
        let m = Infinity;
        for (let t = 0; t < 360; t += 2) m = Math.min(m, Math.hypot(cx + outer.rx * Math.cos(t * DEG) - s.cx, cy + outer.ry * Math.sin(t * DEG) - s.cy) - s.r);
        return m;
      }));
      const score = Math.min(ringGap, ...ins.flatMap((s) => fixed.map((f) => dist(s, f))), ...ins.flatMap((s, i) => ins.slice(i + 1).map((q) => dist(s, q))));
      if (!best || score > best.score + 1e-9) best = { score, ins };
    }
    const ins = best.ins;
    if (best.score < GAP) throw new Error(`${ctx.prefix}: no room for the inner satellites`);
    check(ctx.prefix, b, [...fixed, ...ins], [outer, inner]);

    orbitRing(ctx, outer);
    orbitRing(ctx, inner);
    centre(ctx, { cx, cy }, cd, "caption");
    ins.forEach((s) => satellite(ctx, s.name, s, { fill: "a2", color: "paper", ph: "Inner item" }));
    outs.forEach((s, i) => {
      satellite(ctx, s.name, s, { line: "a3", ph: "Outer item" });
      sideText(ctx, `${s.name} text`, boxes[i]);
    });
    takeaway(ctx, take);
  };
}

// ---------------------------------------------------------------- V-ORB-03: half orbit
// The centre sits on the left edge and the satellites on the right half of the ring,
// from 12 to 6 o'clock, each with its text on the right: a sidebar composition.
const HALF = { 3: 1.0, 4: 0.92, 5: 0.84 };
function halfOrbit(n) {
  return (ctx, b) => {
    const cd = 1.5, d = HALF[n];
    const a = Array.from({ length: n }, (_, i) => (-90 + ((i + 0.5) * 180) / n) * DEG);
    const R = Math.min(1.78, (b.h / 2 - d / 2 - 0.02) / Math.max(...a.map((t) => Math.abs(Math.sin(t)))));
    const o = { cx: b.x + cd / 2, cy: b.y + b.h / 2, rx: R, ry: R };
    const sats = a.map((t, i) => ({ name: `Satellite ${i + 1}`, cx: o.cx + R * Math.cos(t), cy: o.cy + R * Math.sin(t), r: d / 2 }));
    const boxes = sats.map((s, i) => {
      const r = besideBox(s, o, [o], 1, TH);
      r.w = b.x + b.w - r.x;
      const away = s.cy < o.cy ? -0.02 : 0.02;
      while (!clearOfOrbit(r, o) || sats.some((q) => dist(r, q) < GAP + 0.02)) r.y += away;
      return Object.assign(r, { name: `Satellite ${i + 1} text`, text: true });
    });
    check(ctx.prefix, b, [{ name: "Centre", cx: o.cx, cy: o.cy, r: cd / 2 }, ...sats, ...boxes], [o]);

    path(ctx, o.cx, o.cy - R, R, 2 * R, [
      { x: 0, y: 0 },
      { x: 0, y: 2 * R, curve: { type: "arc", wR: R, hR: R, stAng: 270, swAng: 180 } },
    ], { line: "line", lw: 1.25 });
    sats.forEach((s) => {
      const u = { x: (s.cx - o.cx) / R, y: (s.cy - o.cy) / R };
      line(ctx, o.cx + u.x * (cd / 2), o.cy + u.y * (cd / 2), s.cx - u.x * s.r, s.cy - u.y * s.r, { color: "line", w: 1 });
    });
    centre(ctx, o, cd, "small");
    sats.forEach((s, i) => {
      satellite(ctx, s.name, s, { line: "a3" });
      sideText(ctx, `${s.name} text`, boxes[i]);
    });
  };
}

// ---------------------------------------------------------------- registry
const COMMON = {
  category: "Expressive", kind: "diagram", objective: "Show relationship", data_type: "Relational", dimensions: 1,
  arrange: false, // positions are computed for the count
  related: "V-STR-05 V-STR-08",
};
const WORD = { 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight" };
const FALLBACK = "Fallback: V-STR-05 hub and spoke for dense text, a list layout above 8 items.";
const OPT_IN = "Opt-in: one expressive composition per deck at most, only when there is a real centre and satellites.";

const slides = [];
for (let n = 3; n <= 8; n++) {
  slides.push(Object.assign({}, COMMON, {
    id: `V-ORB-01-${n}`, name: `Orbit, ${n} satellites`, frame: "full", complexity: n > 6 ? "Medium" : "Low",
    description: `A dark centre on a thin ring with ${n} satellites placed clockwise from 12 o'clock, each with a label inside and a short text beside it.`,
    use_when: `Expressive composition, only on request: one centre and exactly ${n} things that revolve around it (an ecosystem, stakeholders around a product, capabilities around a core). ${FALLBACK}`,
    limits: `Exactly ${n} satellites (pick the variant for the count). Centre 18 characters, sub-label 30, satellite label 16, satellite text 40. ${OPT_IN}`,
    tags: `expressive orbit orbital satellites centre core ecosystem stakeholders around radial ring ${WORD[n]}`,
    fill_notes: "Centre, Centre text (optional), Satellite n, Satellite n text (optional), Takeaway (optional). Satellites read clockwise from 12 o'clock.",
    draw: singleOrbit(n),
  }));
}
[[2, 4], [3, 5], [3, 6], [4, 6]].forEach(([ni, no]) => {
  slides.push(Object.assign({}, COMMON, {
    id: `V-ORB-02-${ni}x${no}`, name: `Two orbits, ${ni} + ${no} satellites`, frame: "full", complexity: "Medium",
    description: `A dark centre inside two flattened orbits: ${ni} close satellites on the inner one, ${no} on the outer one with a short text beside each.`,
    use_when: `Expressive composition, only on request: a centre with a close circle of ${ni} and a wider circle of ${no} (core and extended team, direct and indirect stakeholders). ${FALLBACK}`,
    limits: `Exactly ${ni} inner and ${no} outer satellites. Centre 18 characters, sub-label 30, labels 16, outer text 40. ${OPT_IN}`,
    tags: `expressive orbit orbital two orbits rings satellites centre core inner outer circle ecosystem stakeholders ${WORD[ni]} ${WORD[no]}`,
    fill_notes: "Centre, Centre text (optional), Inner n, Outer n, Outer n text (optional), Takeaway (optional). Each ring reads clockwise from 12 o'clock.",
    draw: twoOrbits(ni, no),
  }));
});
for (let n = 3; n <= 5; n++) {
  slides.push(Object.assign({}, COMMON, {
    id: `V-ORB-03-${n}`, name: `Half orbit, ${n} satellites`, frame: "half", complexity: "Low",
    description: `A centre on the left edge and ${n} satellites on the right half of a ring, from top to bottom, each with a short text on the right.`,
    use_when: `Expressive composition for a half frame next to text, only on request: one centre and exactly ${n} things around it. ${FALLBACK}`,
    limits: `Exactly ${n} satellites. Centre 18 characters, sub-label 30, satellite label 16, satellite text 40. ${OPT_IN}`,
    tags: `expressive orbit orbital half arc partial satellites centre core sidebar radial ${WORD[n]}`,
    fill_notes: "Centre, Centre text (optional), Satellite n, Satellite n text (optional). Satellites read from top to bottom.",
    draw: halfOrbit(n),
  }));
}

module.exports = { family: "Expressive", slides, _test: { startDeg, angles } };
