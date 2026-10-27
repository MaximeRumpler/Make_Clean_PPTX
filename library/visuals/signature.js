// Signature: metaphor illustrations that give a deck a recognisable tone.
// Opt-in only: every row is tagged `signature`, which read_index.py leaves out of
// free-text search unless asked for (references/index-schema.md). Drawn flat, in
// the neutral greys, with native shapes so that every part stays editable.
const L = require("../tools/lib.js");
const { text, rect, ellipse, path, line, hrule, vrule } = L;

const TAU = Math.PI * 2;
const pt = (cx, cy, r, a) => ({ x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) });

// Gear outline with trapezoid teeth, drawn in a square box of side 2 * (rp + add).
// `phase` is the angle of the centre of the first tooth.
function gearPoints(n, rp, add, phase) {
  const ro = rp + add, rr = rp - add, a = TAU / n, pts = [];
  for (let k = 0; k < n; k++) {
    const c = phase + k * a;
    [[-0.29, rr], [-0.15, ro], [0.15, ro], [0.29, rr]].forEach(([f, r]) => pts.push(pt(ro, ro, r, c + f * a)));
  }
  pts.push({ close: true });
  return pts;
}

// One edge of a puzzle piece from p0 to p1; `knob` +1 sticks out, -1 goes in, 0 is flat.
function puzzleEdge(p0, p1, knob) {
  const dx = p1.x - p0.x, dy = p1.y - p0.y, nx = dy, ny = -dx; // outward normal for a clockwise outline
  const at = (t, u) => ({ x: p0.x + dx * t + nx * u * knob, y: p0.y + dy * t + ny * u * knob });
  if (!knob) return [{ x: p1.x, y: p1.y }];
  const a = at(0.38, 0), top = at(0.5, 0.24), d = at(0.62, 0);
  const c = (p, q, e) => ({ x: e.x, y: e.y, curve: { type: "cubic", x1: p.x, y1: p.y, x2: q.x, y2: q.y } });
  return [a, c(at(0.43, 0.07), at(0.29, 0.23), top), c(at(0.71, 0.23), at(0.57, 0.07), d), { x: p1.x, y: p1.y }];
}

// Point on a cubic Bezier, and the y of the road for a given x (bisection on t).
const bez = (p, t) => {
  const u = 1 - t;
  return {
    x: u * u * u * p[0].x + 3 * u * u * t * p[1].x + 3 * u * t * t * p[2].x + t * t * t * p[3].x,
    y: u * u * u * p[0].y + 3 * u * u * t * p[1].y + 3 * u * t * t * p[2].y + t * t * t * p[3].y,
  };
};

module.exports = {
  family: "Signature",
  slides: [
    {
      id: "V-SIG-01", name: "Meshing gears", category: "Signature", kind: "illustration", frame: "wide",
      objective: "Set the tone", data_type: "Relational", dimensions: 1, complexity: "Low",
      description: "Three meshing gears of decreasing size with a label in each hub and a short text beside each.",
      use_when: "Signature metaphor, only on request or when the idea is that parts drive each other: a mechanism, teams or levers working together.",
      limits: "Three gears; one or two words per hub. Opt-in: at most one or two signature visuals per deck, a single metaphor, never for figures.",
      tags: "signature metaphor gears cogs mechanism machine engine levers interlocking working together drive",
      related: "V-STR-05 V-PRO-02",
      fill_notes: "Gear n (one or two words), Gear n text (optional).",
      draw(ctx, b) {
        const p = 0.38, add = 0.12;
        const spec = [{ rp: 1.3, fill: "a1" }, { rp: 0.85, fill: "a3" }, { rp: 0.62, fill: "a4" }].map((g) => {
          const n = Math.round((TAU * g.rp) / p);
          return Object.assign(g, { n, rp: (n * p) / TAU });
        });
        // chain: big gear, then one up-right, then one down-right of the second
        spec[0].cx = b.x + 1.55; spec[0].cy = b.y + 2.45; spec[0].phase = 0;
        [[1, 0, -25], [2, 1, 62]].forEach(([i, j, deg]) => {
          const g = spec[i], h = spec[j], th = (deg * Math.PI) / 180, d = g.rp + h.rp + 0.005;
          g.cx = h.cx + d * Math.cos(th); g.cy = h.cy + d * Math.sin(th);
          // the driving gear has a tooth at fraction u of its pitch; the driven one needs a gap there
          const u = ((((th - h.phase) / (TAU / h.n)) % 1) + 1) % 1;
          g.phase = th + Math.PI - (0.5 - u) * (TAU / g.n);
        });
        spec.forEach((g, i) => {
          const ro = g.rp + add;
          path(ctx, g.cx - ro, g.cy - ro, 2 * ro, 2 * ro, gearPoints(g.n, g.rp, add, g.phase), { fill: g.fill });
          const hd = g.rp * 1.12;
          text(ctx, `Gear ${i + 1}`, "Label", g.cx - hd / 2, g.cy - hd / 2, hd, hd, i === 2 ? "caption" : "small", {
            shape: "ellipse", fill: "paper", color: "ink", bold: true, align: "center", valign: "middle", inset: 0.04,
            limit: [18, 12, 8][i],
          });
        });
        const tx = b.x + 5.35, tw = b.w - 5.35;
        for (let i = 0; i < 3; i++) {
          const y = b.y + 0.55 + i * 1.25;
          ellipse(ctx, tx, y + 0.06, 0.2, 0.2, { fill: spec[i].fill, follows: `Gear ${i + 1} text` });
          text(ctx, `Gear ${i + 1} text`, "What this part drives", tx + 0.35, y, tw - 0.35, 0.95, "caption", { color: "ink2", optional: true });
        }
      },
    },
    {
      id: "V-SIG-02", name: "Light bulb", category: "Signature", kind: "illustration", frame: "wide",
      objective: "Set the tone", data_type: "Qualitative", dimensions: 1, complexity: "Low",
      description: "An outlined light bulb with the idea written in the glass and three short labels at the ends of its rays.",
      use_when: "Signature metaphor, only on request or when the slide introduces one idea and its three facets: an insight, an innovation, a proposal.",
      limits: "One idea in two or three words, three labels of a few words. Opt-in: at most one or two signature visuals per deck, a single metaphor.",
      tags: "signature metaphor light bulb idea insight innovation creativity eureka proposal",
      related: "V-STR-05 V-SIG-06",
      fill_notes: "Idea, Label n (a few words).",
      draw(ctx, b) {
        const cx = b.x + b.w / 2, r = 1.12, cy = b.y + 2.0;
        // glass and neck as one outline: arc over the top, then down to the neck
        const k = 0.74, nx = r * Math.sqrt(1 - k * k), ny = cy + r * k, nb = ny + 0.42, nw = 0.46;
        const ang = (Math.acos(nx / r) * 180) / Math.PI; // angle of the neck points below the horizontal
        const ox = cx - r, oy = cy - r;
        path(ctx, ox, oy, 2 * r, nb - oy, [
          { x: cx - nx - ox, y: ny - oy },
          { x: cx + nx - ox, y: ny - oy, curve: { type: "arc", wR: r, hR: r, stAng: 180 - ang, swAng: 180 + 2 * ang } },
          { x: cx + nw - ox, y: nb - oy },
          { x: cx - nw - ox, y: nb - oy },
          { close: true },
        ], { fill: "surface", line: "ink", lw: 1.75 });
        // screw base and tip
        [0, 1, 2].forEach((i) => {
          const w = 0.98 - i * 0.1;
          rect(ctx, cx - w / 2, nb + 0.06 + i * 0.25, w, 0.19, { shape: "roundRect", radius: 0.08, fill: "a1" });
        });
        path(ctx, cx - 0.24, nb + 0.8, 0.48, 0.2, [{ x: 0.48, y: 0 }, { x: 0, y: 0, curve: { type: "arc", wR: 0.24, hR: 0.2, stAng: 0, swAng: 180 } }, { close: true }], { fill: "a1" });
        text(ctx, "Idea", "The idea", cx - 0.85, cy - 0.55, 1.7, 1.1, "h3", { align: "center", valign: "middle", limit: 36 });
        // rays: two decorative, three ending on a label
        const rays = [-170, -130, -90, -50, -10];
        rays.forEach((deg, i) => {
          const a = (deg * Math.PI) / 180, p1 = pt(cx, cy, r + 0.18, a), p2 = pt(cx, cy, r + (i % 2 ? 0.45 : 0.6), a);
          const lab = { 0: 1, 2: 2, 4: 3 }[i];
          line(ctx, p1.x, p1.y, p2.x, p2.y, Object.assign({ color: "a3", w: 2 }, lab ? { follows: `Label ${lab}` } : {}));
        });
        const lw = 2.3;
        const end = (deg, rr) => pt(cx, cy, r + rr, (deg * Math.PI) / 180);
        const e1 = end(-170, 0.6), e2 = end(-90, 0.6), e3 = end(-10, 0.6);
        text(ctx, "Label 1", "Short label", e1.x - 0.12 - lw, e1.y - 0.4, lw, 0.6, "small", { bold: true, color: "ink", limit: 30, align: "right", valign: "middle" });
        text(ctx, "Label 2", "Short label", e2.x - lw / 2, b.y, lw, e2.y - b.y - 0.06, "small", { bold: true, color: "ink", align: "center", valign: "bottom" });
        text(ctx, "Label 3", "Short label", e3.x + 0.12, e3.y - 0.4, lw, 0.6, "small", { bold: true, color: "ink", limit: 30, valign: "middle" });
      },
    },
    {
      id: "V-SIG-03", name: "Puzzle", category: "Signature", kind: "illustration", frame: "wide",
      objective: "Set the tone", data_type: "Qualitative", dimensions: 1, complexity: "Low",
      description: "Four interlocking jigsaw pieces in a two by two square, each holding a label and a short text.",
      use_when: "Signature metaphor, only on request or when four parts must fit together to make the whole: a solution, an offer, a team.",
      limits: "Four pieces; a label of one or two words and a short text each. Opt-in: at most one or two signature visuals per deck, a single metaphor.",
      tags: "signature metaphor puzzle jigsaw pieces fit together complete solution components integration",
      related: "V-STR-06 V-FRM-02",
      fill_notes: "Piece n, Piece n text (optional). Pieces read left to right, top to bottom.",
      draw(ctx, b) {
        const s = 2.2, d = 0.26 * s, x0 = b.x + (b.w - 2 * s) / 2, y0 = b.y + (b.h - 2 * s) / 2;
        // knobs on [top, right, bottom, left]: +1 out, -1 in; `pad` [left, top, right, bottom]
        // keeps the text clear of the neighbour's knob that comes into the piece
        const pieces = [
          { c: 0, r: 0, knobs: [0, 1, -1, 0], fill: "a1", dark: true, pad: [0.25, 0.3, 0.25, 0.65] },
          { c: 1, r: 0, knobs: [0, 0, 1, -1], fill: "a4", pad: [0.68, 0.3, 0.22, 0.3] },
          { c: 0, r: 1, knobs: [1, -1, 0, 0], fill: "a5", pad: [0.22, 0.3, 0.68, 0.3] },
          { c: 1, r: 1, knobs: [-1, 0, 0, 1], fill: "a2", dark: true, pad: [0.25, 0.68, 0.25, 0.25] },
        ];
        pieces.forEach((pc, i) => {
          // the shape box grows only on the sides where a knob sticks out
          const [kt, kr, kb, kl] = pc.knobs.map((k) => (k > 0 ? d : 0));
          const bx = x0 + pc.c * s - kl, by = y0 + pc.r * s - kt;
          const q = [{ x: kl, y: kt }, { x: kl + s, y: kt }, { x: kl + s, y: kt + s }, { x: kl, y: kt + s }];
          const pts = [{ x: q[0].x, y: q[0].y }];
          for (let e = 0; e < 4; e++) pts.push(...puzzleEdge(q[e], q[(e + 1) % 4], pc.knobs[e]));
          pts.push({ close: true });
          path(ctx, bx, by, s + kl + kr, s + kt + kb, pts, { fill: pc.fill, line: "paper", lw: 2.5 });
          const [pl, ptop, pr, pb] = pc.pad, px = x0 + pc.c * s + pl, py = y0 + pc.r * s + ptop, pw = s - pl - pr;
          text(ctx, `Piece ${i + 1}`, `Piece ${i + 1}`, px, py, pw, 0.4, "small", { bold: true, color: pc.dark ? "paper" : "ink", align: "center", valign: "middle" });
          text(ctx, `Piece ${i + 1} text`, "What this part brings", px, py + 0.45, pw, s - ptop - pb - 0.45, "caption", { color: pc.dark ? "a5" : "ink2", align: "center", optional: true });
        });
      },
    },
    {
      id: "V-SIG-04", name: "Winding road", category: "Signature", kind: "illustration", frame: "full",
      objective: "Set the tone", data_type: "Sequential", dimensions: 1, complexity: "Low",
      description: "A road winding from left to right with four signposts standing on it, each sign naming a milestone.",
      use_when: "Signature metaphor, only on request or when the story is a journey: a transformation path, a programme told as a road ahead.",
      limits: "Four signposts, a few words per sign. For real dates or a plan, use a timeline (V-TIM-01). Opt-in: at most one or two signature visuals per deck, a single metaphor.",
      tags: "signature metaphor road route path journey signposts milestones way ahead transformation",
      related: "V-TIM-01 V-PRO-01",
      fill_notes: "Milestone n (the sign), Milestone n text (optional, under the sign).",
      draw(ctx, b) {
        const P = (x, y) => ({ x: b.x + x * b.w, y: b.y + y });
        const segs = [
          [P(0, 4.05), P(0.16, 4.05), P(0.19, 2.75), P(0.35, 2.75)],
          [P(0.35, 2.75), P(0.51, 2.75), P(0.5, 3.95), P(0.67, 3.95)],
          [P(0.67, 3.95), P(0.84, 3.95), P(0.84, 2.65), P(1, 2.65)],
        ];
        const pts = [{ x: segs[0][0].x - b.x, y: segs[0][0].y - b.y }];
        segs.forEach((sg) => pts.push({ x: sg[3].x - b.x, y: sg[3].y - b.y, curve: { type: "cubic", x1: sg[1].x - b.x, y1: sg[1].y - b.y, x2: sg[2].x - b.x, y2: sg[2].y - b.y } }));
        path(ctx, b.x, b.y, b.w, b.h, pts, { line: "a5", lw: 30 });
        path(ctx, b.x, b.y, b.w, b.h, pts, { line: "paper", lw: 2, dash: "dash" });
        const roadY = (x) => {
          const sg = segs.find((g) => x <= g[3].x) || segs[segs.length - 1];
          let lo = 0, hi = 1;
          for (let k = 0; k < 40; k++) { const m = (lo + hi) / 2; if (bez(sg, m).x < x) lo = m; else hi = m; }
          return bez(sg, (lo + hi) / 2).y;
        };
        const sw = 2.35, sh = 0.55, top = b.y + 0.1;
        for (let i = 0; i < 4; i++) {
          const px = b.x + 0.55 + i * ((b.w - 0.55 - sw - 0.1) / 3), ry = roadY(px);
          vrule(ctx, px, top + sh, ry - top - sh, { color: "ink", w: 2, follows: `Milestone ${i + 1}`, markN: " stem" });
          ellipse(ctx, px - 0.07, ry - 0.07, 0.14, 0.14, { fill: "ink", follows: `Milestone ${i + 1}` });
          text(ctx, `Milestone ${i + 1}`, "Milestone", px, top, sw, sh, "small", {
            shape: "homePlate", fill: i === 3 ? "a1" : "a2", color: "paper", bold: true, valign: "middle", inset: 0.12,
            optional: i > 1, limit: 22,
          });
          text(ctx, `Milestone ${i + 1} text`, "What changes at this point", px + 0.15, top + sh + 0.12, sw - 0.25, 0.75, "caption", { color: "ink2", optional: true });
        }
      },
    },
    {
      id: "V-SIG-05", name: "Mountain and summit flag", category: "Signature", kind: "illustration", frame: "wide",
      objective: "Set the tone", data_type: "Sequential", dimensions: 1, complexity: "Low",
      description: "A faceted mountain with three numbered steps up its left slope and a flag on the summit naming the goal.",
      use_when: "Signature metaphor, only on request or when the message is an ambition reached in stages: a target state, a long climb, a vision.",
      limits: "Three steps and one summit; a few words each. Opt-in: at most one or two signature visuals per deck, a single metaphor, never for figures.",
      tags: "signature metaphor mountain summit peak flag climb ambition goal vision ascent steps",
      related: "V-STR-03 V-PRO-07",
      fill_notes: "Step n (label beside the marker), Summit, Summit text (optional).",
      draw(ctx, b) {
        const base = b.y + b.h - 0.1, L0 = { x: b.x + 0.6, y: base }, top = { x: b.x + 5.15, y: b.y + 0.85 }, R0 = { x: b.x + b.w, y: base };
        const rel = (p) => ({ x: p.x - b.x, y: p.y - b.y });
        // a lower peak behind, then the two faces of the main mountain
        path(ctx, b.x, b.y, b.w, b.h, [rel({ x: b.x + 4.4, y: base }), rel({ x: b.x + 6.75, y: b.y + 1.9 }), rel(R0), { close: true }], { fill: "a6" });
        const foot = { x: b.x + 5.75, y: base };
        path(ctx, b.x, b.y, b.w, b.h, [rel(L0), rel(top), rel(foot), { close: true }], { fill: "a5" });
        path(ctx, b.x, b.y, b.w, b.h, [rel(top), rel({ x: b.x + 7.2, y: base }), rel(foot), { close: true }], { fill: "a4" });
        hrule(ctx, b.x, base, b.w, { color: "line", w: 1 });
        // flag on the summit
        vrule(ctx, top.x, top.y - 0.72, 0.72, { color: "ink", w: 1.75 });
        path(ctx, top.x, top.y - 0.72, 0.6, 0.36, [{ x: 0, y: 0 }, { x: 0.6, y: 0.18 }, { x: 0, y: 0.36 }, { close: true }], { fill: "a1" });
        text(ctx, "Summit", "The goal", top.x + 0.75, b.y + 0.05, b.x + b.w - top.x - 0.75, 0.62, "h3", { valign: "top", limit: 28 });
        text(ctx, "Summit text", "What success looks like", top.x + 0.75, b.y + 0.72, b.x + b.w - top.x - 0.75, 0.7, "caption", { color: "ink2", optional: true });
        // dashed trail and three steps up the left slope
        const at = (f) => ({ x: L0.x + (top.x - L0.x) * f, y: L0.y + (top.y - L0.y) * f });
        [0.22, 0.48, 0.74].forEach((f, i) => {
          const m = at(f), dm = 0.42;
          text(ctx, `Step ${i + 1} number`, L.num(i + 1), m.x - dm / 2, m.y - dm / 2, dm, dm, "small", {
            shape: "ellipse", fill: "a1", line: "paper", lw: 1.5, color: "paper", bold: true, align: "center", valign: "middle", follows: `Step ${i + 1}`, limit: 2,
          });
          text(ctx, `Step ${i + 1}`, "Step on the way", m.x - 1.75, m.y - 0.9, 1.6, 0.6, "small", { bold: true, color: "ink", align: "right", valign: "bottom" });
        });
      },
    },
    {
      id: "V-SIG-06", name: "Target", category: "Signature", kind: "illustration", frame: "wide",
      objective: "Set the tone", data_type: "Qualitative", dimensions: 1, complexity: "Low",
      description: "A bullseye of three rings around a dark centre holding the main label, an arrow in the centre and a leader from each ring to its label.",
      use_when: "Signature metaphor, only on request or when the message is focus on one aim: the objective, the core target and what surrounds it.",
      limits: "Three rings and a centre; a few words each. To show scope or market sizes, use concentric circles (V-STR-08). Opt-in: at most one or two signature visuals per deck, a single metaphor.",
      tags: "signature metaphor target bullseye aim focus objective goal precision hit",
      related: "V-STR-08 V-SIG-05",
      fill_notes: "Centre (two or three words), Ring n, Ring n text (optional). Ring 1 is the outer ring.",
      draw(ctx, b) {
        const cx = b.x + 2.45, cy = b.y + b.h / 2, radii = [2.15, 1.6, 1.05], rc = 0.56;
        radii.forEach((r, i) => ellipse(ctx, cx - r, cy - r, 2 * r, 2 * r, { fill: ["a6", "a5", "a3"][i], line: "paper", lw: 1.5 }));
        text(ctx, "Centre", "Main aim", cx - rc, cy - rc, 2 * rc, 2 * rc, "small", {
          shape: "ellipse", fill: "a1", line: "paper", lw: 1.5, color: "paper", bold: true, align: "center", valign: "middle", inset: 0.05, limit: 14,
        });
        // arrow from the top left into the centre
        const t = pt(cx, cy, 2.35, (-140 * Math.PI) / 180), hit = pt(cx, cy, rc + 0.02, (-140 * Math.PI) / 180);
        line(ctx, t.x, t.y, hit.x, hit.y, { color: "ink", w: 2.25, end: "triangle" });
        // leaders: from inside each ring band to the label column
        const colX = b.x + 5.15, rows = [-1.45, -0.35, 0.6], mids = [(radii[0] + radii[1]) / 2, (radii[1] + radii[2]) / 2, (radii[2] + rc) / 2];
        rows.forEach((dy, i) => {
          const y = cy + dy, x = cx + Math.sqrt(mids[i] * mids[i] - dy * dy);
          ellipse(ctx, x - 0.06, y - 0.06, 0.12, 0.12, { fill: "ink", follows: `Ring ${i + 1}` });
          hrule(ctx, x, y, colX - 0.1 - x, { color: "ink", w: 0.75, follows: `Ring ${i + 1}`, markN: " stem" });
          text(ctx, `Ring ${i + 1}`, ["Outer ring", "Middle ring", "Inner ring"][i], colX, y - 0.2, b.x + b.w - colX, 0.4, "small", { bold: true, color: "ink", valign: "middle" });
          text(ctx, `Ring ${i + 1} text`, "What it covers", colX, y + 0.22, b.x + b.w - colX, 0.55, "caption", { color: "ink2", optional: true });
        });
      },
    },
  ],
};
