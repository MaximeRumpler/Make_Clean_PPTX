# Layout and storytelling rules

Read this before planning the slides. The goal is a deck a busy person understands in one pass. These rules explain *why*, so you can adapt them when a case is unusual.

## Shape of the deck

1. **Cover** (L-01 to L-05): title + one-line promise; date or author only if the user gave them.
2. **Agenda** (L-06, L-07) only when there are more than ~7 content slides. In long decks, L-08 reminds where we are.
3. **Body**, grouped in 2-4 chapters; a divider (L-09 to L-11) per chapter when there are 3 or more.
4. **Closing**: the decision, next steps or call to action (L-47, L-48), then contacts (L-49) if provided. Never a bare "Thank you" as the only ending.

Length: roughly one slide per minute of talk, or one per key message when no time is given. Six strong slides beat twelve padded ones.

## One slide, one message

- Write the **headline as the conclusion** ("Churn halved after the onboarding redesign"), not as a topic ("Churn"). Reading only the headlines should tell the story.
- 3 to 5 bullets at most, each under ~12 words. More: split the slide or move the detail to the speaker notes.
- Numbers: lead with the figure, then the label. Keep units and rounding consistent across slides.

## From the message to the layout

Choose the layout for **what the message is**, before thinking of style:

| The message is… | Layouts |
|---|---|
| one sentence to remember | L-12 Key message |
| one figure that proves the point | L-13 Figure and interpretation, L-17 Central figure, L-10 Divider with key figure |
| a quotation (real) | L-14 Big quote |
| the question to settle | L-15 Strategic question |
| a stance and its reasons | L-16 Position and three arguments |
| an explanation | L-18 Title and text, L-23 Main content and sidebar, L-24 Text with takeaway box |
| two, three or four parallel items | L-19 Two columns, L-20 Three columns with icons, L-21 Four columns, L-22 Four cards |
| findings and their consequences | L-25 Findings and implications |
| a problem to investigate | L-26 Problem and hypotheses |
| a picture carries it | L-27 Text and image, L-28 Full image, L-29 Case study |
| people | L-30 Team of four |
| a chart or diagram | frames L-31 to L-36, with a visual (see visual-selection.md) |
| a few figures | L-37 to L-40 |
| detail to read row by row | L-41 Table and takeaway, L-42 Action plan |
| a choice | L-43 Two options, L-44 Recommended option, L-45 Three options, L-46 Before and after |
| a rich overview or a narrative | L-50 Bento, L-51 Bands, L-52 Story in four acts, L-53 Side panel, L-54 Vertical sequence |

Then refine with the index: `use_when`, `density`, `style` (Standard, Editorial, Bold).

## Rhythm and variety

- **Never the same layout three times in a row**, and no layout for more than a third of the deck.
- Alternate **dense and airy** slides (`density` column): after a table, a statement or a figure.
- Use the **Bold** layouts (dark covers, dividers, panels) sparingly: two or three per deck give structure, more make it heavy.
- A plain text slide between two visual ones is fine. Do not chase novelty.
- **Signature visuals** (gears, bulb, puzzle, road, mountain, target): sparingly, a single metaphor, only when asked for or when the metaphor is the message; how many depends on the request and the deck (visual-selection.md, sections 6 and 7).

## Fitting the text

- Respect the **character limits** (`≤N` in the index card). If your text is 30% over, the layout is wrong, not the text: pick a roomier one or cut words.
- Unused optional slots disappear on their own; set any other unused field to `null`. Never leave a placeholder.
- Pick the layout with the **right number of items**. Three points on a four-column layout leaves a hole; delete or choose L-20.

## Charts and numbers

- Only chart data the user gave you. Never fabricate a trend to make a slide look complete.
- Say what the chart shows in the headline ("Sales up 18% year on year") and give the source in the `Source` field.
- At most ~6 categories and 3 series per chart; round labels to what the audience needs.

## Icons

- Icons **support** a label, they never replace it. Use them on parallel items (L-20) or small cards, not on every slide.
- One family per deck (the bundled Lucide set by default). Do not mix line and filled styles.
- Pick literal, widely understood icons (shield for security, users for people). Abstract concepts often read better without an icon.

## Images

- An image must carry meaning (a place, a product, a mood that matters). Decorative filler adds noise.
- One strong image beats several weak ones; match the orientation of the slot (wide vs portrait).
- No images with text, logos, watermarks or recognisable people unless the user supplied them. Always real alt text, always the credit.

## Text details

- The user's terminology and language; a consistent tone.
- Sentence case; no ALL CAPS beyond the small labels the layouts already style.
- No full stop at the end of headlines and short bullets.
- `**bold**` for at most one key phrase per slide.
- Story, caveats and sources go to the **speaker notes**.

## Final check

Read only the headlines in order: they should tell the whole story. Then the contact sheet: rhythm, nothing empty, nothing cramped, no repeated run. Details in `review-checklist.md`.
