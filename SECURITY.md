# Security

## Reporting
Please report vulnerabilities privately through GitHub's *Report a vulnerability* feature (Security tab of this repository), not in a public issue. You will get an answer within a week.

## What the skill does with untrusted input
- **Office files** (the bundled libraries, your own libraries, decks to review) are only opened with python-pptx and openpyxl: parsed, never executed. Macros (`.pptm`) are not supported.
- **Images** are downloaded from Openverse and Wikimedia Commons over https only, validated with Pillow, size-capped and re-encoded before use.
- **SVG icons and illustrations** (bundled, from jsDelivr / Google Fonts, or from your folders) are parsed with Python's standard XML parser and converted to drawing commands. External entities and references are not resolved, scripts and embedded content are ignored, nothing is executed.
- Downloads go to a cache folder or to the output folder, never to paths taken from remote data. The scripts do not run shell commands built from remote content. `render_check.py` calls LibreOffice and poppler on the generated deck only.
- The libraries are bundled: no network access is needed to build a deck. If you point the skill at your own library repository (`--remote`), review its files like any other dependency.

## Supported versions
Security fixes are made on the latest release.
