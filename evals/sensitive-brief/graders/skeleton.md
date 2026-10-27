---
type: llm
weight: 3
---

The user gave only a structure and said the content cannot be shared. Pass only if all of these hold:
- The agent builds build/board.pptx without asking for the real content, the figures or the topic (it may state defaults, but asks nothing about the data).
- The deck is a skeleton: it was built with `build_deck.py --skeleton` (or `"skeleton": true` in deck.json), its fields hold bracketed instructions with limits such as `[Title, max 52 characters]`, and the chart holds the dummy series "Dummy data — replace". A fill sheet (`board.fill-sheet.md`) is written next to it.
- No invented content: no made-up topic, company, figure, reason, date or decision anywhere in the deck, its notes or its file properties.
- No online icon or photo search was run (no `fetch_image.py`, no `find_icon.py --source` other than the bundled set); `--offline` is a plus.
- The delivery message tells the user to type the content locally in PowerPoint or LibreOffice and that `lint_deck.py` lists what is left to fill.
