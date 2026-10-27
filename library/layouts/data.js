// Tables and decisions.
const L = require("../tools/lib.js");
const { cols } = require("./opening.js");
const { MX, CW, text, rect, hrule, vrule, line, table, chrome } = L;

function optionCard(ctx, i, x, y, w, h, o = {}) {
  const dark = !!o.dark;
  rect(ctx, x, y, w, h, Object.assign(dark ? { fill: "a1" } : { line: "line", lw: 0.75 }, { role: "card", for: `Option ${i} name` }));
  const ink = dark ? "paper" : undefined;
  text(ctx, `Option ${i} label`, o.label || `Option ${String.fromCharCode(64 + i)}`, x + 0.3, y + 0.3, w - 0.6, 0.3, "label", { color: dark ? "a4" : undefined, keep: true });
  text(ctx, `Option ${i} name`, "Name of the option", x + 0.3, y + 0.65, w - 0.6, 0.85, "h3", { size: o.big ? 22 : 18, color: ink });
  text(ctx, `Option ${i} points`, ["Characteristic", "Characteristic", "Characteristic"], x + 0.3, y + 1.6, w - 0.6, h - 2.55, "body", { bullets: true, color: dark ? "a6" : undefined });
  hrule(ctx, x + 0.3, y + h - 0.85, w - 0.6, { color: dark ? "a2" : "line" });
  text(ctx, `Option ${i} verdict`, "Verdict in one line", x + 0.3, y + h - 0.72, w - 0.6, 0.5, "small", { bold: true, color: dark ? "paper" : "ink", optional: true });
}

module.exports = {
  family: "Data and decision",
  slides: [
    {
      id: "L-41", name: "Table and takeaway", category: "Table", style: "Standard", density: "High",
      description: "Native table on the left two thirds, takeaway column on the right.",
      use_when: "Detailed comparison or figures that must be read row by row, with the conclusion beside.",
      tags: "table benchmark comparison grid data rows columns criteria",
      draw(ctx) {
        chrome(ctx);
        table(ctx, "Table", 5, 6, MX, 2.2, 8.4, { colW: [2.4, 1.5, 1.5, 1.5, 1.5] });
        text(ctx, "Takeaway label", "Takeaway", 9.5, 2.2, 3.23, 0.3, "label", { keep: true });
        text(ctx, "Takeaway", "What the table shows, in two or three lines", 9.5, 2.6, 3.23, 2.4, "h3");
        text(ctx, "Note", "Source and scope", 9.5, 5.3, 3.23, 1.0, "small", { color: "muted", optional: true });
      },
    },
    {
      id: "L-42", name: "Action plan", category: "Table", style: "Standard", density: "High",
      description: "Full-width table with action, owner, due date and status columns.",
      use_when: "Who does what by when; follow-up of decisions.",
      tags: "action plan table owner deadline status follow up todo raci",
      draw(ctx) {
        chrome(ctx);
        table(ctx, "Table", 4, 7, MX, 2.2, CW, { headers: ["Action", "Owner", "Due", "Status"], colW: [6.5, 2.4, 1.6, 1.633], rowH: 0.5 });
      },
    },
    {
      id: "L-43", name: "Two options", category: "Decision", style: "Standard", density: "High",
      description: "Two equal option cards with characteristics and a verdict line.",
      use_when: "Choice between two scenarios presented neutrally.",
      tags: "two options scenarios choice decision versus compare alternatives",
      draw(ctx) {
        chrome(ctx);
        cols(2, MX, CW, 0.4).forEach((c, i) => optionCard(ctx, i + 1, c.x, 2.2, c.w, 4.55));
      },
    },
    {
      id: "L-44", name: "Recommended option", category: "Decision", style: "Bold", density: "Medium",
      description: "Recommended option in a large dark card, the alternative in a smaller light card.",
      use_when: "You recommend one option and show the alternative you discarded.",
      tags: "recommendation recommended option preferred decision alternative asymmetric",
      draw(ctx) {
        chrome(ctx);
        optionCard(ctx, 1, MX, 2.2, 7.4, 4.55, { dark: true, label: "Recommended", big: true });
        optionCard(ctx, 2, 8.3, 2.2, 4.433, 4.55, { label: "Alternative" });
      },
    },
    {
      id: "L-45", name: "Three options", category: "Decision", style: "Standard", density: "High",
      description: "Three option cards with characteristics and a verdict line.",
      use_when: "Choice between three scenarios (do nothing, partial, full).",
      tags: "three options scenarios choice decision compare alternatives",
      draw(ctx) {
        chrome(ctx);
        cols(3, MX, CW, 0.3).forEach((c, i) => optionCard(ctx, i + 1, c.x, 2.2, c.w, 4.55));
      },
    },
    {
      id: "L-46", name: "Before and after", category: "Decision", style: "Standard", density: "Medium",
      description: "Two columns, current state in grey and target state in black, joined by an arrow.",
      use_when: "Transformation, as-is versus to-be, the change you propose.",
      tags: "before after as is to be current target change transformation",
      draw(ctx) {
        chrome(ctx);
        rect(ctx, MX, 2.2, 5.5, 4.55, { fill: "surface", role: "card", for: "Left points" });
        text(ctx, "Left label", "Today", MX + 0.35, 2.5, 4.8, 0.3, "label", { keep: true });
        text(ctx, "Left points", ["Current situation", "Current situation", "Current situation"], MX + 0.35, 2.95, 4.8, 3.5, "body", { bullets: true });
        line(ctx, 6.35, 4.45, 7.0, 4.45, { color: "ink", w: 2, end: "triangle" });
        rect(ctx, 7.233, 2.2, 5.5, 4.55, { fill: "a1", role: "card", for: "Right points" });
        text(ctx, "Right label", "Tomorrow", 7.583, 2.5, 4.8, 0.3, "label", { color: "a4", keep: true });
        text(ctx, "Right points", ["Target situation", "Target situation", "Target situation"], 7.583, 2.95, 4.8, 3.5, "body", { bullets: true, color: "paper" });
      },
    },
  ],
};
