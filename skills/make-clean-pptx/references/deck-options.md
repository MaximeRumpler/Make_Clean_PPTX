# Deck options: format, confidentiality, accessibility

The user settles these in the single question message of step 1 (or you state the defaults when you cannot ask). They apply to the whole process, not only to delivery. Ask again only if the user changes their mind.

The defaults add nothing: a PowerPoint file, no label, the usual sources. Labels, restrictions and checks apply only when the user chooses them. If the content clearly looks sensitive (client names, salaries, unreleased results) and the user did not choose, suggest the confidential option in one line; do not apply it on your own.

## Format

| Choice | What you do |
|---|---|
| PowerPoint `.pptx` (default) | Build as usual and hand over the `.pptx`. |
| LibreOffice `.odp` | Build the `.pptx`, add `--odp` to the last `render_check.py` run, hand over the `.odp` (and the `.pptx`, which LibreOffice also opens). |
| Both | Hand over both files. |

Google Slides and Keynote import `.pptx`: mention it if the user names them.

## Confidentiality

Why it matters beyond the label: an online icon or photo search sends your query, and so the topic of the deck, to an outside service; file properties travel with the file; speaker notes are often forgotten when a deck is forwarded.

| Choice | Label | Online sources (icons, photos) | File properties | Speaker notes |
|---|---|---|---|---|
| No label (default) | none | allowed | title only | as usual |
| Internal | `Internal` in every `Footer` field | allowed for icons; photos only with generic queries that do not reveal the subject | title only, no author unless the user gives one | as usual |
| Confidential | `Confidential` in every `Footer` field | **none**: bundled Lucide icons only (`find_icon.py` without `--source`), no `fetch_image.py` | title only, no author, no keywords, no subject | only what the user wrote; tell them notes travel with the file |
| I can't share the real content | `Confidential` in every `Footer` field | none | as confidential | instructions only |

How to apply the label: fill each layout's `Footer` field with the label (in the deck's language: `Interne`, `Confidentiel` for French content). If a slide has no `Footer` field, do not add shapes for it; say in the delivery message which slides carry no label. Write the label exactly as chosen; do not invent classification levels.

### When the user cannot share the real content

Build a **skeleton deck**: choose layouts and visuals from the structure the user describes (for example "slide 3: one key figure; slide 4: three reasons"), and fill every field with an instruction in square brackets giving its limit, such as `[Key figure, max 6 characters]` or `[Reason 2, max 60 characters]`. Charts get neutral placeholder series and the chart title `[Dummy data: replace with your figures]`. Never ask for the real values and never invent plausible ones. In the delivery message, tell the user to open the deck in PowerPoint or LibreOffice and type their content locally, and that `lint_deck.py` can check it afterwards on their own computer.

## Accessibility (optional)

Standard (default): what every deck already gets: the language tag, headlines that state the message, theme contrast, alt text on photos, and the lint's warnings.

Extra care, only when the user chooses it or asks for an accessible deck:

- Alt text on every photo, illustration and meaningful icon (`"alt"` in the value); purely decorative icons get no alt text.
- Charts: the headline says what the chart shows, and the speaker notes give the key values in one or two sentences (charts have no alt text field yet).
- Run `lint_deck.py --contrast` on the built deck: it measures every text against the fill under it with the deck's own theme (4.5:1, or 3:1 for large text) and fix what it reports. See `theme-contract.md`.
- Never let colour carry meaning alone: label series and categories directly, add values or a word ("risk", "on track") next to any colour code.
- Prefer layouts with fewer, larger text fields; never more text than the field's limit.
- Every slide keeps a visible title; do not leave a slide with only a visual.
- In the delivery message, say what was done and what to check by hand. Be honest about one known limit: PowerPoint's *Check Accessibility* may report missing slide titles, because titles are named text boxes, not title placeholders.

Never call the deck "compliant" or "certified": say it was prepared with extra accessibility care. Formal standards (WCAG, EN 301 549, PDF/UA) are a separate, optional check that the user asks for.

## Delivery message

Say in one line which options were applied, for example: "PowerPoint file, marked Internal in the footer, about 8 slides." For confidential decks add: "No online sources were used; check the speaker notes before sharing."
