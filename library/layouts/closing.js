// Closing slides, editorial compositions and a vertical sequence.
const L = require("../tools/lib.js");
const { cols } = require("./opening.js");
const { MX, CW, W, H, text, rect, ellipse, hrule, vrule, chrome, footer, background } = L;

module.exports = {
  family: "Closing and editorial",
  slides: [
    {
      id: "L-47", name: "Summary and decision", category: "Closing", style: "Standard", density: "Medium",
      description: "Four numbered key points on the left, the decision requested in a dark box on the right.",
      use_when: "End of a decision deck: what to remember and what we ask for.",
      tags: "summary conclusion key points decision ask wrap up synthesis",
      draw(ctx) {
        chrome(ctx, { titlePh: "In summary", titleKeep: true, titleW: 7.6 });
        for (let i = 0; i < 4; i++) {
          const y = 2.2 + i * 1.12;
          hrule(ctx, MX, y, 7.4, { color: i ? "line" : "ink", w: i ? 0.75 : 1.25, follows: i ? `Point ${i + 1}` : undefined });
          text(ctx, `Number ${i + 1}`, L.num(i + 1), MX, y + 0.18, 0.5, 0.6, "h3", { size: 22, color: "muted", follows: `Point ${i + 1}` });
          text(ctx, `Point ${i + 1}`, "Key point to remember", MX + 0.7, y + 0.2, 6.7, 0.8, "body", { bold: true, color: "ink", optional: i > 1 });
        }
        rect(ctx, 8.6, 2.2, 4.133, 4.45, { fill: "a1", role: "callout", for: "Decision" });
        text(ctx, "Decision label", "Decision requested", 8.95, 2.5, 3.5, 0.3, "label", { color: "a4", keep: true });
        text(ctx, "Decision", "What we ask the audience to decide", 8.95, 2.95, 3.45, 3.3, "h3", { size: 20, color: "paper" });
      },
    },
    {
      id: "L-48", name: "Next steps", category: "Closing", style: "Standard", density: "Medium",
      description: "Horizontal line with four dated steps, each with its owner.",
      use_when: "Closing with what happens next and who does it.",
      tags: "next steps actions timeline plan follow up dates owners",
      draw(ctx) {
        chrome(ctx, { titlePh: "Next steps", titleKeep: true, lead: true });
        hrule(ctx, MX, 3.05, CW, { color: "ink", w: 1.25 });
        cols(4).forEach((c, i) => {
          ellipse(ctx, c.x, 2.93, 0.24, 0.24, { fill: i === 0 ? "ink" : "paper", line: "ink", lw: 1.25, follows: `Step ${i + 1}` });
          text(ctx, `Date ${i + 1}`, "Date", c.x, 2.35, c.w, 0.4, "label", { color: "ink", optional: i > 1 });
          text(ctx, `Step ${i + 1}`, "Step", c.x, 3.45, c.w, 0.8, "h3", { optional: i > 1 });
          text(ctx, `Step ${i + 1} detail`, "What will be done", c.x, 4.3, c.w, 1.5, "small", { optional: true });
          text(ctx, `Owner ${i + 1}`, "Owner", c.x, 5.9, c.w, 0.4, "caption", { optional: true });
        });
      },
    },
    {
      id: "L-49", name: "Thank you and contacts", category: "Closing", style: "Standard", density: "Low",
      description: "Large closing line and up to three contacts with name, role and address.",
      use_when: "Last slide: thanks, questions, who to contact.",
      tags: "thank you contacts end closing questions last slide",
      draw(ctx) {
        text(ctx, "Title", "Thank you", MX, 1.7, 9, 1.5, "display", { size: 60, keep: true });
        text(ctx, "Subtitle", "Questions, discussion or call to action", MX, 3.25, 8, 0.6, "lead", { optional: true });
        hrule(ctx, MX, 4.5, CW, { color: "ink", w: 1.25 });
        cols(3).forEach((c, i) => {
          text(ctx, `Contact ${i + 1} name`, "Full name", c.x, 4.7, c.w, 0.4, "h3", { optional: i > 0 });
          text(ctx, `Contact ${i + 1} role`, "Role", c.x, 5.1, c.w, 0.35, "small", { color: "muted", optional: true });
          text(ctx, `Contact ${i + 1} details`, "Email or phone", c.x, 5.45, c.w, 0.6, "small", { optional: true });
        });
        footer(ctx);
      },
    },
    {
      id: "L-50", name: "Bento grid", category: "Editorial", style: "Bold", density: "Medium",
      description: "Grid of five modules of different sizes; the main one is dark and holds a figure.",
      use_when: "A rich overview (offer, results, programme) where one element dominates.",
      tags: "bento grid mosaic modules overview tiles editorial modern",
      arrange: false, // the sizes of the modules are the design: no rearranging
      draw(ctx) {
        chrome(ctx);
        rect(ctx, MX, 2.1, 5.0, 4.65, { fill: "a1", role: "keyfigure", for: "Main value" });
        text(ctx, "Main value", "00", MX + 0.35, 2.4, 4.3, 1.4, "display", { size: 72, color: "paper" });
        text(ctx, "Main label", "Main message of the grid", MX + 0.35, 4.0, 4.3, 1.2, "h3", { size: 20, color: "paper" });
        text(ctx, "Main detail", "Short detail", MX + 0.35, 5.3, 4.3, 1.1, "small", { color: "a4", optional: true });
        const tiles = [[5.85, 2.1, 6.883, 2.2], [5.85, 4.55, 3.29, 2.2], [9.44, 4.55, 3.293, 2.2]];
        tiles.forEach(([x, y, w, h], i) => {
          rect(ctx, x, y, w, h, { fill: "surface", role: "card", for: `Tile ${i + 1} heading` });
          text(ctx, `Tile ${i + 1} heading`, "Heading", x + 0.3, y + 0.25, w - 0.6, 0.45, "h3");
          text(ctx, `Tile ${i + 1} body`, "Short text", x + 0.3, y + 0.8, w - 0.6, h - 1.05, "small", { optional: true });
        });
      },
    },
    {
      id: "L-51", name: "Horizontal bands", category: "Editorial", style: "Editorial", density: "Medium",
      description: "Three full-width bands alternating grey and white: label, heading and text on each.",
      use_when: "Three themes or periods read top to bottom (past, present, future).",
      tags: "bands horizontal rows three themes past present future layers",
      draw(ctx) {
        chrome(ctx);
        for (let i = 0; i < 3; i++) {
          const y = 2.05 + i * 1.6;
          if (i % 2 === 0) rect(ctx, 0, y, W, 1.6, { fill: "surface", role: "panel", for: `Band ${i + 1} heading` });
          text(ctx, `Band ${i + 1} label`, `Theme ${i + 1}`, MX, y + 0.3, 2.4, 0.3, "label", { color: "ink" });
          text(ctx, `Band ${i + 1} heading`, "Heading", 3.3, y + 0.25, 3.6, 1.1, "h3", { size: 18 });
          text(ctx, `Band ${i + 1} body`, "Two lines on this theme.", 7.2, y + 0.28, 5.5, 1.1, "body");
        }
      },
    },
    {
      id: "L-52", name: "Story in four acts", category: "Editorial", style: "Editorial", density: "Medium",
      description: "Four acts in columns joined by a line: act number, title and short text.",
      use_when: "Narrative arc: situation, complication, resolution, outcome.",
      tags: "story narrative four acts storytelling arc situation complication resolution",
      draw(ctx) {
        chrome(ctx);
        hrule(ctx, MX, 2.75, CW, { color: "line" });
        cols(4).forEach((c, i) => {
          rect(ctx, c.x, 2.55, 0.4, 0.4, { fill: i === 3 ? "ink" : "paper", line: "ink", lw: 1.25, follows: `Act ${i + 1} title` });
          text(ctx, `Act ${i + 1} label`, `Act ${i + 1}`, c.x + 0.55, 2.6, c.w - 0.55, 0.3, "label", { color: "ink", keep: true, follows: `Act ${i + 1} title` });
          text(ctx, `Act ${i + 1} title`, "Act title", c.x, 3.25, c.w, 0.8, "h3", { size: 18 });
          text(ctx, `Act ${i + 1} body`, "What happens in this act.", c.x, 4.1, c.w, 2.3, "body");
        });
      },
    },
    {
      id: "L-53", name: "Side panel", category: "Editorial", style: "Bold", density: "Medium",
      description: "Dark panel on the left third with title and lead; two text columns on the right.",
      use_when: "Dense content that needs a strong anchor; executive summaries.",
      tags: "side panel dark sidebar executive summary editorial anchor",
      draw(ctx) {
        rect(ctx, 0, 0, 4.4, H, { fill: "a1", role: "panel", for: "Title" });
        text(ctx, "Kicker", "Section", MX, 0.6, 3.4, 0.3, "label", { color: "a4", optional: true });
        text(ctx, "Title", "Slide title states the takeaway", MX, 1.0, 3.4, 2.6, "title", { color: "paper" });
        text(ctx, "Subtitle", "Framing line", MX, 3.8, 3.4, 1.4, "lead", { color: "a4", optional: true });
        cols(2, 5.0, W - 5.0 - MX, 0.5).forEach((c, i) => {
          hrule(ctx, c.x, 1.0, c.w, { color: "ink", w: 1.25 });
          text(ctx, `Heading ${i + 1}`, "Heading", c.x, 1.15, c.w, 0.5, "h3");
          text(ctx, `Body ${i + 1}`, "Text for this column.", c.x, 1.75, c.w, 4.9, "body");
        });
        text(ctx, "Footer", "Source or confidentiality note", 5.0, 7.0, 6, 0.25, "caption", { optional: true });
      },
    },
    {
      id: "L-54", name: "Vertical sequence", category: "Process", style: "Standard", density: "Medium",
      description: "Title on the left; five numbered steps stacked on the right along a vertical line.",
      use_when: "A method, procedure or chronology of up to five steps with a line of detail each.",
      tags: "steps sequence vertical method procedure process numbered chronology",
      draw(ctx) {
        text(ctx, "Kicker", "Section", MX, 0.45, 4, 0.3, "label", { optional: true });
        text(ctx, "Title", "Slide title states the takeaway", MX, 0.85, 4.2, 2.0, "title");
        text(ctx, "Subtitle", "Framing line", MX, 3.0, 4.0, 1.5, "lead", { optional: true });
        vrule(ctx, 5.75, 0.9, 5.6, { color: "line" });
        for (let i = 0; i < 5; i++) {
          const y = 0.7 + i * 1.2;
          L.ellipse(ctx, 5.5, y + 0.12, 0.5, 0.5, { fill: "ink", follows: `Step ${i + 1}`, role: "label" });
          text(ctx, `Step ${i + 1} number`, L.num(i + 1), 5.5, y + 0.12, 0.5, 0.5, "h3", { size: 14, color: "paper", align: "center", valign: "middle", follows: `Step ${i + 1}` });
          text(ctx, `Step ${i + 1}`, "Step", 6.35, y + 0.1, 6.4, 0.45, "h3", { optional: i > 2 });
          text(ctx, `Step ${i + 1} detail`, "One line of detail", 6.35, y + 0.55, 6.4, 0.55, "small", { optional: true });
        }
        footer(ctx);
      },
    },
  ],
};
