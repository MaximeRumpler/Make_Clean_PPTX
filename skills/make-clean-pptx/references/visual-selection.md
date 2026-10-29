# Choosing a visual

The visuals library is indexed by **what the visual does for the reader**, not by business domain: a risk matrix serves finance as well as HR. Choose in four steps, then check the limits.

## 1. Restate the request as four attributes

1. **Objective**: what the reader must understand (table below).
2. **Data shape**: quantitative, time series, ordinal (scores, levels), qualitative, hierarchical, relational, sequential.
3. **Dimensions** shown at once: one measure; two axes; three (axes + size).
4. **Audience**: executives and non-specialists → prefer `complexity: Low`.

## 2. Words in the request → objective

| The request says… | Objective (`objective` column) |
|---|---|
| strengths and weaknesses, causes, why, state of play | Diagnose |
| compare, versus, benchmark, ranking, against | Compare |
| trend, evolution, over time, from X to Y | Show change |
| bridge, contribution, breakdown, what makes up, mix, share | Break down |
| spread, distribution, range, concentration | Show distribution |
| link between, correlation, influence of X on Y | Show relationship |
| maturity, levels, where do we stand | Show maturity |
| prioritise, sort, where to start, quick wins | Prioritise |
| segment, categorise, profiles | Segment |
| choose between, arbitrate, recommend an option | Decide |
| plan, schedule, roadmap, milestones | Plan |
| track, monitor, dashboard, progress, achievement | Track performance |
| risks, exposure, criticality, sensitivity | Assess risk |
| organisation, structure, architecture, governance, model | Describe a structure |
| process, steps, flow, workflow, method | Describe a process |
| a metaphor, a tone, an identity, "make it memorable" | Set the tone (Signature visuals only, see section 6) |

```bash
python3 scripts/read_index.py visuals --where objective="break down"
python3 scripts/read_index.py visuals -q "variance budget actual contribution"
```

## 3. Data shape → family

| Data | Prefer | Ids |
|---|---|---|
| One value and its target | KPI, progress | V-KPI-01, V-KPI-02, V-CMP-03 |
| One series over time | line, area | V-EVO-01, V-KPI-03 |
| Change between two totals | waterfall | V-COM-01 |
| Same items at two moments | two periods, slope | V-CMP-02, V-CMP-05 |
| Ranking on one measure | ranked bars, Pareto | V-CMP-01, V-REL-05 |
| Parts of a whole | donut (≤ 5 parts), mix bars, stacked columns | V-COM-03, V-COM-02, V-COM-06 |
| Steps losing volume | funnel | V-COM-05 |
| Two scored criteria | 2x2, impact/effort, positioning | V-MAT-01, V-MAT-03, V-MAT-06 |
| Two criteria and a size | bubble portfolio | V-REL-02 |
| Likelihood × impact | risk matrix, tornado | V-MAT-04, V-CMP-04 |
| Values over two dimensions | heatmap | V-REL-04 |
| Options × criteria | scored comparison, RACI | V-CMP-06, V-FRM-04 |
| Hierarchy | org chart, logic tree, pyramid, half-ring layers | V-STR-01, V-STR-02, V-STR-03, V-STR-09 |
| Actors and links | hub and spoke, Venn | V-STR-05, V-STR-06 |
| Ordered steps | chevrons, stage-gate, swimlane, cycle | V-PRO-01, V-PRO-04, V-PRO-03, V-PRO-02 |
| Dates and work | milestones, roadmap lanes, Gantt, now-next-later | V-TIM-01, V-TIM-02, V-TIM-03, V-TIM-05 |
| Six to eight steps in order | serpentine timeline | V-TIM-06 |
| Known management tool | SWOT, five forces, PESTEL, BMC, value chain, OKR | V-MAT-02, V-FRM-02, V-FRM-03, V-FRM-01, V-FRM-06, V-FRM-05 |

When the request names a known tool (SWOT, RACI, Gantt, waterfall), go straight to it.

## 4. Cautions (they make the difference between a chart and a message)

- **Pie only for 2 or 3 very unequal parts** (V-COM-04). Otherwise a donut with ≤ 5 parts, or sorted bars.
- **No gauges to compare several values**: use progress to target (V-CMP-03) or a trend table (V-EVO-05).
- **A change between two dates is explained by a waterfall**, not by two bars.
- **More than 5 lines → small multiples** (V-EVO-06).
- **Sort bars** by value unless the categories have a natural order (time, stages).
- **Axis labels and units are part of the message**: fill the notes and axis fields.
- **Never chart invented numbers.** If the user gave no data, pick a qualitative visual or a text layout.
- Read the `limits` and `fill_notes` columns before filling: they say how many items fit and how to give the data.

## 5. Pair with a layout

The visual goes into a frame of a layout. Pick the layout for what must be *said* around the visual:

| Need | Layout |
|---|---|
| The visual is the message | L-31 Full visual |
| The visual needs reading help | L-32 Visual and key points |
| Three things to notice | L-33 Visual with three callouts |
| Two visuals side by side | L-34 Two visuals |
| A trend and its two headline figures | L-35 Visual and two figures |
| Four indicators read together | L-36 Dashboard |

Check the `frame` column: `full` visuals belong in L-31 / L-33, `wide` in L-32 / L-35, `half` in L-34. The builder scales the visual to the frame and warns if text gets too small.

## 6. Signature visuals: sparingly, on purpose

The **Signature** family (`V-SIG-*`: meshing gears, light bulb, puzzle, winding road, mountain and summit flag, target) holds metaphor illustrations that give a deck a recognisable tone. A metaphor is strong once and tiring the third time, and a deck full of them reads as clip art, so they are opt-in: hidden from searches unless asked for (`read_index.py visuals --category signature`, see index-schema.md).

- **Only when** the user asks for a tone, an identity or "something memorable", or when the metaphor genuinely *is* the message (parts that drive each other: gears; four parts that make a whole: puzzle; an ambition reached in stages: mountain).
- **How many: no fixed number.** Judge per deck from the request, the audience and the content style: a sober board update may need none, a keynote or workshop deck can carry more. Typical places: the opening of a chapter, the closing vision. Never as filler.
- **Usually one metaphor per deck**: gears on slide 3 and a puzzle on slide 9 read as clip art. Reuse the same one when a second is needed, unless the request calls for more.
- **Never for figures or data**: the labels are words. A real plan goes on a timeline (V-TIM-01), real scopes on concentric circles (V-STR-08).
- Prefer the ordinary visual whenever it says the same thing: the signature is a seasoning, not the meal.

## 7. Expressive compositions: one strong shape, on request

The **Expressive** family holds compositions with a strong shape, for the one slide that should stand out. The first is the **orbital diagram**: a centre and the things that revolve around it (`V-ORB-01-<n>` one orbit with 3 to 8 satellites, `V-ORB-02-<inner>x<outer>` two orbits for a close and a wider circle, `V-ORB-03-<n>` a half orbit for a half frame). They are opt-in like the signature visuals (`read_index.py visuals --category expressive`).

- **Only when** the user asks for it, or when there is a real centre and satellites (an ecosystem, stakeholders around a product, capabilities around a core). Items that are merely parallel go in a list or a grid.
- **Pick the variant for the exact count**: positions are computed for it, so there is no satellite to delete. Satellites read clockwise from 12 o'clock.
- **Short words only**: labels of 16 characters, a text of 40 beside each satellite. Denser text goes to V-STR-05 (hub and spoke); more than 8 items go to a list layout.
- **Sparingly, judged per deck**: it is the slide that stands out, so how many depends on the request and the tone of the content, not on a fixed count.
