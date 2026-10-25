// Build the raw libraries: out/<lib>.pptx + out/<lib>.registry.json
//   node tools/build.js [layouts|visuals|all]
// post.py then applies the theme, groups the visual components and copies the
// result into the skill folder.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const L = require("./lib.js");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "out");

const LIBS = {
  layouts: ["opening", "message", "content", "data", "closing"],
  visuals: ["compare", "evolve", "compose", "relate", "kpi", "matrix", "process", "time", "structure", "frameworks"],
};

function load(lib) {
  const dir = path.join(ROOT, lib);
  return LIBS[lib]
    .filter((m) => fs.existsSync(path.join(dir, m + ".js")))
    .map((m) => require(path.join(dir, m + ".js")));
}

function build(lib) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "Make Clean PPTX";
  pres.company = "github.com/MaximeRumpler/Make_Clean_PPTX";
  pres.title = lib === "layouts" ? "Make Clean PPTX, layouts" : "Make Clean PPTX, visuals";
  pres.theme = { headFontFace: L.FONT.heading, bodyFontFace: L.FONT.body };
  L.init(pres);

  const registry = [];
  const seen = new Set();
  let n = 0;
  for (const mod of load(lib)) {
    pres.addSection({ title: mod.family });
    for (const entry of mod.slides) {
      if (seen.has(entry.id)) throw new Error(`duplicate id ${entry.id}`);
      seen.add(entry.id);
      const slide = pres.addSlide({ sectionTitle: mod.family });
      n += 1;
      let ctx;
      if (lib === "visuals") {
        // Catalogue caption, outside the component group
        slide.addText(`${entry.id}  ·  ${entry.name}`, {
          x: L.MX, y: 0.35, w: 9, h: 0.3, fontFace: L.FONT.label, fontSize: 10, bold: true, color: L.C.muted,
          margin: 0, objectName: "Catalogue label",
        });
        ctx = new L.Ctx(slide, entry.id);
        entry.draw(ctx, entry.box || BOX[entry.frame || "full"]);
      } else {
        ctx = new L.Ctx(slide);
        entry.draw(ctx);
      }
      const { draw, box, ...meta } = entry;
      registry.push(Object.assign({ slide: n, family: mod.family }, meta, { fields: ctx.fields }));
    }
  }
  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, `${lib}.registry.json`), JSON.stringify(registry, null, 2));
  return pres.writeFile({ fileName: path.join(OUT, `${lib}.pptx`) }).then(() => {
    console.log(`${lib}: ${registry.length} slides, ${registry.reduce((a, e) => a + e.fields.length, 0)} fields`);
  });
}

// Native drawing boxes of the visuals, matching the frames of the layouts.
const BOX = {
  full: { x: L.MX, y: 1.2, w: L.CW, h: 4.55 },
  wide: { x: L.MX, y: 1.2, w: 7.9, h: 4.55 },
  half: { x: L.MX, y: 1.2, w: 5.9, h: 4.2 },
};
module.exports = { BOX };

if (require.main === module) {
  const which = process.argv[2] || "all";
  const libs = which === "all" ? Object.keys(LIBS) : [which];
  libs.reduce((p, lib) => p.then(() => build(lib)), Promise.resolve()).catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
