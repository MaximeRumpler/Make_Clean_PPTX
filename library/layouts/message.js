// Statements (one idea per slide) and text structures.
const L = require("../tools/lib.js");
const { cols } = require("./opening.js");
const { MX, CW, W, text, rect, ellipse, hrule, vrule, line, icon, chrome, footer } = L;

module.exports = {
  family: "Message",
  slides: [
    {
      id: "L-12", name: "Key message", category: "Statement", style: "Editorial", density: "Low",
      description: "One sentence set very large on an empty slide, with a short rule above and a source line.",
      use_when: "The single takeaway the audience must remember; a turning point in the story.",
      tags: "key message statement takeaway big sentence one idea headline",
      draw(ctx) {
        hrule(ctx, MX, 2.2, 1.2, { color: "ink", w: 2 });
        text(ctx, "Message", "The one sentence the audience must remember", MX, 2.5, 10.8, 2.6, "hero", { size: 38 });
        text(ctx, "Source", "Source or supporting detail", MX, 5.4, 8, 0.4, "caption", { optional: true });
        footer(ctx);
      },
    },
    {
      id: "L-13", name: "Figure and interpretation", category: "Statement", style: "Editorial", density: "Low",
      description: "A very large number on the left, its caption beneath, and the interpretation in a column on the right.",
      use_when: "One fact carries the argument: show the number, then say what it means.",
      tags: "figure number stat fact proof big number interpretation insight",
      draw(ctx) {
        chrome(ctx, { title: false });
        text(ctx, "Number", "00%", MX, 2.0, 6.2, 2.2, "display", { size: 110, valign: "bottom" });
        text(ctx, "Number caption", "What the figure measures", MX, 4.35, 5.6, 0.8, "body", { color: "muted" });
        vrule(ctx, 7.3, 2.2, 3.8, { color: "line" });
        text(ctx, "Title", "What this figure means", 7.8, 2.2, 4.9, 1.2, "title");
        text(ctx, "Body", "Interpretation in two or three sentences: why it matters and what follows from it.", 7.8, 3.55, 4.9, 2.4, "body");
      },
    },
    {
      id: "L-14", name: "Big quote", category: "Statement", style: "Editorial", density: "Low",
      description: "A large quotation in italics with a thick opening rule and the attribution below.",
      use_when: "A customer, expert or leader said it better; use real quotes only.",
      tags: "quote quotation testimonial citation voice customer verbatim",
      draw(ctx) {
        rect(ctx, MX, 1.9, 0.08, 3.4, { fill: "ink" });
        text(ctx, "Quote", "Quotation, word for word", MX + 0.5, 1.9, 10.5, 3.4, "hero", { size: 32, bold: false, italic: true, valign: "middle" });
        text(ctx, "Attribution", "Name, role, organisation", MX + 0.5, 5.6, 8, 0.4, "label", { color: "ink2" });
        footer(ctx);
      },
    },
    {
      id: "L-15", name: "Strategic question", category: "Statement", style: "Editorial", density: "Low",
      description: "The question that frames the discussion, centred and large, with one line of context.",
      use_when: "Opening a debate or a decision: state the question before the answers.",
      tags: "question problem framing debate issue key question discussion",
      draw(ctx) {
        text(ctx, "Kicker", "The question", MX, 2.0, CW, 0.3, "label", { align: "center", optional: true, keep: true });
        text(ctx, "Question", "The question this presentation answers?", MX + 1, 2.45, CW - 2, 2.2, "hero", { size: 36, align: "center", valign: "middle" });
        text(ctx, "Context", "Why the question matters now", MX + 2.5, 4.9, CW - 5, 0.8, "lead", { align: "center", color: "muted", optional: true });
        footer(ctx);
      },
    },
    {
      id: "L-16", name: "Position and three arguments", category: "Statement", style: "Standard", density: "Medium",
      description: "A position statement across the top, then three numbered arguments in columns.",
      use_when: "Take a stand and back it with three reasons.",
      tags: "position argument reasons three why recommendation stance thesis",
      draw(ctx) {
        chrome(ctx, { titlePh: "The position, stated as a full sentence", titleW: CW * 0.85 });
        const cc = cols(3);
        cc.forEach((c, i) => {
          hrule(ctx, c.x, 2.6, c.w, { color: "ink", w: 1.25, follows: `Argument ${i + 1}` });
          text(ctx, `Number ${i + 1}`, L.num(i + 1), c.x, 2.8, 1, 0.8, "display", { size: 40, follows: `Argument ${i + 1}` });
          text(ctx, `Argument ${i + 1}`, "Argument in a few words", c.x, 3.75, c.w, 0.75, "h3");
          text(ctx, `Argument ${i + 1} detail`, "Evidence or explanation for this argument.", c.x, 4.55, c.w, 1.9, "body", { optional: true });
        });
      },
    },
    {
      id: "L-17", name: "Central figure with annotations", category: "Statement", style: "Bold", density: "Medium",
      description: "One very large number in the centre, four short annotations in the corners linked by thin rules.",
      use_when: "A number that needs context from several angles (cause, trend, comparison, consequence).",
      tags: "figure number annotations centre callouts context stat",
      draw(ctx) {
        chrome(ctx, { titlePh: "Slide title states the takeaway" });
        text(ctx, "Number", "000", 3.9, 3.0, 5.5, 2.0, "display", { size: 110, align: "center", valign: "middle" });
        text(ctx, "Number caption", "Unit and scope", 3.9, 5.0, 5.5, 0.4, "caption", { align: "center" });
        const spots = [[MX, 2.35, "left"], [9.75, 2.35, "right"], [MX, 5.4, "left"], [9.75, 5.4, "right"]];
        spots.forEach(([x, y, al], i) => {
          hrule(ctx, al === "left" ? x : x + 2.4, y - 0.12, 0.6, { color: "ink", w: 1.5, follows: `Note ${i + 1}` });
          text(ctx, `Note ${i + 1}`, "Short annotation", x, y, 3.0, 0.9, "small", { align: al, optional: i > 1 });
        });
      },
    },
    {
      id: "L-18", name: "Title and text", category: "Text", style: "Standard", density: "Medium",
      description: "Title, framing line and one text block, with an optional side note.",
      use_when: "A paragraph of explanation that does not split into parallel points.",
      tags: "text paragraph explanation body narrative simple",
      draw(ctx) {
        chrome(ctx, { lead: true });
        text(ctx, "Body", "Main text. Keep it to one paragraph that supports the title.", MX, 2.3, 7.6, 4.2, "body", { size: 16 });
        vrule(ctx, 8.8, 2.3, 2.5, { color: "line", name: "Side rule" });
        text(ctx, "Side note", "Optional note, definition or source", 9.1, 2.3, 3.6, 2.5, "small", { color: "muted", optional: true });
      },
    },
    {
      id: "L-19", name: "Two columns", category: "Text", style: "Standard", density: "Medium",
      description: "Two balanced text columns, each with a heading over a strong rule.",
      use_when: "Two parallel ideas: problem and solution, today and tomorrow, two audiences.",
      tags: "two columns comparison parallel side by side text pair",
      draw(ctx) {
        chrome(ctx, { lead: true });
        cols(2, MX, CW, 0.6).forEach((c, i) => {
          hrule(ctx, c.x, 2.3, c.w, { color: "ink", w: 1.25 });
          text(ctx, `Heading ${i + 1}`, "Column heading", c.x, 2.45, c.w, 0.5, "h3");
          text(ctx, `Body ${i + 1}`, ["Point", "Point", "Point"], c.x, 3.05, c.w, 3.4, "body", { bullets: true });
        });
      },
    },
    {
      id: "L-20", name: "Three columns with icons", category: "Text", style: "Standard", density: "Medium",
      description: "Three columns, each with an icon, a heading and a short text.",
      use_when: "Three pillars, benefits, principles or offers of equal weight.",
      tags: "three columns pillars icons benefits principles offers features",
      draw(ctx) {
        chrome(ctx, { lead: true });
        cols(3).forEach((c, i) => {
          icon(ctx, `Icon ${i + 1}`, c.x, 2.35, 0.6, { optional: true });
          text(ctx, `Heading ${i + 1}`, "Pillar heading", c.x, 3.2, c.w, 0.5, "h3");
          text(ctx, `Body ${i + 1}`, "Two or three sentences that explain this pillar.", c.x, 3.8, c.w, 2.6, "body");
        });
      },
    },
    {
      id: "L-21", name: "Four columns", category: "Text", style: "Standard", density: "Medium",
      description: "Four narrow numbered columns separated by thin rules.",
      use_when: "Four steps, levers or components that read left to right.",
      tags: "four columns levers components steps numbered pillars",
      draw(ctx) {
        chrome(ctx, { lead: true });
        cols(4).forEach((c, i) => {
          if (i) vrule(ctx, c.x - L.GUT / 2, 2.35, 4.1, { color: "line" });
          text(ctx, `Number ${i + 1}`, L.num(i + 1, "padded"), c.x, 2.35, c.w, 0.6, "h3", { size: 24, color: "muted", follows: `Heading ${i + 1}` });
          text(ctx, `Heading ${i + 1}`, "Heading", c.x, 3.05, c.w, 0.75, "h3");
          text(ctx, `Body ${i + 1}`, "Short text for this column.", c.x, 3.85, c.w, 2.6, "small");
        });
      },
    },
    {
      id: "L-22", name: "Four cards", category: "Text", style: "Standard", density: "High",
      description: "A two-by-two grid of light cards, each with a heading and a short text.",
      use_when: "Four items of equal weight that need a few lines each (findings, recommendations).",
      tags: "four cards grid 2x2 findings recommendations blocks tiles",
      draw(ctx) {
        chrome(ctx);
        const cc = cols(2, MX, CW, 0.25);
        for (let i = 0; i < 4; i++) {
          const c = cc[i % 2], y = 2.2 + Math.floor(i / 2) * 2.35;
          rect(ctx, c.x, y, c.w, 2.15, { fill: "surface" });
          text(ctx, `Heading ${i + 1}`, "Card heading", c.x + 0.3, y + 0.25, c.w - 0.6, 0.45, "h3");
          text(ctx, `Body ${i + 1}`, "Two or three lines that explain the card.", c.x + 0.3, y + 0.8, c.w - 0.6, 1.2, "body");
        }
      },
    },
    {
      id: "L-23", name: "Main content and sidebar", category: "Text", style: "Standard", density: "Medium",
      description: "Main text on the left two thirds, a grey sidebar with key points on the right.",
      use_when: "Explanation plus the facts, definitions or figures the reader should keep.",
      tags: "sidebar main content key points facts aside 70 30",
      draw(ctx) {
        chrome(ctx, { titleW: 7.9 });
        text(ctx, "Body", "Main text that develops the title in a few short paragraphs.", MX, 2.2, 7.6, 4.3, "body", { size: 16 });
        rect(ctx, 8.9, 0, W - 8.9, 7.5, { fill: "surface" });
        text(ctx, "Sidebar label", "Key points", 9.3, 2.2, 3.4, 0.3, "label", { keep: true });
        text(ctx, "Sidebar", ["Key point", "Key point", "Key point"], 9.3, 2.65, 3.4, 3.8, "body", { bullets: true });
      },
    },
    {
      id: "L-24", name: "Text with takeaway box", category: "Text", style: "Standard", density: "Medium",
      description: "Explanatory text on the left, a dark box on the right holding the takeaway.",
      use_when: "The reasoning matters but the conclusion must stand out.",
      tags: "takeaway conclusion box highlight summary so what",
      draw(ctx) {
        chrome(ctx, { titleW: 7.6 });
        text(ctx, "Body", ["Supporting point", "Supporting point", "Supporting point"], MX, 2.3, 7.1, 4.2, "body", { bullets: true, size: 16 });
        rect(ctx, 8.4, 2.3, 4.333, 3.9, { fill: "a1" });
        text(ctx, "Takeaway label", "Takeaway", 8.75, 2.6, 3.6, 0.3, "label", { color: "a4", keep: true });
        text(ctx, "Takeaway", "The conclusion in one or two sentences", 8.75, 3.05, 3.65, 2.9, "h3", { size: 20, color: "paper" });
      },
    },
    {
      id: "L-25", name: "Findings and implications", category: "Text", style: "Editorial", density: "High",
      description: "Three rows: a finding on the left, an arrow, its implication on the right.",
      use_when: "Turning a diagnosis into consequences: what we saw, what it means.",
      tags: "findings implications diagnosis so what consequences insight analysis",
      draw(ctx) {
        chrome(ctx);
        text(ctx, "Left label", "Finding", MX, 2.2, 5.3, 0.3, "label", { keep: true });
        text(ctx, "Right label", "Implication", 7.0, 2.2, 5.7, 0.3, "label", { color: "ink", keep: true });
        for (let i = 0; i < 3; i++) {
          const y = 2.65 + i * 1.35;
          hrule(ctx, MX, y, CW, { color: i ? "line" : "ink", w: i ? 0.75 : 1.25, follows: i ? `Finding ${i + 1}` : undefined });
          text(ctx, `Finding ${i + 1}`, "What we observed", MX, y + 0.2, 5.3, 1.0, "body", { optional: i > 1 });
          line(ctx, 6.15, y + 0.33, 6.75, y + 0.33, { color: "ink", w: 1.25, end: "triangle", follows: `Implication ${i + 1}` });
          text(ctx, `Implication ${i + 1}`, "What it means for us", 7.0, y + 0.2, 5.7, 1.0, "body", { bold: true, color: "ink", optional: i > 1 });
        }
      },
    },
    {
      id: "L-26", name: "Problem and hypotheses", category: "Text", style: "Standard", density: "Medium",
      description: "Problem statement in a grey band, three hypothesis cards below.",
      use_when: "Framing an analysis: the problem and the hypotheses to test.",
      tags: "problem hypotheses framing issue analysis plan test",
      draw(ctx) {
        chrome(ctx);
        rect(ctx, MX, 2.2, CW, 1.15, { fill: "surface" });
        text(ctx, "Problem label", "Problem", MX + 0.3, 2.38, 2, 0.3, "label", { keep: true });
        text(ctx, "Problem", "The problem in one sentence", MX + 0.3, 2.7, CW - 0.6, 0.55, "h3", { size: 18 });
        cols(3).forEach((c, i) => {
          text(ctx, `Hypothesis ${i + 1} label`, `H${i + 1}`, c.x, 3.75, 1, 0.5, "h3", { size: 22, color: "muted", follows: `Hypothesis ${i + 1}` });
          text(ctx, `Hypothesis ${i + 1}`, "Hypothesis to test", c.x, 4.3, c.w, 0.7, "h3");
          text(ctx, `Hypothesis ${i + 1} test`, "How we test it", c.x, 5.05, c.w, 1.4, "small", { optional: true });
        });
      },
    },
  ],
};
