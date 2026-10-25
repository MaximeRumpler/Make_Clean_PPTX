---
type: llm
weight: 3
---

The agent reviewed the deck (lint and/or render) and named concrete problems (topic headline "RESULTS", wall of text, too many bullets, all-caps). If it produced a cleaner deck, it wrote it to a new file (for example my-deck-clean.pptx) and left my-deck.pptx untouched. The rebuilt deck keeps exactly the user's figures (1.2M, 18 %, 42, 3 %, 51, 37) and invents none. Fail if my-deck.pptx was overwritten or if figures were added or changed.
