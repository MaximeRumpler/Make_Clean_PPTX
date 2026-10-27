// Covers, agendas and dividers.
const L = require("../tools/lib.js");
const { MX, CW, W, H, text, rect, hrule, vrule, image, chrome, footer, background } = L;

const cols = (n, x0 = MX, w = CW, gut = L.GUT) => {
  const cw = (w - gut * (n - 1)) / n;
  return Array.from({ length: n }, (_, i) => ({ x: x0 + i * (cw + gut), w: cw }));
};

function coverMeta(ctx, y, dark) {
  const c = dark ? "a4" : undefined;
  text(ctx, "Author", "Author or team", MX, y, 4, 0.3, "caption", { color: c, optional: true });
  text(ctx, "Date", "Date", MX + 4.3, y, 3, 0.3, "caption", { color: c, optional: true });
}

module.exports = {
  family: "Opening",
  slides: [
    {
      id: "L-01", name: "Cover, title left", category: "Cover", style: "Standard", density: "Low",
      description: "White cover: kicker, large left-aligned title, subtitle, a rule and author/date line.",
      use_when: "Default opening for reports, reviews and proposals.",
      tags: "cover title opening first slide intro report",
      draw(ctx) {
        L.logo(ctx); // first on this slide since v1.0: kept there so its ids do not change
        text(ctx, "Kicker", "Context or event", MX, 2.3, 8, 0.3, "label", { optional: true });
        text(ctx, "Title", "Presentation title", MX, 2.7, 9.2, 1.9, "hero", { valign: "bottom" });
        text(ctx, "Subtitle", "What this presentation is about, in one line", MX, 4.75, 8.5, 0.7, "lead", { optional: true });
        hrule(ctx, MX, 6.3, CW, { color: "ink", w: 1 });
        coverMeta(ctx, 6.45);
      },
    },
    {
      id: "L-02", name: "Cover, dark", category: "Cover", style: "Bold", density: "Low",
      description: "Full dark cover with white title, muted subtitle and meta line.",
      use_when: "Executive or keynote opening that needs presence.",
      tags: "cover dark black inverted keynote executive opening",
      draw(ctx) {
        background(ctx, "a1");
        text(ctx, "Kicker", "Context or event", MX, 2.3, 8, 0.3, "label", { color: "a4", optional: true });
        text(ctx, "Title", "Presentation title", MX, 2.7, 9.6, 1.9, "hero", { color: "paper", valign: "bottom" });
        text(ctx, "Subtitle", "What this presentation is about, in one line", MX, 4.75, 8.5, 0.7, "lead", { color: "a5", optional: true });
        hrule(ctx, MX, 6.3, CW, { color: "a2", w: 0.75 });
        coverMeta(ctx, 6.45, true);
        L.logo(ctx);
      },
    },
    {
      id: "L-03", name: "Cover, typographic", category: "Cover", style: "Editorial", density: "Low",
      description: "Very large centred title between two thin rules, short line below, date at the bottom.",
      use_when: "Short punchy title (two to five words), editorial or manifesto tone.",
      tags: "cover typographic editorial big title centred manifesto",
      draw(ctx) {
        hrule(ctx, MX, 1.9, CW, { color: "ink", w: 1 });
        text(ctx, "Title", "Short title", MX, 2.25, CW, 2.4, "display", { align: "center", valign: "middle" });
        text(ctx, "Subtitle", "One line that sets the scene", MX + 2, 4.75, CW - 4, 0.6, "lead", { align: "center", optional: true });
        hrule(ctx, MX, 5.6, CW, { color: "ink", w: 1 });
        text(ctx, "Date", "Date", MX, 6.6, CW, 0.3, "caption", { align: "center", optional: true });
        L.logo(ctx, "center");
      },
    },
    {
      id: "L-04", name: "Cover, split image", category: "Cover", style: "Standard", density: "Low",
      description: "Title block on the left half, full-height picture on the right half.",
      use_when: "Opening that benefits from a strong photo (place, product, people).",
      tags: "cover image photo split half picture visual opening",
      draw(ctx) {
        image(ctx, "Photo", W / 2, 0, W / 2, H);
        text(ctx, "Kicker", "Context or event", MX, 2.2, 5.4, 0.3, "label", { optional: true });
        text(ctx, "Title", "Presentation title", MX, 2.6, 5.5, 2.2, "hero", { valign: "bottom" });
        text(ctx, "Subtitle", "What this presentation is about", MX, 4.9, 5.3, 0.8, "lead", { optional: true });
        coverMeta(ctx, 6.45);
        L.logo(ctx);
      },
    },
    {
      id: "L-05", name: "Cover, side band", category: "Cover", style: "Bold", density: "Low",
      description: "Dark vertical band on the left third with context and date; title and subtitle on the right.",
      use_when: "Formal opening with a strong structure; works well for board and committee decks.",
      tags: "cover band sidebar vertical formal board committee",
      draw(ctx) {
        rect(ctx, 0, 0, 4.2, H, { fill: "a1", role: "panel", for: "Title" });
        text(ctx, "Kicker", "Context or event", MX, 0.8, 3.0, 0.6, "label", { color: "a4", optional: true });
        text(ctx, "Date", "Date", MX, 6.45, 3.0, 0.3, "caption", { color: "a4", optional: true });
        text(ctx, "Title", "Presentation title", 4.9, 2.5, 7.8, 1.9, "hero", { valign: "bottom" });
        text(ctx, "Subtitle", "What this presentation is about, in one line", 4.9, 4.55, 7.2, 0.7, "lead", { optional: true });
        text(ctx, "Author", "Author or team", 4.9, 6.45, 6, 0.3, "caption", { optional: true });
        L.logo(ctx, "right");
      },
    },
    {
      id: "L-06", name: "Agenda, numbered", category: "Agenda", style: "Standard", density: "Medium",
      description: "Six numbered agenda items on a two-column grid, each with a short detail line.",
      use_when: "Table of contents for decks with three to six parts.",
      tags: "agenda contents summary outline plan sommaire numbered",
      draw(ctx) {
        chrome(ctx, { titlePh: "Agenda", titleKeep: true });
        const cc = cols(2);
        for (let i = 0; i < 6; i++) {
          const c = cc[i % 2], y = 2.3 + Math.floor(i / 2) * 1.45;
          hrule(ctx, c.x, y, c.w, { color: "line", follows: `Item ${i + 1}` });
          text(ctx, `Number ${i + 1}`, L.num(i + 1, "padded"), c.x, y + 0.15, 0.9, 0.6, "h3", { size: 24, color: "muted", follows: `Item ${i + 1}` });
          text(ctx, `Item ${i + 1}`, `Part ${i + 1} title`, c.x + 1.0, y + 0.18, c.w - 1.0, 0.4, "h3", { optional: i > 1 });
          text(ctx, `Item ${i + 1} detail`, "Short description of this part", c.x + 1.0, y + 0.62, c.w - 1.0, 0.6, "small", { optional: true });
        }
      },
    },
    {
      id: "L-07", name: "Agenda, timed sessions", category: "Agenda", style: "Standard", density: "Medium",
      description: "Rows of sessions with time, title and owner, separated by thin rules.",
      use_when: "Workshop, seminar or meeting programme with times and speakers.",
      tags: "agenda programme schedule workshop meeting times sessions speakers",
      draw(ctx) {
        chrome(ctx, { titlePh: "Programme", titleKeep: true, lead: true });
        for (let i = 0; i < 6; i++) {
          const y = 2.3 + i * 0.72;
          hrule(ctx, MX, y, CW, { color: i === 0 ? "ink" : "line", w: i === 0 ? 1 : 0.75, follows: i ? `Session ${i + 1}` : undefined });
          text(ctx, `Time ${i + 1}`, "00:00", MX, y + 0.16, 1.4, 0.4, "h3", { optional: true });
          text(ctx, `Session ${i + 1}`, "Session title", MX + 1.6, y + 0.16, 6.6, 0.4, "body", { bold: true, optional: i > 1 });
          text(ctx, `Owner ${i + 1}`, "Speaker or owner", MX + 8.6, y + 0.16, CW - 8.6, 0.4, "small", { color: "muted", optional: true });
        }
      },
    },
    {
      id: "L-08", name: "Agenda, active chapter", category: "Agenda", style: "Standard", density: "Low",
      description: "Chapter list on the left with the current one highlighted; chapter number and title large on the right.",
      use_when: "Reminder of where we are, between parts of a long deck.",
      tags: "agenda progress chapter marker where we are navigation transition",
      draw(ctx) {
        for (let i = 0; i < 5; i++) {
          const y = 1.6 + i * 0.85, on = i === 1;
          if (on) rect(ctx, MX, y, 0.06, 0.55, { fill: "ink" });
          text(ctx, `Chapter ${i + 1}`, `Chapter ${i + 1}`, MX + 0.25, y + 0.08, 3.6, 0.45, "body", { bold: on, color: on ? "ink" : "muted", optional: i > 2 });
        }
        vrule(ctx, 4.7, 1.4, 4.6, { color: "line" });
        text(ctx, "Number", "02", 5.3, 1.6, 3, 1.4, "display", { size: 80, color: "a3" });
        text(ctx, "Title", "Current chapter title", 5.3, 3.2, 7.2, 1.3, "hero", { size: 34 });
        text(ctx, "Subtitle", "What this chapter answers", 5.3, 4.6, 6.8, 0.8, "lead", { optional: true });
        footer(ctx);
      },
    },
    {
      id: "L-09", name: "Chapter divider, dark", category: "Divider", style: "Bold", density: "Low",
      description: "Dark full slide with a large chapter number, chapter title and one framing line.",
      use_when: "Start of a new part in decks of fifteen slides or more.",
      tags: "divider section chapter break separator dark transition",
      draw(ctx) {
        background(ctx, "a1");
        text(ctx, "Number", "01", MX, 1.4, 4, 1.6, "display", { size: 96, color: "a3" });
        text(ctx, "Title", "Chapter title", MX, 3.3, 10, 1.3, "hero", { color: "paper" });
        text(ctx, "Subtitle", "What this chapter covers", MX, 4.7, 8, 0.8, "lead", { color: "a4", optional: true });
        footer(ctx, true);
      },
    },
    {
      id: "L-10", name: "Divider with key figure", category: "Divider", style: "Editorial", density: "Low",
      description: "Light divider: chapter title on the left, one large figure and its caption on the right.",
      use_when: "Opening a chapter with the single number that motivates it.",
      tags: "divider section key figure number hook chapter",
      draw(ctx) {
        text(ctx, "Kicker", "Chapter 01", MX, 2.4, 5.5, 0.3, "label", { optional: true });
        text(ctx, "Title", "Chapter title", MX, 2.8, 5.6, 1.8, "hero", { size: 36 });
        vrule(ctx, 6.9, 2.2, 3.4, { color: "ink", w: 1 });
        text(ctx, "Number", "00%", 7.4, 2.3, 5.3, 1.8, "display", { size: 88 });
        text(ctx, "Number caption", "What the figure measures and its source", 7.4, 4.25, 5, 0.9, "body", { optional: true });
        footer(ctx);
      },
    },
    {
      id: "L-11", name: "Transition, seen and next", category: "Divider", style: "Standard", density: "Medium",
      description: "Two columns: what has been covered (muted) and what comes next (strong), split by a rule.",
      use_when: "Bridge between the diagnosis and the proposal, or between two parts.",
      tags: "transition recap next so far bridge seen coming up",
      draw(ctx) {
        chrome(ctx, { titlePh: "Where we are", titleKeep: true });
        const cc = cols(2, MX, CW, 0.9);
        text(ctx, "Left label", "So far", cc[0].x, 2.3, cc[0].w, 0.3, "label", { keep: true });
        text(ctx, "Left points", ["Point already covered", "Point already covered", "Point already covered"], cc[0].x, 2.75, cc[0].w, 3.6, "body", { bullets: true, color: "muted" });
        vrule(ctx, MX + CW / 2, 2.3, 4.1, { color: "line" });
        text(ctx, "Right label", "Next", cc[1].x, 2.3, cc[1].w, 0.3, "label", { color: "ink", keep: true });
        text(ctx, "Right points", ["Point coming next", "Point coming next", "Point coming next"], cc[1].x, 2.75, cc[1].w, 3.6, "body", { bullets: true, color: "ink" });
      },
    },
  ],
};
module.exports.cols = cols;
