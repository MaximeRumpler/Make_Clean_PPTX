<div align="center">

[![Make_Clean_PPTX](docs/banner.svg)](https://maximerumpler.github.io/Make_Clean_PPTX/)

*Give your AI assistant your notes. Get back a clean, professional PowerPoint.*

[![CI](https://img.shields.io/github/actions/workflow/status/MaximeRumpler/Make_Clean_PPTX/ci.yml?branch=main&style=flat-square&label=CI&color=10B981&labelColor=1C2333)](https://github.com/MaximeRumpler/Make_Clean_PPTX/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-EUPL--1.2-10B981?style=flat-square&labelColor=1C2333)](LICENSE)
[![Gallery](https://img.shields.io/badge/Gallery-122_slides-10B981?style=flat-square&labelColor=1C2333)](https://maximerumpler.github.io/Make_Clean_PPTX/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-D97757?style=flat-square&logo=anthropic&logoColor=white&labelColor=1C2333)](#install)

</div>

* * *

<div align="center">

[![Nine sample slides: a cover, a key figure, a chart with key points, a recommended option, a waterfall chart, an impact and effort matrix, a process, a roadmap and a grid of tiles](docs/preview.jpg)](https://maximerumpler.github.io/Make_Clean_PPTX/)

</div>

## What it does

Make Clean PPTX is a *skill*, a set of instructions and tools that teaches an AI assistant such as Claude or Codex to make presentations.

You give it your notes, a report or a few figures, in English or French. It writes one message per slide, takes a matching slide design and chart from its library, and checks the file before handing it over. It never makes up numbers.

The slides are black, grey and white. Apply your company's PowerPoint theme and they switch to your colours and fonts. They open in LibreOffice too, and can be saved as `.odp`.

* * *

## Install

| **Claude Code** | **Claude.ai and Claude desktop** | **Other AI assistants** |
|:---|:---|:---|
| `/plugin marketplace add MaximeRumpler/Make_Clean_PPTX`<br>then `/plugin install make-clean-pptx@make-clean-pptx` | Download [`make-clean-pptx.zip`](https://github.com/MaximeRumpler/Make_Clean_PPTX/releases/latest), then *Settings → Capabilities → Skills → Upload skill* | `npx skills add MaximeRumpler/Make_Clean_PPTX` |

Works the same on Windows, macOS and Linux. The skill needs Python, which most assistants already have. If something is missing, it tells you what to install.

**Update**: Claude Code, `/plugin marketplace update MaximeRumpler/Make_Clean_PPTX`; Claude.ai, upload the new zip; other assistants, run the `npx skills add` line again.

## Use

Just ask, in your own words:

```text
Make a 10-slide deck from this report for the board.
Make an 8-slide deck in French from these notes.
Review my-deck.pptx and make it look professional.
```

* * *

## What's inside

| **54 slide designs** | **68 charts and diagrams** | **1,900 icons** |
|:---:|:---:|:---:|
| covers, key messages, figures, options, next steps | bars, waterfalls, matrices, timelines, org charts | bundled, plus free online icons and photos |

Browse them in the [gallery](https://maximerumpler.github.io/Make_Clean_PPTX/), or download a [finished example deck](https://github.com/MaximeRumpler/Make_Clean_PPTX/releases/latest) made from a page of notes. How it works and how to add your own designs: [docs/how-it-works.md](docs/how-it-works.md).

* * *

## The Make PPTX set

Part of [**Make PPTX**](https://github.com/MaximeRumpler/Make_PPTX), a set of three skills from your notes to a finished deck.

*From your content, first Make_Clean, then add your style and your colours.*

| **Make_Clean_PPTX** | **Make_Style_PPTX** | **Make_Colors_PPTX** |
|:---|:---|:---|
| **Form.** Notes in, clean deck out. | **Look.** The same deck in another style: editorial, organic, geometric, tech, soft. | **Brand.** Your colours, fonts and logo, from your brand guidelines, website or example files. |
| This repository | In preparation | In preparation |

Each one works on its own; Make_Clean_PPTX is all you need to start.

* * *

## License

[EUPL-1.2](LICENSE), the open source licence of the European Union: free to use; if you share an improved version, share it under the same licence. **The presentations you make are yours**, with no obligation ([NOTICE](NOTICE)). Contributions are welcome: [CONTRIBUTING.md](CONTRIBUTING.md).

<div align="center">

Built by [**Maxime Rumpler**](https://github.com/MaximeRumpler) · [![KairosTech](https://img.shields.io/badge/Kairos-Tech-10B981?style=flat-square&labelColor=1C2333&logoColor=white)](https://github.com/KairosTech-fr) · [kairostech.fr](https://kairostech.fr)

<sub>With thanks to the creators and contributors of [impeccable](https://github.com/pbakaus/impeccable), whose design skills for AI agents inspired this set, and of Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), which guides how its texts are written.</sub>

</div>
