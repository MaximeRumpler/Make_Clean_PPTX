// Style tokens: which pack is being built, and where its files go.
//
// The style is chosen with `--style <name|file.json>` on the command line or the
// MAKE_CLEAN_STYLE environment variable; nothing means "default", the bundled
// libraries. Same rules as tools/_style.py (keep the two in step).
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const FILE = path.join(ROOT, "style-tokens.json");

const ALLOWED = {
  cards: ["fill", "outline", "fill-outline"],
  background: ["paper", "surface"],
  title_case: ["as-written", "upper"],
  numbering: ["as-designed", "plain", "padded"],
};

function merge(base, over) {
  const out = Object.assign({}, base);
  for (const [k, v] of Object.entries(over || {})) {
    if (k.startsWith("_")) continue;
    if (!(k in base)) throw new Error(`unknown style token '${k}'`);
    out[k] = v && typeof v === "object" && !Array.isArray(v) ? Object.assign({}, base[k], v) : v;
  }
  return out;
}

function validate(name, t) {
  for (const [k, values] of Object.entries(ALLOWED)) {
    if (!values.includes(t[k])) throw new Error(`style '${name}': ${k} must be one of ${values.join(", ")} (got '${t[k]}')`);
  }
  if (typeof t.radius !== "number" || t.radius < 0 || t.radius > 0.5) throw new Error(`style '${name}': radius is in inches, 0 to 0.5`);
  for (const k of ["heading", "body"]) {
    if (typeof t.fonts[k] !== "string" || !t.fonts[k]) throw new Error(`style '${name}': fonts.${k} must be a font name`);
    if (!(t.char_em[k] >= 0.4 && t.char_em[k] <= 0.8)) throw new Error(`style '${name}': char_em.${k} must be between 0.4 and 0.8`);
  }
  return t;
}

function requested() {
  const i = process.argv.indexOf("--style");
  if (i > 0 && process.argv[i + 1]) return process.argv[i + 1];
  return process.env.MAKE_CLEAN_STYLE || "default";
}

function load(which) {
  const all = JSON.parse(fs.readFileSync(FILE, "utf8"));
  if (!which || which === "default") return { name: "default", tokens: validate("default", merge(all.default, {})) };
  let name = which, over;
  if (which.endsWith(".json")) {
    over = JSON.parse(fs.readFileSync(path.resolve(which), "utf8"));
    name = over.name || path.basename(which, ".json");
    delete over.name;
  } else if (all.styles && all.styles[which]) {
    over = all.styles[which];
  } else {
    throw new Error(`unknown style '${which}': use a name from library/style-tokens.json or a .json file`);
  }
  if (!/^[a-z0-9][a-z0-9_-]*$/i.test(name) || name === "default") throw new Error(`style name '${name}' must be a simple word other than 'default'`);
  return { name, tokens: validate(name, merge(all.default, over)) };
}

const STYLE = load(requested());
// Raw output of build.js: library/out for the default build, library/out/styles/<name> for a pack.
STYLE.out = STYLE.name === "default" ? path.join(ROOT, "out") : path.join(ROOT, "out", "styles", STYLE.name);

module.exports = { STYLE, load, ALLOWED };
