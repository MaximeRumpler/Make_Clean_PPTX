<div align="center">

[![Make_Clean_PPTX, an agent skill that turns notes into PowerPoint decks: 54 slide layouts, 81 charts and diagrams](docs/banner.svg)](https://maximerumpler.github.io/Make_Clean_PPTX/)

*Give your AI assistant your notes. Get back a PowerPoint deck with one idea per slide and real, editable charts.*

<sub lang="fr">En français : donnez vos notes à votre assistant IA, recevez une présentation PowerPoint propre, une idée par diapositive.</sub>

[![CI](https://img.shields.io/github/actions/workflow/status/MaximeRumpler/Make_Clean_PPTX/ci.yml?branch=main&style=flat-square&label=CI&color=10B981&labelColor=1C2333)](https://github.com/MaximeRumpler/Make_Clean_PPTX/actions/workflows/ci.yml)
[![Licence](https://img.shields.io/badge/Licence-EUPL--1.2-10B981?style=flat-square&labelColor=1C2333)](LICENSE)
[![Gallery](https://img.shields.io/badge/Gallery-135_slides-10B981?style=flat-square&labelColor=1C2333)](https://maximerumpler.github.io/Make_Clean_PPTX/)
[![Make PPTX](https://img.shields.io/badge/Set-Make_PPTX-10B981?style=flat-square&labelColor=1C2333)](https://github.com/MaximeRumpler/Make_PPTX)

</div>

* * *

<div align="center">

[![Nine sample slides: a cover, a key figure, a chart with key points, a recommended option, a waterfall chart, an impact and effort matrix, a process, a roadmap and a grid of tiles](docs/preview.jpg)](https://maximerumpler.github.io/Make_Clean_PPTX/)

</div>

## What it does

Make_Clean_PPTX is a *skill*: a folder of instructions and small tools that an AI assistant such as Claude or Codex uses to make presentations.

You give it your notes, a report or a few figures, in English or French. It writes one message per slide, takes a matching slide design and chart from its library, and checks the file before handing it over. It never makes up numbers.

The slides are black, grey and white. Apply your company's PowerPoint theme and they switch to your colours and fonts (best with accent colours that run from dark to light, see the [theme contract](skills/make-clean-pptx/references/theme-contract.md)). They open in LibreOffice too, and can be saved as `.odp`.

* * *

## Install

| **Claude.ai or Claude desktop** | **Claude Code** | **Codex, Cursor, Copilot, Gemini CLI and others** |
|:---|:---|:---|
| 1. Download [**make-clean-pptx.zip**](https://github.com/MaximeRumpler/Make_Clean_PPTX/releases/latest/download/make-clean-pptx.zip)<br>2. *Settings → Capabilities*: turn on *Code execution and file creation*<br>3. *Skills → Upload skill*, choose the zip | `/plugin marketplace add MaximeRumpler/Make_PPTX`<br>then `/plugin install make-clean-pptx@make-pptx` | `npx skills add MaximeRumpler/Make_Clean_PPTX`<br>It asks which assistant you use. Needs [Node.js](https://nodejs.org). |

**Not sure which one?** If you talk to Claude in a browser or in the Claude app, use the first column: nothing to install on your computer. Without step 2, Claude can read the skill but cannot build the file. First time with a skill? The [Get started guide](https://github.com/MaximeRumpler/Make_PPTX/blob/main/docs/get-started.md) walks you through it.

Works on Windows, macOS and Linux. The second and third columns need Python on your computer; the skill tells you if it, or anything else, is missing. Other ways (manual copy, `install.sh`): [docs/how-it-works.md](docs/how-it-works.md#manual-install-and-requirements).

The Claude Code command adds `make-pptx`, the marketplace of the Make PPTX set. Installed earlier with `/plugin marketplace add MaximeRumpler/Make_Clean_PPTX`? That still works; update with `/plugin marketplace update make-clean-pptx`.

**Update**: Claude Code, `/plugin marketplace update make-pptx`; Claude.ai, upload the new zip; other assistants, run the `npx skills add` line again.

## Use

Just ask, in your own words:

```text
Make a 10-slide deck from this report for the board.
Make an 8-slide deck in French from these notes.
Review my-deck.pptx and make it look professional.
```

It may ask a few quick choices first (file format, a confidentiality label, length, extra accessibility care). Every choice is optional and the defaults add nothing. Content you cannot share? Ask for a skeleton deck that you fill in yourself, offline if needed. Both are explained in the [Get started guide](https://github.com/MaximeRumpler/Make_PPTX/blob/main/docs/get-started.md#5-the-quick-choices-it-asks-about) and the [Private mode page](https://github.com/MaximeRumpler/Make_PPTX/blob/main/docs/private-mode.md).

* * *

## What's inside

| **54 slide designs** | **81 charts and diagrams** | **1,900 icons** |
|:---:|:---:|:---:|
| covers, key messages, figures, options, next steps | bars, waterfalls, matrices, timelines, org charts | bundled, plus free online icons and photos |

19 of the visuals are opt-in: six *signature* illustrations (gears, a light bulb, a summit…) and thirteen *expressive* orbital diagrams. The skill uses them only when you ask or when the content clearly suits them, and sparingly: how many depends on your request, your audience and the style of the content.

Browse them in the [gallery](https://maximerumpler.github.io/Make_Clean_PPTX/), or download a [finished example deck](https://github.com/MaximeRumpler/Make_Clean_PPTX/releases/latest) made from a page of notes. How it works and how to add your own designs: [docs/how-it-works.md](docs/how-it-works.md).

* * *

## The Make PPTX set

Part of [**Make PPTX**](https://github.com/MaximeRumpler/Make_PPTX), three skills that take your notes to a finished deck. Each one works on its own.

| **Make_Clean_PPTX** | **Make_Style_PPTX** | **Make_Colors_PPTX** |
|:---|:---|:---|
| **Form.** Notes in, a clean deck out: one message per slide, tested layouts and charts. | **Look.** The same deck in another style: other shapes, arrangements and backgrounds. | **Brand.** Your colours, fonts and logo, from your brand guidelines, website or example files. |
| [Install](https://github.com/MaximeRumpler/Make_Clean_PPTX#install) · [Gallery](https://maximerumpler.github.io/Make_Clean_PPTX/) | Preview · [Install](https://github.com/MaximeRumpler/Make_Style_PPTX#install) | Preview · [Install](https://github.com/MaximeRumpler/Make_Colors_PPTX#install) |

*Start with Make_Clean_PPTX for the structure. Add a style and your brand colours when you need them.*

* * *

## Licence

[EUPL-1.2](LICENSE), the open source licence of the European Union: free to use; if you share an improved version, share it under the same licence. **You own the decks you make.** The EUPL does not apply to them and no attribution is required ([NOTICE](NOTICE)). Contributions are welcome: [CONTRIBUTING.md](CONTRIBUTING.md).

<div align="center">

Built by [**Maxime Rumpler**](https://github.com/MaximeRumpler) · [![KairosTech](https://img.shields.io/badge/Kairos-Tech-10B981?style=flat-square&labelColor=1C2333&logoColor=white)](https://github.com/KairosTech-fr) · [kairostech.fr](https://kairostech.fr)

<sub>With thanks to the creators and contributors of [impeccable](https://github.com/pbakaus/impeccable), whose design skills for AI agents inspired this set, and of Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), which guides how its texts are written.</sub>

<p align="right">
  <img src="https://komarev.com/ghpvc/?username=MaximeRumpler&repo=Make_Clean_PPTX&color=44cc11&style=flat-square&label=views" alt="Repository Views" />
</p>

</div>
