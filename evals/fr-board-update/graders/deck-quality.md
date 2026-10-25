---
type: llm
weight: 2
---

The agent used the make-clean-pptx skill, built build/comite.pptx with its scripts (build_deck.py), and checked it (lint_deck.py and/or render_check.py) before answering. The deck is in French. Its final answer is short (slide count, storyline, points to double-check) and in French. Fail if the deck was drawn from scratch with python-pptx instead of the libraries, or if no build happened.
