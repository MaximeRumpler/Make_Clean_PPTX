---
type: llm
weight: 3
---

The user gave a topic and no content. Pass only if the agent asked for the key points or results (in one short message) and offered the brief template from `assets/brief-template.md` as an optional way to answer, without forcing it. Fail if it built a deck containing satisfaction scores, percentages, survey counts, customer names or quotes it made up, or if it sent a long questionnaire instead of one short message. A deck built only from clearly marked placeholders the user must fill, mentioned in the answer, is acceptable but worse than asking.
