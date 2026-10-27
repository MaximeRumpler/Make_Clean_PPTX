// Process: steps, cycles, flows.
const L = require("../tools/lib.js");
const { C, text, rect, ellipse, line, hrule, vrule } = L;
const { arrow, card } = require("./_kit.js");

module.exports = {
  family: "Process",
  slides: [
    {
      id: "V-PRO-01", name: "Chevron process", category: "Process", kind: "diagram", frame: "full",
      objective: "Describe a process", data_type: "Sequential", dimensions: 1, complexity: "Low",
      description: "Five chevrons in a row, the current one dark, with a short text under each.",
      use_when: "A linear method or phases of a project, 3 to 5 steps.",
      limits: "Delete unused steps with null; keep step names to two or three words.",
      tags: "chevron process steps phases method linear stages arrows",
      related: "V-PRO-04 V-TIM-01",
      fill_notes: "Step n (name), Step n text. Shade the current step with {\"text\", \"fill\": \"a1\"}.",
      draw(ctx, b) {
        const n = 5, ov = 0.25, w = (b.w + ov * (n - 1)) / n;
        for (let i = 0; i < n; i++) {
          const x = b.x + i * (w - ov), on = i === 1;
          text(ctx, `Step ${i + 1}`, `Step ${i + 1}`, x, b.y, w, 0.85, "small", {
            shape: i === 0 ? "homePlate" : "chevron", fill: on ? "a1" : "a6", color: on ? "paper" : "ink",
            bold: true, align: "center", valign: "middle", inset: 0.05, optional: i > 2,
          });
          text(ctx, `Step ${i + 1} text`, "What happens in this step", x + 0.15, b.y + 1.05, w - ov - 0.3, b.h - 1.1, "caption", { color: "ink2", optional: true });
        }
      },
    },
    {
      id: "V-PRO-02", name: "Cycle", category: "Process", kind: "diagram", frame: "wide",
      objective: "Describe a process", data_type: "Sequential", dimensions: 1, complexity: "Low",
      description: "Four steps arranged on a circle with arrows, the centre naming the cycle.",
      use_when: "A recurring loop: continuous improvement, planning cycle, customer lifecycle.",
      limits: "Four steps; for six, use two cycles or a chevron process.",
      tags: "cycle loop circular recurring continuous improvement pdca lifecycle",
      related: "V-PRO-01 V-STR-05",
      fill_notes: "Centre, Step n, Step n text.",
      draw(ctx, b) {
        const r = Math.min(b.h, b.w) / 2 - 0.55, cx = b.x + b.w / 2, cy = b.y + b.h / 2;
        ellipse(ctx, cx - r, cy - r, 2 * r, 2 * r, { line: "line", lw: 1.5 });
        text(ctx, "Centre", "Cycle name", cx - 1.1, cy - 0.4, 2.2, 0.8, "h3", { align: "center", valign: "middle" });
        const pts = [[0, -1], [1, 0], [0, 1], [-1, 0]];
        pts.forEach(([dx, dy], i) => {
          const x = cx + dx * r, y = cy + dy * r, d = 0.9;
          text(ctx, `Step ${i + 1}`, L.num(i + 1), x - d / 2, y - d / 2, d, d, "h3", { shape: "ellipse", fill: i === 0 ? "a1" : "a4", color: i === 0 ? "paper" : "ink", align: "center", valign: "middle", limit: 3 });
          const tx = dx > 0 ? x + 0.55 : dx < 0 ? x - 2.75 : x + 0.55;
          const ty = dy < 0 ? y - 0.45 : dy > 0 ? y - 0.15 : y - 0.35;
          text(ctx, `Step ${i + 1} text`, "Step name and one line", tx, ty, 2.2, 0.7, "caption", { color: "ink2", align: dx < 0 ? "right" : "left", optional: true });
        });
      },
    },
    {
      id: "V-PRO-03", name: "Swimlane flow", category: "Process", kind: "diagram", frame: "full",
      objective: "Describe a process", data_type: "Sequential", dimensions: 2, complexity: "High",
      description: "Three horizontal lanes (one per actor) with process boxes and arrows passing between lanes.",
      use_when: "Who does what in a process with hand-offs: approval workflows, order to cash.",
      limits: "Box positions are fixed; delete unused boxes with null.",
      tags: "swimlane flow workflow actors roles hand off process map approval",
      related: "V-PRO-01 V-FRM-04",
      fill_notes: "Lane n (actor), Box n (activity).",
      draw(ctx, b) {
        const lanes = 3, lh = b.h / lanes, labW = 1.8, cols = 5, cw = (b.w - labW) / cols;
        for (let l = 0; l < lanes; l++) {
          const y = b.y + l * lh;
          rect(ctx, b.x, y, b.w, lh, { fill: l % 2 ? "paper" : "surface", role: "panel", for: `Lane ${l + 1}` });
          text(ctx, `Lane ${l + 1}`, `Actor ${l + 1}`, b.x + 0.15, y, labW - 0.3, lh, "small", { bold: true, color: "ink", valign: "middle", optional: l > 1 });
        }
        vrule(ctx, b.x + labW, b.y, b.h, { color: "line" });
        const boxes = [[0, 0], [1, 1], [2, 1], [3, 2], [4, 0]];
        const bw = cw - 0.45, bh = Math.min(0.75, lh - 0.3);
        const centre = ([c, l]) => [b.x + labW + c * cw + cw / 2, b.y + l * lh + lh / 2];
        boxes.forEach((p, i) => {
          const [x, y] = centre(p);
          text(ctx, `Box ${i + 1}`, "Activity", x - bw / 2, y - bh / 2, bw, bh, "caption", { fill: i === boxes.length - 1 ? "a1" : "paper", line: "ink", role: "card", color: i === boxes.length - 1 ? "paper" : "ink", align: "center", valign: "middle", inset: 0.05, optional: i > 2 });
          if (i) {
            const [px, pyy] = centre(boxes[i - 1]);
            if (Math.abs(pyy - y) < 0.01) arrow(ctx, px + bw / 2, y, x - bw / 2, y, { follows: `Box ${i + 1}` });
            else { line(ctx, px + bw / 2, pyy, x, pyy, { color: "ink", w: 1, follows: `Box ${i + 1}`, markN: " elbow" }); arrow(ctx, x, pyy, x, y + (y > pyy ? -bh / 2 : bh / 2), { follows: `Box ${i + 1}` }); }
          }
        });
      },
    },
    {
      id: "V-PRO-04", name: "Stage-gate", category: "Process", kind: "diagram", frame: "full",
      objective: "Describe a process", data_type: "Sequential", dimensions: 1, complexity: "Medium",
      description: "Four stages as bars separated by diamond decision gates, with criteria under each gate.",
      use_when: "Development or investment process with go / no-go decisions.",
      limits: "Four stages and three gates; gate criteria in a few words.",
      tags: "stage gate phase gate go no go decision milestones innovation development",
      related: "V-PRO-01 V-TIM-01",
      fill_notes: "Stage n, Gate n, Gate n criteria.",
      draw(ctx, b) {
        const n = 4, gd = 0.7, sw = (b.w - (n - 1) * (gd + 0.2)) / n, y = b.y + 0.3;
        for (let i = 0; i < n; i++) {
          const x = b.x + i * (sw + gd + 0.2);
          text(ctx, `Stage ${i + 1}`, `Stage ${i + 1}`, x, y, sw, 0.8, "small", { fill: "surface", role: "card", color: "ink", bold: true, align: "center", valign: "middle" });
          text(ctx, `Stage ${i + 1} text`, "Main activities", x, y + 0.95, sw, b.h - 1.3, "caption", { color: "ink2", optional: true });
          if (i < n - 1) {
            const gx = x + sw + 0.1;
            text(ctx, `Gate ${i + 1}`, `G${i + 1}`, gx, y + 0.05, gd, gd, "caption", { shape: "diamond", fill: "a1", color: "paper", bold: true, align: "center", valign: "middle", limit: 4 });
            text(ctx, `Gate ${i + 1} criteria`, "Decision criteria", gx - 0.35, y + 0.95, gd + 0.7, b.h - 1.3, "caption", { align: "center", optional: true });
          }
        }
      },
    },
    {
      id: "V-PRO-05", name: "Customer journey", category: "Process", kind: "diagram", frame: "full",
      objective: "Describe a process", data_type: "Sequential", dimensions: 2, complexity: "High",
      description: "Journey stages in columns; rows for actions, touchpoints and pain points.",
      use_when: "Map an experience end to end: customer, employee or user journey.",
      limits: "Five stages and three rows; keep cells to a few words.",
      tags: "customer journey experience stages touchpoints pain points user map",
      related: "V-PRO-01 V-PRO-03",
      fill_notes: "Stage n; Row n label; Cell r-c.",
      draw(ctx, b) {
        const n = 5, labW = 1.9, cw = (b.w - labW) / n, rows = ["Actions", "Touchpoints", "Pain points"], rh = (b.h - 0.85) / rows.length;
        for (let c = 0; c < n; c++) {
          text(ctx, `Stage ${c + 1}`, `Stage ${c + 1}`, b.x + labW + c * cw, b.y, cw + 0.2, 0.7, "caption", {
            shape: c === 0 ? "homePlate" : "chevron", fill: "a1", color: "paper", bold: true, align: "center", valign: "middle", optional: c > 2,
          });
        }
        rows.forEach((r, i) => {
          const y = b.y + 0.85 + i * rh;
          hrule(ctx, b.x, y, b.w, { color: "line" });
          text(ctx, `Row ${i + 1}`, r, b.x, y + 0.1, labW - 0.15, rh - 0.2, "label", { color: "ink", keep: true });
          for (let c = 0; c < n; c++) text(ctx, `Cell ${i + 1}-${c + 1}`, "Short text", b.x + labW + c * cw + 0.15, y + 0.1, cw - 0.25, rh - 0.2, "caption", { color: "ink2", optional: true });
        });
      },
    },
    {
      id: "V-PRO-06", name: "Double diamond", category: "Process", kind: "diagram", frame: "full",
      objective: "Describe a process", data_type: "Sequential", dimensions: 1, complexity: "Low",
      description: "Two diamonds side by side: diverge then converge on the problem, then on the solution.",
      use_when: "Design or innovation method: discover, define, develop, deliver.",
      limits: "Four phases.",
      tags: "double diamond design thinking diverge converge discover define develop deliver innovation",
      related: "V-PRO-01 V-PRO-02",
      fill_notes: "Phase n, Phase n text, Milestone n.",
      draw(ctx, b) {
        const dw = b.w / 2, dh = b.h - 1.2;
        [0, 1].forEach((k) => {
          text(ctx, `Diamond ${k + 1}`, " ", b.x + k * dw, b.y, dw, dh, "caption", { shape: "diamond", fill: k ? "a5" : "a6", limit: 2, optional: true });
          vrule(ctx, b.x + k * dw + dw / 2, b.y + 0.15, dh - 0.3, { color: "paper", w: 1.5 });
        });
        for (let i = 0; i < 4; i++) {
          const x = b.x + i * (dw / 2);
          text(ctx, `Phase ${i + 1}`, `Phase ${i + 1}`, x + 0.2, b.y + dh / 2 - 0.2, dw / 2 - 0.4, 0.4, "small", { bold: true, color: "ink", align: "center" });
          text(ctx, `Phase ${i + 1} text`, "What happens", x + 0.1, b.y + dh + 0.15, dw / 2 - 0.2, 1.0, "caption", { color: "ink2", align: "center", optional: true });
        }
        text(ctx, "Milestone 1", "Problem defined", b.x + dw - 1.2, b.y - 0.02, 2.4, 0.3, "caption", { align: "center", color: "ink", optional: true, keep: true });
        text(ctx, "Milestone 2", "Solution delivered", b.x + 2 * dw - 2.4, b.y - 0.02, 2.4, 0.3, "caption", { align: "right", color: "ink", optional: true, keep: true });
      },
    },
    {
      id: "V-PRO-07", name: "Staircase", category: "Process", kind: "diagram", frame: "full",
      objective: "Show maturity", data_type: "Ordinal", dimensions: 1, complexity: "Low",
      description: "Four rising steps, darker as they climb, each with a level name and its description.",
      use_when: "Maturity levels, capability growth, a progression plan.",
      limits: "Four levels; mark where we are by shading a step.",
      tags: "staircase maturity levels progression steps growth capability ladder",
      related: "V-FRM-05 V-PRO-01",
      fill_notes: "Level n, Level n text.",
      draw(ctx, b) {
        const n = 4, w = b.w / n, stepH = (b.h - 1.6) / n;
        for (let i = 0; i < n; i++) {
          const h = stepH * (i + 1) + 0.4, x = b.x + i * w, y = b.y + b.h - h;
          rect(ctx, x + 0.04, y, w - 0.08, h, { fill: ["a6", "a4", "a2", "a1"][i], role: "card", for: `Level ${i + 1}` });
          text(ctx, `Level ${i + 1}`, `Level ${i + 1}`, x + 0.2, y + 0.15, w - 0.4, 0.4, "small", { bold: true, color: i > 1 ? "paper" : "ink" });
          text(ctx, `Level ${i + 1} text`, "What this level looks like", x + 0.2, y - 1.1, w - 0.4, 1.0, "caption", { color: "ink2", valign: "bottom", optional: true });
        }
      },
    },
  ],
};
