# Contributing

Thanks for helping make decks cleaner. Three kinds of contributions are especially useful.

## 1. Layouts and visuals
A missing structure, a better character limit, richer tags, a clearer description. The libraries are generated: change `library/layouts/*.js` or `library/visuals/*.js`, then rebuild (see [library/README.md](library/README.md)). Follow [template-authoring.md](skills/make-clean-pptx/references/template-authoring.md):

- placeholders only, never sample content;
- theme tokens only (`ink`, `a1`…), never fixed colours;
- every editable element named; `optional`, `keep` and `follows` set where they apply;
- run the fit test and look at the contact sheet; regenerate the gallery.

Open an issue first for a new family of visuals, so we can agree on the place it takes in the selection guide.

## 2. Engine and scripts
Bug fixes, new fill types, better fit heuristics, new icon or image sources.

```bash
pip install -r requirements-dev.txt
pytest
```

- Python 3.9 compatible; standard library + python-pptx, openpyxl, Pillow only.
- Every script keeps its contract: JSON (or clearly structured) output and distinct exit codes. The agent relies on it.
- `skills/make-clean-pptx/` must stay self-contained (no reads outside that folder).
- Add or update a test for each behaviour change. The tests build real decks and re-open them, so they catch broken packages.
- If you change the index contract, update `index-schema.md`, `read_index.py`, `build_index.py` and `tests/make_fixtures.py` together.

## 3. Skill instructions
`SKILL.md` and `references/` are read by an agent, not a human. Explain *why* a rule exists instead of shouting it, keep `SKILL.md` short, and move detail into `references/`. Test changes on a few real prompts, including one in French and one with very little content.

## Pull requests
Small and focused. Describe the problem, what changed, and how you verified it (test, rendered contact sheet). Be kind in reviews.

By contributing you agree that your contribution is licensed under the EUPL-1.2, the licence of this repository, including the additional permission in [NOTICE](NOTICE) that leaves the decks people create free of any obligation. This is what keeps improvements to the libraries shared with everyone.
