// Pictures, frames that receive a visual, and key figures.
const L = require("../tools/lib.js");
const { cols } = require("./opening.js");
const { MX, CW, W, H, text, rect, hrule, vrule, image, frame, chrome, footer } = L;

function kpi(ctx, i, x, y, w, o = {}) {
  text(ctx, `KPI ${i} value`, o.value || "00", x, y, w, o.h || 1.0, "number", { size: o.size || 44, color: o.color });
  text(ctx, `KPI ${i} label`, "What is measured", x, y + (o.h || 1.0) + 0.05, w, 0.45, "body", { bold: true, color: o.labelColor || "ink" });
  if (o.detail !== false) text(ctx, `KPI ${i} detail`, o.detailPh || "Context, period or comparison", x, y + (o.h || 1.0) + 0.5, w, 0.7, "small", { color: o.detailColor || "muted", optional: true });
}

module.exports = {
  family: "Content",
  slides: [
    {
      id: "L-27", name: "Text and image", category: "Media", style: "Standard", density: "Medium",
      description: "Title and text on the left, a full-height picture bleeding off the right edge.",
      use_when: "A message that a photo makes concrete: a site, a product, a team at work.",
      tags: "image photo picture text left visual right illustration",
      draw(ctx) {
        image(ctx, "Photo", 7.2, 0, W - 7.2, H);
        chrome(ctx, { titleW: 6.0, footer: false });
        text(ctx, "Body", "Text that the picture illustrates.", MX, 2.3, 6.0, 4.2, "body", { size: 16 });
        text(ctx, "Footer", "Source or image credit", MX, 7.0, 6, 0.25, "caption", { optional: true });
      },
    },
    {
      id: "L-28", name: "Full image with caption box", category: "Media", style: "Bold", density: "Low",
      description: "Full-bleed picture with a white box in the lower left holding a title and a short text.",
      use_when: "Emotional or contextual moment carried by one strong picture.",
      tags: "full image photo background bleed caption box visual impact",
      draw(ctx) {
        image(ctx, "Photo", 0, 0, W, H);
        rect(ctx, MX, 3.9, 6.2, 2.9, { fill: "paper" });
        text(ctx, "Kicker", "Section", MX + 0.4, 4.2, 5.4, 0.3, "label", { optional: true });
        text(ctx, "Title", "Title over the picture", MX + 0.4, 4.55, 5.4, 1.0, "title");
        text(ctx, "Body", "One or two lines of context.", MX + 0.4, 5.6, 5.4, 1.0, "body", { optional: true });
      },
    },
    {
      id: "L-29", name: "Case study", category: "Media", style: "Standard", density: "Medium",
      description: "Square picture on the left; context and three result figures on the right.",
      use_when: "Customer story, project reference or pilot with measurable results.",
      tags: "case study customer story reference results testimonial pilot",
      draw(ctx) {
        chrome(ctx, { title: false });
        image(ctx, "Photo", MX, 0.9, 4.6, 5.8);
        text(ctx, "Title", "Who, what, and the result in one line", 5.7, 0.9, 7.0, 1.2, "title");
        text(ctx, "Body", "Context, what was done, and how.", 5.7, 2.25, 7.0, 1.9, "body");
        cols(3, 5.7, 7.03).forEach((c, i) => {
          hrule(ctx, c.x, 4.45, c.w, { color: "ink", w: 1.25, follows: `Result ${i + 1} value` });
          text(ctx, `Result ${i + 1} value`, "00", c.x, 4.6, c.w, 0.8, "number", { size: 32, optional: i > 0 });
          text(ctx, `Result ${i + 1} label`, "What improved", c.x, 5.45, c.w, 0.9, "small", { follows: `Result ${i + 1} value` });
        });
      },
    },
    {
      id: "L-30", name: "Team of four", category: "Team", style: "Standard", density: "Medium",
      description: "Four portraits in a row, each with name, role and a one-line focus.",
      use_when: "Introducing the team, the speakers or the key contacts.",
      tags: "team people portraits members speakers bios contacts staff",
      draw(ctx) {
        chrome(ctx, { titlePh: "Team", titleKeep: true });
        cols(4).forEach((c, i) => {
          image(ctx, `Photo ${i + 1}`, c.x, 2.2, c.w, 2.6, { optional: true });
          text(ctx, `Name ${i + 1}`, "Full name", c.x, 4.95, c.w, 0.4, "h3", { optional: i > 0 });
          text(ctx, `Role ${i + 1}`, "Role", c.x, 5.35, c.w, 0.35, "small", { color: "muted", optional: true });
          text(ctx, `Focus ${i + 1}`, "Focus or expertise", c.x, 5.75, c.w, 0.75, "small", { optional: true });
        });
      },
    },
    {
      id: "L-31", name: "Full visual", category: "Frame", style: "Standard", density: "Low",
      description: "Title, framing line and one wide frame for a chart or diagram from the visuals library.",
      use_when: "The visual is the message and needs all the room (roadmap, process, big chart).",
      tags: "frame chart diagram visual full width big graph roadmap",
      draw(ctx) {
        chrome(ctx, { lead: true });
        frame(ctx, "Content Area", MX, 2.2, CW, 4.55);
      },
    },
    {
      id: "L-32", name: "Visual and key points", category: "Frame", style: "Standard", density: "Medium",
      description: "Frame on the left two thirds; key points and a takeaway on the right.",
      use_when: "A chart that needs reading help: what to look at and what it means.",
      tags: "chart commentary key points side comment analysis frame graph",
      draw(ctx) {
        chrome(ctx);
        frame(ctx, "Content Area", MX, 2.2, 7.9, 4.55);
        text(ctx, "Points label", "Key points", 8.9, 2.2, 3.83, 0.3, "label", { keep: true });
        text(ctx, "Points", ["What to look at", "What to look at", "What to look at"], 8.9, 2.65, 3.83, 2.6, "body", { bullets: true });
        hrule(ctx, 8.9, 5.45, 3.83, { color: "ink", w: 1.25 });
        text(ctx, "Takeaway", "So what, in one line", 8.9, 5.6, 3.83, 1.0, "h3", { optional: true });
      },
    },
    {
      id: "L-33", name: "Visual with three callouts", category: "Frame", style: "Standard", density: "Medium",
      description: "Three short numbered callouts in a row above a wide frame.",
      use_when: "A visual with three things to notice, read before looking at it.",
      tags: "callouts highlights frame visual chart three insights",
      draw(ctx) {
        chrome(ctx);
        cols(3).forEach((c, i) => {
          text(ctx, `Callout ${i + 1} number`, L.num(i + 1), c.x, 1.95, 0.4, 0.5, "h3", { size: 20, follows: `Callout ${i + 1}` });
          text(ctx, `Callout ${i + 1}`, "Thing to notice", c.x + 0.45, 2.0, c.w - 0.45, 0.65, "small", { optional: true });
        });
        frame(ctx, "Content Area", MX, 2.85, CW, 3.9);
      },
    },
    {
      id: "L-34", name: "Two visuals", category: "Frame", style: "Standard", density: "Medium",
      description: "Two frames side by side, each with a heading and a caption.",
      use_when: "Comparing two charts or diagrams: before and after, two segments, two periods.",
      tags: "two charts compare side by side frames visuals pair dual",
      draw(ctx) {
        chrome(ctx);
        cols(2, MX, CW, 0.4).forEach((c, i) => {
          text(ctx, `Heading ${i + 1}`, "Visual heading", c.x, 2.0, c.w, 0.45, "h3");
          frame(ctx, `Content Area ${i + 1}`, c.x, 2.5, c.w, 3.5);
          text(ctx, `Caption ${i + 1}`, "What this visual shows", c.x, 6.1, c.w, 0.6, "small", { color: "muted", optional: true });
        });
      },
    },
    {
      id: "L-35", name: "Visual and two figures", category: "Frame", style: "Standard", density: "Medium",
      description: "Frame on the left; two key figures stacked on the right.",
      use_when: "A trend or breakdown with the two numbers that summarise it.",
      tags: "chart kpi figures numbers frame visual summary",
      draw(ctx) {
        chrome(ctx);
        frame(ctx, "Content Area", MX, 2.2, 8.3, 4.55);
        [2.2, 4.5].forEach((y, k) => {
          hrule(ctx, 9.3, y, 3.43, { color: "ink", w: 1.25 });
          kpi(ctx, k + 1, 9.3, y + 0.15, 3.43, { size: 40, h: 0.85 });
        });
      },
    },
    {
      id: "L-36", name: "Dashboard, four modules", category: "Frame", style: "Standard", density: "High",
      description: "Two-by-two grid of frames, each with its own small heading.",
      use_when: "Monitoring view: four indicators or charts read together.",
      tags: "dashboard four modules monitoring overview grid charts kpis",
      draw(ctx) {
        chrome(ctx);
        const cc = cols(2, MX, CW, 0.3);
        for (let i = 0; i < 4; i++) {
          const c = cc[i % 2], y = 2.05 + Math.floor(i / 2) * 2.4;
          text(ctx, `Heading ${i + 1}`, "Module heading", c.x, y, c.w, 0.3, "label", { color: "ink" });
          frame(ctx, `Content Area ${i + 1}`, c.x, y + 0.35, c.w, 1.9);
        }
      },
    },
    {
      id: "L-37", name: "Three figures", category: "KPI", style: "Standard", density: "Low",
      description: "Three large figures in columns, each with label and context, over a strong rule.",
      use_when: "Three numbers that tell the story of a period, a project or an offer.",
      tags: "kpi three figures numbers metrics stats results key figures",
      draw(ctx) {
        chrome(ctx, { lead: true });
        cols(3).forEach((c, i) => {
          hrule(ctx, c.x, 2.6, c.w, { color: "ink", w: 1.5 });
          kpi(ctx, i + 1, c.x, 2.8, c.w, { size: 60, h: 1.2 });
        });
      },
    },
    {
      id: "L-38", name: "Four figures on cards", category: "KPI", style: "Standard", density: "Medium",
      description: "Four grey cards in a row, each with a figure, its label and its variation.",
      use_when: "Four indicators of a scorecard; each needs a short comparison.",
      tags: "kpi four figures cards scorecard indicators variation metrics",
      draw(ctx) {
        chrome(ctx, { lead: true });
        cols(4, MX, CW, 0.25).forEach((c, i) => {
          rect(ctx, c.x, 2.3, c.w, 3.4, { fill: "surface" });
          kpi(ctx, i + 1, c.x + 0.3, 2.6, c.w - 0.6, { size: 40, h: 0.9, detailPh: "Variation and reference" });
        });
      },
    },
    {
      id: "L-39", name: "Six figures", category: "KPI", style: "Standard", density: "Medium",
      description: "Three-by-two grid of compact figures with labels, separated by thin rules.",
      use_when: "Overview of up to six indicators without charts.",
      tags: "kpi six figures grid indicators overview numbers",
      draw(ctx) {
        chrome(ctx);
        const cc = cols(3);
        for (let i = 0; i < 6; i++) {
          const c = cc[i % 3], y = 2.15 + Math.floor(i / 3) * 2.3;
          hrule(ctx, c.x, y, c.w, { color: "line" });
          kpi(ctx, i + 1, c.x, y + 0.15, c.w, { size: 36, h: 0.8 });
        }
      },
    },
    {
      id: "L-40", name: "Hero figure and breakdown", category: "KPI", style: "Bold", density: "Medium",
      description: "Dark left panel with one big figure; four breakdown lines with values on the right.",
      use_when: "A total and what it is made of; a headline result and its drivers.",
      tags: "hero kpi total breakdown drivers big number dark panel",
      draw(ctx) {
        rect(ctx, 0, 0, 5.2, H, { fill: "a1" });
        text(ctx, "Kicker", "Section", MX, 0.45, 4, 0.3, "label", { color: "a4", optional: true });
        text(ctx, "Title", "Slide title states the takeaway", MX, 0.85, 4.2, 1.6, "title", { color: "paper" });
        text(ctx, "Number", "00", MX, 3.2, 4.3, 1.6, "display", { size: 88, color: "paper" });
        text(ctx, "Number caption", "What the figure measures", MX, 4.85, 4.2, 0.8, "body", { color: "a4" });
        text(ctx, "Breakdown label", "Breakdown", 5.9, 1.6, 6.8, 0.3, "label", { keep: true });
        for (let i = 0; i < 4; i++) {
          const y = 2.05 + i * 1.1;
          hrule(ctx, 5.9, y, 6.83, { color: i ? "line" : "ink", w: i ? 0.75 : 1.25, follows: `Item ${i + 1}` });
          text(ctx, `Item ${i + 1}`, "Component", 5.9, y + 0.2, 4.6, 0.7, "body", { optional: i > 1 });
          text(ctx, `Item ${i + 1} value`, "00", 10.6, y + 0.15, 2.13, 0.7, "h3", { size: 24, align: "right", optional: i > 1 });
        }
        text(ctx, "Footer", "Source or confidentiality note", 5.9, 7.0, 6, 0.25, "caption", { optional: true });
      },
    },
  ],
};
