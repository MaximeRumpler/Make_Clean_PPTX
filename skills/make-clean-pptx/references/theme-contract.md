# Theme contract

What a PowerPoint theme must provide so that the layouts and visuals of this skill stay readable and keep their meaning when the theme replaces the neutral greys. Read it before applying a brand theme, or when writing a tool that produces one (the companion skill Make_Colors_PPTX does).

The machine-readable version is `assets/theme-contract.json`. It is **generated** from the libraries (`library/tools/build_contract.py`): the usage counts and the colour pairs below are measured on `layouts.pptx` and `visuals.pptx`, not estimated, and CI fails if the file no longer matches the libraries.

## Why a contract

Every colour in the libraries is a theme reference, so a theme recolours everything. Two things are fixed, though:

- **The meaning of the accents.** `accent1` to `accent6` are a ramp from strong to faint. Charts, heat grids, layers and levels read them in that order, and `accent1` is the emphasis everywhere.
- **The text colour on each fill.** Text on `accent1` and `accent2` is the background colour (`paper`); text on `accent3` to `accent6` is the text colour (`ink`). The engine applies the same rule when it tints a shape (`is_dark` in `scripts/_common.py`).

A typical brand palette, six distinct hues, breaks both: charts turn into a rainbow, the order means nothing, and white text lands on yellow or black text on navy.

## Slots

Each colour slot of the theme, what the libraries use it for, and how many times (text runs, shape fills, lines, chart series or slices) and in how many of the 122 library slides.

| Slot | Role | Neutral | Text | Fill | Line | Chart | Slides |
|---|---|---|---|---|---|---|---|
| `dk1` | main text (`ink`); lightened for captions and labels (`muted`) | `111111` | 971 | 27 | 131 | 0 | 120 |
| `lt1` | slide background (`paper`), text on dark fills; darkened for rules (`line`) | `FFFFFF` | 135 | 52 | 259 | 0 | 90 |
| `dk2` | body text (`ink2`) | `404040` | 474 | 0 | 0 | 0 | 99 |
| `lt2` | cards, panels, frames (`surface`) | `F2F2F2` | 0 | 112 | 0 | 0 | 32 |
| `accent1` | strongest emphasis, main series, dark panels and slides | `1F1F1F` | 0 | 98 | 25 | 47 | 70 |
| `accent2` | second step, dark secondary panels | `595959` | 0 | 39 | 4 | 4 | 17 |
| `accent3` | middle step, third series; muted text on dark slides | `8C8C8C` | 4 | 25 | 14 | 8 | 23 |
| `accent4` | reference series, light fills; kickers on dark slides | `B3B3B3` | 15 | 26 | 16 | 8 | 29 |
| `accent5` | light fills, levels; subtitles on dark slides | `D0D0D0` | 6 | 43 | 2 | 6 | 31 |
| `accent6` | faintest fill (quadrants, logo slots); captions on dark fills | `E6E6E6` | 8 | 31 | 0 | 6 | 27 |
| `hlink` | hyperlinks (none in the libraries; links people add) | `404040` | 0 | 0 | 0 | 0 | 0 |
| `folHlink` | visited hyperlinks | `8C8C8C` | 0 | 0 | 0 | 0 | 0 |

Fonts: the **major** font (`+mj`) sets headings, titles and big numbers (227 runs on 68 slides); the **minor** font (`+mn`) sets everything else, including table and chart text (1,386 runs on all 122 slides). The libraries' character limits are measured with Arial metrics: a much wider brand font makes text overflow sooner, so check the render.

Chart series take the accents in the order `accent1, accent3, accent5, accent2, accent4, accent6`, so that neighbouring series are far apart on the ramp.

A brand is colours, fonts and a logo. The theme carries the first two; the logo is not part of the theme: a brand tool gives it to the deck with the `"logo"` key of deck.json (`spec-reference.md`), which fills the `Logo` slot of the covers and the closing slide. Its contrast with the slide is not checked: provide a light variant for dark covers.

## Ramp order

- `accent1` sits next to the text colour and `accent6` next to the background. On a light theme, luminance strictly increases from `accent1` to `accent6`; on a dark theme it strictly decreases.
- `dk1` and `dk2` sit on the text side, `lt1` and `lt2` on the background side.
- Neighbouring accents differ by at least 1.1:1 in contrast, or levels and series look the same.

Hue is free: a ramp of one brand hue (navy to pale blue) or a ramp that drifts between two close hues both work. Six unrelated hues do not.

**Dark themes** follow the same rule, relative to text and background: the background slot (`lt1`, or `dk1` when the master's colour map swaps them) is dark, the text slot is light, and `accent1` is the *lightest* accent, because it carries the background colour as text.

## Pairs to keep readable

Thresholds are WCAG 2.x: **4.5:1** for text, **3:1** for large text (18 pt and above, or 14 pt bold and above) and for graphics that carry meaning on their own. The libraries use 10 pt text on almost every pair, so 4.5:1 applies nearly everywhere.

| Text | On | Slots | Runs | Needs | Neutral |
|---|---|---|---|---|---|
| muted | paper | dk1 (lightened) / lt1 | 371 | 4.5 | 5.1 |
| ink2 | paper | dk2 / lt1 | 346 | 4.5 | 10.4 |
| ink | paper | dk1 / lt1 | 345 | 4.5 | 18.9 |
| ink | surface | dk1 / lt2 | 101 | 4.5 | 16.9 |
| paper | a1 | lt1 / accent1 | 89 | 4.5 | 16.5 |
| ink2 | surface | dk2 / lt2 | 57 | 4.5 | 9.3 |
| paper | a2 | lt1 / accent2 | 31 | 4.5 | 7.0 |
| ink | a3, a6, a4, a5 | dk1 / accent3–6 | 20, 18, 17, 17 | 4.5 | 5.6 to 15.1 |
| muted | surface | dk1 (lightened) / lt2 | 16 | 4.5 | 4.5 |
| a4, a6, a5, a3 | a1 | accent4, 6, 5, 3 / accent1 | 15, 8, 5, 3 | 4.5 | 4.9 to 13.2 |
| paper | ink | lt1 / dk1 | 11 | 4.5 | 18.9 |
| ink2 | a5, a6, a4 | dk2 / accent5, 6, 4 | 7, 5, 2 | 4.5 | 5.0 to 8.3 |
| a3 | paper | accent3 / lt1 | 1 (80 pt) | 3.0 | 3.4 |
| a5 | a2 | accent5 / accent2 | 1 | 4.5 | 4.5 |

Graphics: `accent1`, `accent2` and `accent3` on `paper` need 3:1 (lines, markers, single-series charts, arrows). Lighter accents are fills that always carry a label or sit next to one. Links: `hlink` needs 4.5:1 on `paper` and on `surface`.

The tightest pairs in the neutral theme are `muted` on `surface` (4.5:1), `a5` on `a2` (4.5:1) and `a3` on `a1` (4.9:1): a brand theme has little room there, so check them first. Text over semi-transparent stacked fills (Venn-type visuals) depends on the overlap and is checked on the actual deck only.

## Applying a theme

Add `"theme": "brand.thmx"` to deck.json (`.potx`, `.pptx` and theme `.xml` work too): `build_deck.py` replaces the colours and fonts of the deck's theme in one pass, applies the source master's colour map if it has one (dark themes), and prints this contract's findings as warnings without failing the build. Details and the font fallback: `spec-reference.md`, "Brand theme".

## Checking a theme

```bash
python3 scripts/lint_deck.py deck.pptx --contrast
```

The flag is opt-in; without it the lint is unchanged. It reads the deck's own theme (`ppt/theme/theme1.xml` and the master's colour map), resolves every `schemeClr` with its `lumMod`, `lumOff`, `tint`, `shade` and `alpha`, and then:

- **errors**: each shape whose text is below its threshold over the fill actually under it (shape fill, group, table cell, chart slice, or what lies below a transparent shape), in plain words with both colours and the ratio;
- **warnings** (`theme: …`): the theme against this contract, for pairs the deck may not use yet: a broken ramp, accents too close, each failing pair with how often the libraries use it.

It cannot judge text over pictures or gradients (reported as "not checked"), and it decides what is under a text box at the box's centre.

## What the contract catches

The test suite applies three themes to the libraries (`tests/test_theme_contract.py`):

- a **one-hue brand ramp** (navy to pale blue): no failure;
- a **dark theme** (light text on near-black, `accent1` lightest): no failure;
- a **saturated brand palette** (red, orange, teal, yellow, purple, dark teal): the ramp warning, plus 167 shapes too faint across the two libraries, among them white text on the red `accent1` (64 shapes, 4.2:1), white on the orange `accent2` (31), black on the purple and dark-teal `accent5` and `accent6` (34), and the light accents used as text on dark slides.

The fix is never in the deck: build the brand theme as a ramp, keep the brand's signature hue on `accent1` (or `accent2` when it is mid-tone), and use `lint_deck.py --contrast` until the warnings are gone.
