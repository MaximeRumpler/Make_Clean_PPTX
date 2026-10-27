// Drawing kit shared by the layouts and visuals generators (pptxgenjs, inches).
//
// Every editable element is drawn with a name and recorded as a *field*, so the
// same code produces the .pptx and the index: the two cannot drift apart.
// Colours and fonts are drawn with the token values from theme/tokens.json;
// post.py then turns them into theme references. The style tokens
// (style-tokens.json, chosen with --style) change corners, card treatment,
// background, title case, numbering and the character width behind the limits.
const tokens = require("../theme/tokens.json");
const { STYLE } = require("./style.js");
const ST = STYLE.tokens;

const C = Object.fromEntries(Object.entries(tokens.colors).map(([k, v]) => [k, v.hex]));
C.none = "FEFEFE"; // invisible fill (waterfall and Gantt bases), removed by post.py
const FONT = { heading: tokens.fonts.heading.draw, body: tokens.fonts.body.draw, label: "MCP Label", headingCaps: "MCP Heading Caps" };
const TYPE = tokens.type;
const G = tokens.grid;
const W = G.slide.w, H = G.slide.h, MX = G.margin.x, CW = W - 2 * MX, GUT = G.gutter;
const SERIES = [C.a1, C.a3, C.a5, C.a2, C.a4, C.a6];

// Same constants as skills/make-clean-pptx/scripts/_common.py (estimate_fit) in the
// default style; a style pack sets its own average character width per font
// (char_em), so each pack has its own character limits.
const LINE_EM = 1.2;
const CAPS_EM = 1.2; // capitals are about a fifth wider than mixed case
// Containers whose corners and treatment follow the style tokens.
const SOFT_ROLES = new Set(["card", "callout", "keyfigure", "label"]);

// Roles of the shapes, for the restyler of style packs (references/style-contract.md).
const ROLES = ["card", "callout", "keyfigure", "label", "panel", "frame", "decoration"];

let pres = null;
function init(p) { pres = p; }

// ---------------------------------------------------------------- context
class Ctx {
  constructor(slide, prefix) {
    this.s = slide;
    this.prefix = prefix || "";
    this.fields = [];
    this.names = new Set();
    this.roles = {};
    this.links = [];
  }
  name(n) {
    if (this.names.has(n)) throw new Error(`duplicate shape name '${n}' on ${this.prefix || "slide"}`);
    this.names.add(n);
    return this.prefix ? `${this.prefix}::${n}` : n;
  }
  // Name of a shape that is not a field: "<role>#<n>", plus " > <field>" for the text it holds.
  roleName(role, link) {
    if (!ROLES.includes(role)) throw new Error(`unknown role '${role}' on ${this.prefix || "slide"}`);
    if (link) this.links.push(link); // checked against the fields once the slide is drawn
    this.roles[role] = (this.roles[role] || 0) + 1;
    return this.name(`${role}#${this.roles[role]}${link ? " > " + link : ""}`);
  }
  field(f) { this.fields.push(f); }
}

function charLimit(w, h, size, inset, em = ST.char_em.body) {
  const wPt = (w - 2 * inset) * 72, hPt = (h - 2 * inset) * 72;
  const perLine = Math.max(1, Math.floor(wPt / (size * em)));
  const lines = Math.max(1, Math.floor(hPt / (size * LINE_EM)));
  return { limit: Math.max(4, Math.floor(perLine * lines * 0.85)), lines, perLine };
}

function styleOf(style, o) {
  const t = Object.assign({}, TYPE[style] || TYPE.body);
  if (o.size) t.size = o.size;
  if (o.bold !== undefined) t.bold = o.bold;
  if (o.color) t.color = o.color;
  return t;
}

// Slide and cover titles take the title case of the style.
const upperTitle = (style) => ST.title_case === "upper" && (style === "title" || style === "hero");

function charEm(t, style) {
  const em = ST.char_em[t.font] || ST.char_em.body;
  return upperTitle(style) ? em * CAPS_EM : em; // labels keep their measured limits (capped at 40)
}

// Background "surface" swaps the two light fills, so cards stay visible on the tinted slide.
function tone(fill) {
  if (ST.background === "surface") {
    if (fill === "surface") return "paper";
    if (fill === "paper") return "surface";
  }
  return fill;
}

// Numbers drawn as placeholders ("1", "01"): kept as designed or forced by the style.
function num(n, designed = "plain") {
  const how = ST.numbering === "as-designed" ? designed : ST.numbering;
  return how === "padded" ? String(n).padStart(2, "0") : String(n);
}

function textOpts(t, o, style) {
  const color = C[t.color] || t.color;
  return {
    fontFace: t.caps ? FONT.label : upperTitle(style) ? FONT.headingCaps : FONT[t.font],
    fontSize: t.size,
    bold: !!t.bold,
    italic: !!o.italic,
    color,
    align: o.align || "left",
    valign: o.valign || "top",
    margin: o.inset !== undefined ? o.inset * 72 : 0,
    lineSpacingMultiple: o.lineSpacing || (t.size >= 26 ? 0.95 : 1.1),
    charSpacing: t.caps ? 1 : undefined,
    fit: "none",
    wrap: true,
  };
}

// A named text field. `ph` is the placeholder text shown in the template:
// it describes the slot and never contains invented content.
function text(ctx, name, ph, x, y, w, h, style = "body", o = {}) {
  const t = styleOf(style, o);
  const opts = Object.assign(textOpts(t, o, style), { x, y, w, h, objectName: ctx.name(name) });
  if (o.fill) opts.fill = { color: C[tone(o.fill)] || o.fill };
  if (o.line) opts.line = { color: C[o.line] || o.line, width: o.lw || 0.75 };
  if (o.shape) opts.shape = o.shape;
  // A text field drawn with its own fill or outline is also a container (a badge, a tile, a pill).
  const role = o.fill || o.line || o.shape ? (o.role || "label") : undefined;
  if (role && SOFT_ROLES.has(role) && ST.radius > 0 && !o.shape) {
    opts.shape = "roundRect";
    opts.rectRadius = Math.min(ST.radius, w / 2, h / 2);
  }
  if (o.rotate) opts.rotate = o.rotate;
  const inset = o.inset || 0;
  const fit = charLimit(w, h, t.size, inset, charEm(t, style));
  let body = ph;
  if (o.bullets) {
    const items = Array.isArray(ph) ? ph : [ph];
    body = items.map((p) => ({ text: p, options: { bullet: { indent: Math.round(t.size * 1.1) }, paraSpaceAfter: 4, breakLine: true } }));
  }
  ctx.s.addText(body, opts);
  // default: the placeholder is an acceptable value (framework headings, numbering), kept when not filled.
  const numbering = typeof ph === "string" && /^(0?[1-9]|1[0-9]|[A-Z]?[0-9])$/.test(ph);
  // Editorial caps: labels stay labels, and text inside a visual stays short.
  let limit = o.limit || fit.limit;
  if (!o.limit && style === "label") limit = Math.min(limit, 40);
  if (!o.limit && ctx.prefix) limit = Math.min(limit, 60);
  ctx.field({
    name, type: o.bullets ? "bullets" : "text", limit, lines: fit.lines,
    style, size: t.size, x, y, w, h, placeholder: Array.isArray(ph) ? ph.join(" / ") : ph,
    optional: !!o.optional, default: o.keep === false ? false : !!(o.keep || numbering), follows: o.follows, role,
  });
  return opts;
}

// ---------------------------------------------------------------- shapes
// Every shape that is not a field carries a role (o.role, default "decoration")
// and, with o.for, the field it holds: see references/style-contract.md.
function rect(ctx, x, y, w, h, o = {}) {
  const role = o.role || "decoration";
  let fill = o.fill ? tone(o.fill) : undefined, line = o.line, lw = o.lw, shape = o.shape, radius = o.radius;
  if (SOFT_ROLES.has(role) && !o.points) {
    // Card treatment: light containers are filled (default), outlined, or both. Never a shadow.
    if (fill === tone("surface") && ST.cards !== "fill") {
      line = line || "line";
      lw = lw || 0.75;
      if (ST.cards === "outline") fill = undefined;
    }
    if (ST.radius > 0 && (!shape || shape === "rect")) {
      shape = "roundRect";
      radius = Math.min(ST.radius, w / 2, h / 2);
    }
  }
  const opts = {
    x, y, w, h,
    fill: fill ? { color: C[fill] || fill, transparency: o.transparency || 0 } : { type: "none" },
    line: line ? { color: C[line] || line, width: lw || 0.75, dashType: o.dash || "solid" } : { type: "none" },
    objectName: o.name ? ctx.name(o.name) : o.follows ? ctx.name(`${o.follows} mark${o.markN || ""}`) : ctx.roleName(role, o.for),
  };
  if (o.follows && !o.name) ctx.field({ name: `${o.follows} mark${o.markN || ""}`, type: "deco", follows: o.follows, x, y, w, h, optional: true, role });
  if (radius) opts.rectRadius = radius;
  if (o.rotate) opts.rotate = o.rotate;
  if (o.flipH) opts.flipH = true;
  if (o.flipV) opts.flipV = true;
  if (o.angleRange) opts.angleRange = o.angleRange;
  if (o.arcThicknessRatio) opts.arcThicknessRatio = o.arcThicknessRatio;
  if (o.points) opts.points = o.points;
  ctx.s.addShape(o.points ? "custGeom" : shape || "rect", opts);
  return opts;
}
const ellipse = (ctx, x, y, w, h, o = {}) => rect(ctx, x, y, w, h, Object.assign({ shape: "ellipse" }, o));

// A free-form shape (custom geometry): `pts` are in inches from the top left of
// the box, as pptxgenjs expects ({x, y}, {x, y, curve: {type: "cubic", x1, y1, x2, y2}}, {close: true}).
// Coordinates are rounded so that rebuilds stay byte-identical.
const r4 = (v) => Math.round(v * 10000) / 10000;
function path(ctx, x, y, w, h, pts, o = {}) {
  const points = pts.map((p) => {
    if (p.close) return { close: true };
    const q = { x: r4(p.x), y: r4(p.y) };
    if (p.moveTo) q.moveTo = true;
    if (p.curve) q.curve = Object.fromEntries(Object.entries(p.curve).map(([k, v]) => [k, typeof v === "number" ? r4(v) : v]));
    return q;
  });
  return rect(ctx, x, y, w, h, Object.assign({}, o, { points }));
}

function line(ctx, x1, y1, x2, y2, o = {}) {
  const opts = {
    x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.0001, h: Math.abs(y2 - y1) || 0.0001,
    line: { color: C[o.color || "line"] || o.color, width: o.w || 0.75, dashType: o.dash || "solid",
            beginArrowType: o.begin, endArrowType: o.end },
    objectName: o.name ? ctx.name(o.name) : o.follows ? ctx.name(`${o.follows} mark${o.markN || ""}`) : ctx.roleName("decoration"),
  };
  if (o.follows && !o.name) ctx.field({ name: `${o.follows} mark${o.markN || ""}`, type: "deco", follows: o.follows, optional: true, role: "decoration" });
  if ((x2 < x1) !== (y2 < y1) && x1 !== x2 && y1 !== y2) opts.flipV = true;
  ctx.s.addShape("line", opts);
}
const hrule = (ctx, x, y, w, o = {}) => line(ctx, x, y, x + w, y, o);
const vrule = (ctx, x, y, h, o = {}) => line(ctx, x, y, x, y + h, o);

// An empty area where a visual from the visuals library is inserted (spec: "into").
function frame(ctx, name, x, y, w, h, o = {}) {
  rect(ctx, x, y, w, h, { fill: o.dark ? "a2" : "surface", name, role: "frame" });
  ctx.field({ name, type: "frame", hint: `${(w / h).toFixed(2)}:1`, x, y, w, h,
    placeholder: "Insert a visual", optional: !!o.optional, role: "frame" });
  // the label is a separate, deletable caption so that the frame stays a clean box
}

// An image slot: a grey box replaced by the picture (cover crop).
function image(ctx, name, x, y, w, h, o = {}) {
  rect(ctx, x, y, w, h, { fill: o.fill || "a5", name });
  ctx.field({ name, type: "image", hint: `${(w / h).toFixed(2)}:1`, x, y, w, h, placeholder: "Image", optional: !!o.optional, role: o.role });
}

// The brand logo slot of covers and closing slides: always optional, filled from the
// deck's "logo" key (scale to fit, aspect ratio kept), removed when the deck has none.
// Drawn last on the slide, so the other shapes keep their ids. Corner: "left", "right", "center".
const LOGO = { w: 1.6, h: 0.5, y: 0.5 };
function logo(ctx, corner = "left") {
  const x = corner === "right" ? W - MX - LOGO.w : corner === "center" ? (W - LOGO.w) / 2 : MX;
  image(ctx, "Logo", x, LOGO.y, LOGO.w, LOGO.h, { fill: "a6", optional: true, role: "logo" });
}

// An icon slot: a square whose outline colour is the colour the icon will take.
function icon(ctx, name, x, y, size, o = {}) {
  rect(ctx, x, y, size, size, { line: o.color || "ink", lw: 0.75, dash: "sysDot", name });
  ctx.field({ name, type: "icon", hint: o.color || "ink", x, y, w: size, h: size, placeholder: "Icon", optional: !!o.optional });
}

// ---------------------------------------------------------------- charts
function chartBase(o) {
  return {
    catAxisLabelFontFace: FONT.body, valAxisLabelFontFace: FONT.body, legendFontFace: FONT.body,
    dataLabelFontFace: FONT.body, titleFontFace: FONT.body,
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, legendFontSize: 10, dataLabelFontSize: 10,
    catAxisLabelColor: C.muted, valAxisLabelColor: C.muted, legendColor: C.ink2, dataLabelColor: C.ink2,
    catAxisLineShow: true, catAxisLineColor: C.line, valAxisLineShow: false,
    valGridLine: { color: C.line, size: 0.5, style: "solid" }, catGridLine: { style: "none" },
    showLegend: !!o.legend, legendPos: o.legendPos || "t",
    showValue: !!o.values, showTitle: false,
    chartColors: o.colors || SERIES,
  };
}

function chart(ctx, name, type, data, x, y, w, h, o = {}) {
  const opts = Object.assign(chartBase(o), { x, y, w, h, objectName: ctx.name(name) }, o.extra || {});
  ctx.s.addChart(pres.ChartType[type] || type, data, opts);
  ctx.field({ name, type: "chart", hint: type, x, y, w, h, placeholder: "Chart data", optional: !!o.optional });
}

// Placeholder series: plain labels and round numbers, no fake business data.
function series(names, cats, values) {
  return names.map((n, i) => ({ name: n, labels: cats, values: values[i] }));
}
const cats = (n, word = "Category") => Array.from({ length: n }, (_, i) => `${word} ${i + 1}`);

// ---------------------------------------------------------------- tables
function table(ctx, name, nCols, nRows, x, y, w, o = {}) {
  const colW = o.colW || Array(nCols).fill(w / nCols);
  const head = Array.from({ length: nCols }, (_, i) => ({
    text: o.headers ? o.headers[i] : `Header ${i + 1}`,
    options: { bold: true, color: C.ink, fontFace: FONT.body, fontSize: 11,
      border: [{ type: "none" }, { type: "none" }, { pt: 1.25, color: C.ink }, { type: "none" }] },
  }));
  const rows = [head];
  for (let r = 0; r < nRows; r++) {
    rows.push(Array.from({ length: nCols }, (_, i) => ({
      text: i === 0 ? `Row ${r + 1}` : "Value",
      options: { color: C.ink2, fontFace: FONT.body, fontSize: 11,
        fill: o.zebra && r % 2 === 1 ? { color: C.surface } : undefined,
        border: [{ type: "none" }, { type: "none" }, { pt: 0.5, color: C.line }, { type: "none" }] },
    })));
  }
  const rowH = o.rowH || 0.42;
  ctx.s.addTable(rows, { x, y, w, colW, rowH, margin: [3, 6, 3, 6], valign: "middle", objectName: ctx.name(name) });
  ctx.field({ name, type: "table", hint: `${nCols} columns`, x, y, w, h: rowH * (nRows + 1), placeholder: "Table rows", optional: !!o.optional });
}

// ---------------------------------------------------------------- layout chrome
// Kicker (section label), title, optional lead and footer, on the shared grid.
function chrome(ctx, o = {}) {
  const dark = !!o.dark;
  const ink = dark ? "paper" : undefined;
  if (o.kicker !== false) text(ctx, "Kicker", "Section", MX, G.kicker.y, 6, G.kicker.h, "label", { color: dark ? "a4" : undefined, optional: true, limit: 40 });
  if (o.title !== false) {
    const w = o.titleW || CW;
    text(ctx, "Title", o.titlePh || "Slide title states the takeaway", MX, G.title.y, w, G.title.h, "title", { color: ink, valign: "top", keep: !!o.titleKeep });
  }
  if (o.lead) text(ctx, "Subtitle", "One line that frames the slide", MX, G.lead.y, o.leadW || CW * 0.75, G.lead.h, "lead", { color: dark ? "a5" : undefined, optional: true });
  if (o.footer !== false) footer(ctx, dark);
}

function footer(ctx, dark) {
  text(ctx, "Footer", "Source or confidentiality note", MX, G.footer.y, 8, G.footer.h, "caption", { color: dark ? "a3" : undefined, valign: "middle", optional: true });
  ctx.s.slideNumber = { x: W - MX - 0.8, y: G.footer.y, w: 0.8, h: G.footer.h, fontFace: FONT.body, fontSize: 10, color: dark ? C.a3 : C.muted, align: "right", valign: "middle" };
}

function background(ctx, color) { ctx.s.background = { color: C[color] || color }; }

module.exports = {
  C, FONT, TYPE, G, W, H, MX, CW, GUT, SERIES, ST, STYLE, ROLES, init, Ctx, charLimit, num, tone,
  text, rect, ellipse, path, line, hrule, vrule, frame, image, logo, LOGO, icon, chart, series, cats, table, chrome, footer, background,
  get pres() { return pres; },
};
