# Index schema

Each library has one index: `assets/layouts.csv` and `assets/visuals.csv`. The agent reads the index instead of opening every slide, so the quality of the index decides the quality of the choices. In this repository the indexes are **generated** with the libraries (`library/tools/build_index.py`), so they cannot drift from the slides.

- CSV, separator `;`, UTF-8, first row = header. `.xlsx` with the same columns is also accepted (first sheet, or a sheet named `index`).
- Column order does not matter and names are matched loosely (`ALIASES` in `scripts/read_index.py`); extra columns are kept and can be filtered with `read_index.py --where column=value`.
- One row per layout slide, or per visual component.

## Columns

| Column | Layouts | Visuals | Content |
|---|:---:|:---:|---|
| `id` | ✓ | ✓ | stable id used in specs: `L-01`…, `V-CMP-01`… (also the group name of the visual) |
| `slide` | ✓ | ✓ | 1-based position in the pptx |
| `name` | ✓ | ✓ | short human name |
| `category` | ✓ | ✓ | family used for browsing (see below) |
| `style` | ✓ | | `Standard`, `Editorial` (typographic, airy) or `Bold` (dark surfaces) |
| `density` | ✓ | | `Low`, `Medium`, `High`: how much text the slide holds |
| `kind` | | ✓ | `chart` (native, data-driven), `diagram`, `matrix`, `table`, `timeline`, `illustration` (a metaphor drawing, see opt-in rows) |
| `frame` | | ✓ | native size: `full` (12.1 × 4.6 in), `wide` (7.9 × 4.6), `half` (5.9 × 4.2) |
| `objective` | | ✓ | controlled vocabulary, see visual-selection.md |
| `data_type` | | ✓ | `Quantitative`, `Time series`, `Ordinal`, `Qualitative`, `Hierarchical`, `Relational`, `Sequential` |
| `dimensions` | | ✓ | how many dimensions it shows at once |
| `complexity` | | ✓ | `Low`, `Medium`, `High` (prefer Low for executives) |
| `description` | ✓ | ✓ | what is *visible*, in one sentence |
| `use_when` | ✓ | ✓ | the message or situation it is *for* |
| `limits` | | ✓ | capacity and caveats (max items, data rules) |
| `fill_notes` | | ✓ | how to give the data |
| `tags` | ✓ | ✓ | search words, synonyms included |
| `related` | | ✓ | close alternatives |
| `fields` | ✓ | ✓ | the editable fields, see below |

Categories: layouts use Cover, Agenda, Divider, Statement, Text, Media, Team, Frame, KPI, Table, Decision, Closing, Editorial, Process. Visuals use Compare, Evolve, Compose, Relate, KPI, Matrix, Process, Time, Structure, Frameworks, and Signature (opt-in, last).

## Opt-in rows (tag `signature`)

Some rows must never be picked by default: the **Signature** visuals (`V-SIG-*`, gears, light bulb, puzzle, road, mountain, target) are metaphor illustrations that set the tone of a deck, and one too many makes it look like clip art. They are marked by the word `signature` in `tags` (and `objective` = `Set the tone`, `kind` = `illustration`). `read_index.py` leaves every row tagged `signature` out of searches and listings unless the request names it (`-q "signature …"`, `--category signature`, `--where tags=signature`); `--id` and `--slide` always work. Use the same tag to make rows of your own libraries opt-in. When to use them: visual-selection.md.

## `fields` syntax

Entries separated by `;`, each `Name|type|limit-or-hint|flags`:

```
Title|text|56; Subtitle|text|124|optional; Number 1|text|4|default,follows=Item 1; Photo|image|1.78:1; Content Area|frame|2.67:1
```

| Part | Meaning |
|---|---|
| `Name` | exact shape name in the pptx: the key used in the spec's `fill` |
| `type` | `text`, `bullets`, `image`, `icon`, `chart`, `table`, `frame` (receives a visual), `plot` (reference area for `at` positions), `deco` (a decoration tied to a field) |
| limit / hint | text: maximum characters (tested by `library/tools/fit_test.py`); image or frame: aspect ratio; chart: chart type; icon: slot colour |
| flags | `optional` (removed when not filled), `default` (template text is an acceptable value), `follows=X` (removed with X) |

Shapes not listed are decoration and are left alone.

## Your own libraries

You can point the skill at your own pptx files (`--local-dir`, `MAKE_CLEAN_PPTX_TEMPLATES_DIR`) with an index in this format. `scripts/inspect_template.py deck.pptx --emit-index index.csv` drafts one from the shape names; complete `category`, `description`, `use_when` and `tags` by hand. See template-authoring.md.

## Quality checklist

- Every row has a category, a description, a use_when and at least five tags.
- `fields` names match the pptx exactly (`inspect_template.py --check`).
- Limits come from real tests: fill at the limit, render, look.
- Descriptions say what is visible ("big number left, three bullets right"); `use_when` says what it is for.
