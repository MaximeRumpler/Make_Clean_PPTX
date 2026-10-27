// Structure: hierarchies, layers, relations, causes.
const L = require("../tools/lib.js");
const { C, text, rect, ellipse, path, line, hrule, vrule } = L;
const { arrow } = require("./_kit.js");

const box = (ctx, name, ph, x, y, w, h, o = {}) => text(ctx, name, ph, x, y, w, h, o.style || "caption", Object.assign({
  fill: o.dark ? "a1" : "surface", role: "card", color: o.dark ? "paper" : "ink", bold: !!o.bold, align: "center", valign: "middle", inset: 0.06,
}, o));

module.exports = {
  family: "Structure",
  slides: [
    {
      id: "V-STR-01", name: "Organisation chart", category: "Structure", kind: "diagram", frame: "full",
      objective: "Describe a structure", data_type: "Hierarchical", dimensions: 1, complexity: "Medium",
      description: "One head box, four boxes below, two sub-boxes under each, joined by elbow lines.",
      use_when: "Organisation, governance or team structure on three levels.",
      limits: "Up to 4 x 2 boxes under the head; delete unused boxes with null.",
      tags: "org chart organisation hierarchy team structure reporting lines governance",
      related: "V-STR-02 V-FRM-04",
      fill_notes: "Head, Unit n, Unit n.m (name and role on two lines).",
      draw(ctx, b) {
        const hw = 2.6, hh = 0.75, n = 4, uw = (b.w - 0.9) / n, ux = (i) => b.x + i * (uw + 0.3);
        box(ctx, "Head", "Name\nRole", b.x + b.w / 2 - hw / 2, b.y, hw, hh, { dark: true, style: "small", bold: true });
        const busY = b.y + hh + 0.35;
        vrule(ctx, b.x + b.w / 2, b.y + hh, 0.35, { color: "ink" });
        hrule(ctx, ux(0) + uw / 2, busY, ux(n - 1) - ux(0), { color: "ink" });
        for (let i = 0; i < n; i++) {
          const x = ux(i);
          vrule(ctx, x + uw / 2, busY, 0.3, { color: "ink", follows: `Unit ${i + 1}` });
          box(ctx, `Unit ${i + 1}`, "Name\nRole", x, busY + 0.3, uw, 0.75, { style: "small", bold: true, optional: i > 1 });
          for (let k = 0; k < 2; k++) {
            const y = busY + 1.35 + k * 0.95;
            vrule(ctx, x + 0.2, busY + 1.05, y + 0.35 - busY - 1.05, { color: "line", follows: `Unit ${i + 1}.${k + 1}`, markN: " stem" });
            hrule(ctx, x + 0.2, y + 0.35, 0.2, { color: "line", follows: `Unit ${i + 1}.${k + 1}` });
            box(ctx, `Unit ${i + 1}.${k + 1}`, "Name\nRole", x + 0.4, y, uw - 0.4, 0.7, { fill: "paper", line: "line", optional: true });
          }
        }
      },
    },
    {
      id: "V-STR-02", name: "Logic tree", category: "Structure", kind: "diagram", frame: "full",
      objective: "Diagnose", data_type: "Hierarchical", dimensions: 1, complexity: "Medium",
      description: "Question on the left, three branches, each splitting into two leaves on the right.",
      use_when: "Break a problem or objective into its drivers (issue tree, KPI tree, decision tree).",
      limits: "Branches must not overlap and together cover the question (MECE).",
      tags: "logic tree issue tree driver tree decomposition mece problem solving kpi tree",
      arrange: false, // branches follow the tree
      related: "V-STR-01 V-STR-07",
      fill_notes: "Root, Branch n, Leaf n.m.",
      draw(ctx, b) {
        const rw = 2.4, bw = 3.0, lw = 4.0, colX = [b.x, b.x + rw + 0.8, b.x + rw + bw + 1.6];
        const rowH = b.h / 6;
        box(ctx, "Root", "Question or objective", colX[0], b.y + b.h / 2 - 0.6, rw, 1.2, { dark: true, style: "small", bold: true });
        for (let i = 0; i < 3; i++) {
          const cy = b.y + (2 * i + 1) * rowH;
          line(ctx, colX[0] + rw, b.y + b.h / 2, colX[1], cy, { color: "ink", follows: `Branch ${i + 1}` });
          box(ctx, `Branch ${i + 1}`, "Driver", colX[1], cy - 0.35, bw, 0.7, { style: "small", bold: true, optional: i > 1 });
          for (let k = 0; k < 2; k++) {
            const ly = b.y + (2 * i + k) * rowH + rowH / 2;
            line(ctx, colX[1] + bw, cy, colX[2], ly, { color: "a4", follows: `Leaf ${i + 1}.${k + 1}` });
            box(ctx, `Leaf ${i + 1}.${k + 1}`, "Sub-driver", colX[2], ly - 0.27, lw, 0.54, { fill: "paper", line: "line", align: "left", optional: true });
          }
        }
      },
    },
    {
      id: "V-STR-03", name: "Pyramid", category: "Structure", kind: "diagram", frame: "wide",
      objective: "Describe a structure", data_type: "Hierarchical", dimensions: 1, complexity: "Low",
      description: "Four stacked levels narrowing to the top, with a description beside each level.",
      use_when: "Hierarchy of needs, priorities or foundations (vision to operations).",
      limits: "Four levels; the top holds the most important or the rarest.",
      tags: "pyramid levels hierarchy foundations layers priorities vision",
      arrange: false, // level widths carry the hierarchy
      related: "V-STR-04 V-PRO-07",
      fill_notes: "Level n, Level n text.",
      draw(ctx, b) {
        const n = 4, pw = b.w * 0.5, lh = b.h / n;
        for (let i = 0; i < n; i++) {
          const y = b.y + i * lh, top = pw * (i / n), bot = pw * ((i + 1) / n);
          text(ctx, `Level ${i + 1}`, i === 0 ? "Top" : `Level ${i + 1}`, b.x + (pw - bot) / 2, y + 0.03, bot, lh - 0.06, "small", {
            shape: i === 0 ? "triangle" : "trapezoid", fill: ["a1", "a2", "a3", "a5"][i], color: i < 2 ? "paper" : "ink", bold: true, align: "center", valign: i === 0 ? "bottom" : "middle", inset: 0.04,
          });
          hrule(ctx, b.x + pw + 0.2, y + lh / 2, 0.4, { color: "line" });
          text(ctx, `Level ${i + 1} text`, "What this level means", b.x + pw + 0.7, y + 0.05, b.w - pw - 0.7, lh - 0.1, "caption", { color: "ink2", valign: "middle", optional: true });
          void top;
        }
      },
    },
    {
      id: "V-STR-04", name: "Layered architecture", category: "Structure", kind: "diagram", frame: "full",
      objective: "Describe a structure", data_type: "Hierarchical", dimensions: 2, complexity: "Medium",
      description: "Four horizontal layers with a label on the left and up to four blocks per layer.",
      use_when: "System, data or operating model architecture; stack of capabilities.",
      limits: "Delete unused blocks with null.",
      tags: "architecture layers stack system platform capabilities operating model technology",
      arrange: false, // layers stack in order
      related: "V-STR-03 V-STR-01",
      fill_notes: "Layer n, Block n.m.",
      draw(ctx, b) {
        const n = 4, labW = 2.0, lh = (b.h - 0.3) / n, bpl = 4, bw = (b.w - labW - 0.2) / bpl;
        for (let i = 0; i < n; i++) {
          const y = b.y + i * (lh + 0.1);
          text(ctx, `Layer ${i + 1}`, `Layer ${i + 1}`, b.x, y, labW, lh, "small", { fill: i === 0 ? "a1" : "a2", color: "paper", bold: true, valign: "middle", inset: 0.12 });
          rect(ctx, b.x + labW, y, b.w - labW, lh, { fill: "surface", role: "panel", for: `Layer ${i + 1}` });
          for (let k = 0; k < bpl; k++) {
            box(ctx, `Block ${i + 1}.${k + 1}`, "Component", b.x + labW + 0.15 + k * bw, y + 0.12, bw - 0.15, lh - 0.24, { fill: "paper", line: "line", optional: true });
          }
        }
      },
    },
    {
      id: "V-STR-05", name: "Hub and spoke", category: "Structure", kind: "diagram", frame: "wide",
      objective: "Show relationship", data_type: "Relational", dimensions: 1, complexity: "Low",
      description: "A central circle linked to six satellites, each with a short label.",
      use_when: "Ecosystem around a core: partners, stakeholders, services around a platform.",
      limits: "Six satellites; delete unused ones with null.",
      tags: "hub spoke ecosystem stakeholders partners centre satellites network platform",
      related: "V-STR-08 V-PRO-02",
      fill_notes: "Centre, Node n.",
      draw(ctx, b) {
        const cx = b.x + b.w / 2, cy = b.y + b.h / 2, R = Math.min(b.w / 2 - 1.1, b.h / 2 - 0.45), cd = 1.5, nd = 1.0;
        for (let i = 0; i < 6; i++) {
          const a = (Math.PI * 2 * i) / 6 - Math.PI / 2, x = cx + R * Math.cos(a), y = cy + R * Math.sin(a);
          line(ctx, cx, cy, x, y, { color: "a4", follows: `Node ${i + 1}` });
        }
        text(ctx, "Centre", "Core", cx - cd / 2, cy - cd / 2, cd, cd, "small", { shape: "ellipse", fill: "a1", color: "paper", bold: true, align: "center", valign: "middle" });
        for (let i = 0; i < 6; i++) {
          const a = (Math.PI * 2 * i) / 6 - Math.PI / 2, x = cx + R * Math.cos(a), y = cy + R * Math.sin(a);
          text(ctx, `Node ${i + 1}`, "Node", x - nd / 2, y - nd / 2, nd, nd, "caption", { shape: "ellipse", fill: "paper", line: "ink", color: "ink", bold: true, align: "center", valign: "middle", inset: 0.04, optional: i > 2 });
        }
      },
    },
    {
      id: "V-STR-06", name: "Venn diagram", category: "Structure", kind: "diagram", frame: "wide",
      objective: "Show relationship", data_type: "Qualitative", dimensions: 2, complexity: "Low",
      description: "Three overlapping translucent circles with a label in each and one at the centre.",
      use_when: "Where three domains meet: the sweet spot, a skills profile, a value proposition.",
      limits: "Three sets; the centre label is the point of the slide.",
      tags: "venn overlap intersection sweet spot three circles sets",
      arrange: false, // overlaps carry the meaning
      related: "V-STR-05 V-STR-08",
      fill_notes: "Set n, Centre.",
      draw(ctx, b) {
        const d = Math.min(b.h * 0.62, b.w * 0.42), cx = b.x + b.w / 2, cy = b.y + b.h / 2;
        const pos = [[-0.28, -0.22], [0.28, -0.22], [0, 0.26]];
        pos.forEach(([dx, dy], i) => rect(ctx, cx + dx * d - d / 2, cy + dy * d - d / 2, d, d, { shape: "ellipse", fill: ["a3", "a4", "a5"][i], transparency: 45 }));
        pos.forEach(([dx, dy], i) => text(ctx, `Set ${i + 1}`, `Set ${i + 1}`, cx + dx * d * 1.55 - 1.0, cy + dy * d * 1.55 - 0.25, 2.0, 0.5, "small", { bold: true, color: "ink", align: "center", valign: "middle" }));
        text(ctx, "Centre", "Overlap", cx - 0.75, cy - 0.2, 1.5, 0.45, "caption", { bold: true, color: "ink", align: "center", valign: "middle" });
      },
    },
    {
      id: "V-STR-07", name: "Fishbone", category: "Structure", kind: "diagram", frame: "full",
      objective: "Diagnose", data_type: "Hierarchical", dimensions: 2, complexity: "Medium",
      description: "Cause-and-effect diagram: a spine to the effect on the right, six cause categories as bones.",
      use_when: "Root cause analysis of a quality, delay or performance problem.",
      limits: "Six categories with two causes each.",
      tags: "fishbone ishikawa cause effect root cause quality analysis 6m",
      arrange: false, // bones hang on the spine
      related: "V-STR-02 V-REL-05",
      fill_notes: "Effect, Category n, Cause n.m.",
      draw(ctx, b) {
        const ew = 2.2, sy = b.y + b.h / 2, sx2 = b.x + b.w - ew - 0.1;
        line(ctx, b.x, sy, sx2, sy, { color: "ink", w: 2, end: "triangle" });
        text(ctx, "Effect", "Effect or problem", sx2 + 0.1, sy - 0.6, ew, 1.2, "small", { fill: "a1", role: "callout", color: "paper", bold: true, align: "center", valign: "middle", inset: 0.1 });
        const step = (sx2 - b.x) / 3.2;
        for (let i = 0; i < 6; i++) {
          const up = i < 3, k = i % 3, bx = b.x + 0.4 + k * step, tipX = bx + step * 0.55, endY = up ? b.y + 0.35 : b.y + b.h - 0.35;
          line(ctx, bx, endY, tipX, sy, { color: "a3", w: 1.25, follows: `Category ${i + 1}` });
          text(ctx, `Category ${i + 1}`, `Category ${i + 1}`, bx - 0.6, up ? b.y : b.y + b.h - 0.3, 2.0, 0.3, "label", { color: "ink", optional: i > 3 });
          for (let c = 0; c < 2; c++) {
            const t = 0.35 + c * 0.3, cy2 = endY + (sy - endY) * t;
            text(ctx, `Cause ${i + 1}.${c + 1}`, "Cause", bx + (tipX - bx) * t + 0.1, cy2 - 0.15, step * 0.5, 0.3, "caption", { color: "ink2", optional: true });
          }
        }
      },
    },
    {
      id: "V-STR-08", name: "Concentric circles", category: "Structure", kind: "diagram", frame: "wide",
      objective: "Describe a structure", data_type: "Hierarchical", dimensions: 1, complexity: "Low",
      description: "Three nested circles from the core outwards, with a label for each ring on the side.",
      use_when: "Scope or influence by distance: core business, adjacent, ecosystem; TAM SAM SOM.",
      limits: "Three rings.",
      tags: "concentric circles core rings scope tam sam som influence layers",
      arrange: false, // rings nest by design
      related: "V-STR-05 V-STR-03",
      fill_notes: "Ring n, Ring n text.",
      draw(ctx, b) {
        const D = Math.min(b.h, b.w * 0.55), cx = b.x + D / 2, cy = b.y + b.h / 2;
        [1, 0.68, 0.36].forEach((f, i) => {
          const d = D * f;
          rect(ctx, cx - d / 2, cy + D / 2 - d - (b.h - D) / 2, d, d, { shape: "ellipse", fill: ["a6", "a4", "a1"][i], line: "paper", lw: 1.5 });
        });
        for (let i = 0; i < 3; i++) {
          const y = b.y + 0.2 + i * (b.h - 0.4) / 3;
          hrule(ctx, b.x + D + 0.3, y + 0.05, 0.4, { color: "ink", w: 1.5 });
          text(ctx, `Ring ${i + 1}`, ["Outer ring", "Middle ring", "Core"][i], b.x + D + 0.3, y + 0.15, b.w - D - 0.3, 0.4, "small", { bold: true, color: "ink" });
          text(ctx, `Ring ${i + 1} text`, "What it contains", b.x + D + 0.3, y + 0.55, b.w - D - 0.3, 0.7, "caption", { color: "ink2", optional: true });
        }
      },
    },
    {
      id: "V-STR-09", name: "Half-ring layers", category: "Structure", kind: "diagram", frame: "wide",
      objective: "Describe a structure", data_type: "Hierarchical", dimensions: 1, complexity: "Low",
      description: "A dark half disc at the base wrapped by three nested half rings, each layer named at its top.",
      use_when: "Layers that build outwards from a core: capabilities around a product, circles of stakeholders, foundations to reach.",
      limits: "A core and three rings (the outer ring can be deleted with null); a few words per layer.",
      tags: "half ring radial layers semicircle arch core onion nested levels foundations rainbow",
      arrange: false, // rings nest by design
      related: "V-STR-08 V-STR-03",
      fill_notes: "Layer 1 is the core, Layer 4 the outer ring; Layer n text (optional).",
      draw(ctx, b) {
        const cx = b.x + b.w / 2, base = b.y + b.h - 0.05, radii = [1.05, 2.0, 2.95, 3.9];
        for (let i = radii.length - 1; i >= 0; i--) {
          const ro = radii[i], ri = i ? radii[i - 1] : 0, fill = ["a1", "a3", "a5", "a6"][i];
          const pts = [{ x: 0, y: ro }, { x: 2 * ro, y: ro, curve: { type: "arc", wR: ro, hR: ro, stAng: 180, swAng: 180 } }];
          if (ri) pts.push({ x: ro + ri, y: ro }, { x: ro - ri, y: ro, curve: { type: "arc", wR: ri, hR: ri, stAng: 0, swAng: -180 } });
          pts.push({ close: true });
          path(ctx, cx - ro, base - ro, 2 * ro, ro, pts, Object.assign({ fill, line: "paper", lw: 1.5 }, i === 3 ? { follows: "Layer 4" } : {}));
        }
        radii.forEach((ro, i) => {
          const ri = i ? radii[i - 1] : 0, w = i ? 2.0 : 1.6, top = i ? base - ro + 0.1 : base - ro + 0.3, dark = i === 0;
          text(ctx, `Layer ${i + 1}`, i ? `Layer ${i + 1}` : "Core", cx - w / 2, top, w, 0.32, "small", {
            bold: true, color: dark ? "paper" : "ink", align: "center", valign: "middle", optional: i === 3,
          });
          text(ctx, `Layer ${i + 1} text`, "What this layer adds", cx - w / 2, top + 0.33, w, i ? ro - ri - 0.48 : 0.45, "caption", {
            color: dark ? "a5" : i === 1 ? "ink" : "ink2", align: "center", optional: true,
          });
        });
      },
    },
  ],
};
