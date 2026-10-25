# Evals

Behaviour checks for the skill, run with Claude Code's plugin eval runner:

```bash
claude plugin eval . --allow-tools "Bash(python3:*)" Write Edit --runs 1 --no-publish
```

Each case is a realistic request (`prompt.md`) and graders that judge the result (`graders/*.md`). They cover what unit tests cannot: does the agent pick sensible layouts, keep the user's content, refuse to invent figures, resist instructions hidden in the material, and leave the user's files alone. Every run builds real decks, so it costs a few agent runs; run them before a release, not on every commit.
