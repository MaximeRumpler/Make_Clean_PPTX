# Review checklist

Use it on `build/render/contact-sheet.png` and on single slides (`build/render/slide-N.png`). It is written so that a separate reviewer (a sub-agent, a colleague) can apply it without context. Report findings as: slide number, problem, concrete fix (field, value, other layout id).

## Blocking (fix before delivery)

1. **Placeholder left**: any slot description ("Slide title states the takeaway", "Short text", "00", "Item name", "Category 1") or an empty grey frame/image box.
2. **Invented content**: a figure, name, quote or date that is not in the user's material.
3. **Overflow or clipping**: text outside its box, over another shape, or cut at the slide edge.
4. **Unreadable**: text smaller than ~9 pt on screen, light grey on light grey, chart labels colliding.
5. **Wrong data visual**: chart type that misleads (pie with many parts, unsorted ranking, two bars for a variation that needs a waterfall).
6. **Image problem**: visible text, logo or watermark, recognisable person not supplied by the user, an important part cropped out, missing credit in notes.

## Quality (fix when possible)

7. **Headline is a topic, not a message** ("Revenue" instead of "Revenue grew 18%").
8. **Headline and visual disagree**: the chart does not show what the title says.
9. **Rhythm**: the same layout three times in a row, three dense slides in a row, too many dark slides.
10. **Empty or unbalanced**: one short line on a large layout, a column much longer than its neighbours. Choose a layout with fewer slots.
11. **Inconsistency**: units, rounding, date formats, capitalisation, tone or language differ between slides.
12. **Icons**: mixed families or styles, an icon that needs explaining, icons on some parallel items only.
13. **Story**: reading only the headlines does not give the argument; the closing is not a decision or next step.

## Not a problem

- Small differences between LibreOffice and PowerPoint rendering (kerning, line breaks a word earlier).
- Neutral grey styling: it is the design; the user's theme will recolour it.
- Empty speaker notes on simple slides.

## Output format

```text
slide 4  BLOCKING  placeholder "Short text" under Tile 2 -> set "Tile 2 body": null or give it text
slide 7  QUALITY   headline is a topic -> "Costs fell 12% after the merger"
```
End with one line: `ready` or `needs fixes (N blocking, M quality)`.
