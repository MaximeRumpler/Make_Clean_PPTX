# Image sources

`scripts/fetch_image.py` finds photos in free banks that need **no API key**, so the skill works the same for everyone. Icons and SVG illustrations are covered in `icons-and-illustrations.md`.

| Source | Endpoint | What it is |
|---|---|---|
| Openverse | `api.openverse.org/v1/images/` | search engine over openly licensed media (Flickr, Wikimedia, museums, more) |
| Wikimedia Commons | `commons.wikimedia.org/w/api.php` | the Wikimedia media repository |

Unsplash, Pexels and Pixabay are good banks, but their APIs require a key, so they are intentionally not used. To add one for your own setup, add a `search_<name>()` function in `fetch_image.py` that returns the same candidate dictionaries and register it in `candidates()`.

## Licences

Only licences that allow commercial reuse are accepted (see `images.allowed_licenses` in `config.json`):

- **CC0** and **public domain mark**: no attribution needed (credited anyway).
- **CC BY**: attribution required.
- **CC BY-SA**: attribution required, derivatives must stay share-alike. For a slide deck that is normally fine, but mention it if the deck will be redistributed as an editable template.

NC (non-commercial) and ND (no derivatives) licences are filtered out. Always pass the returned `credit` string in the spec: it lands in the speaker notes of that slide and in `<deck>.credits.md`.

## Using it

```bash
python3 scripts/fetch_image.py --query "solar panels on a roof" --out build/img/s3.jpg --orientation wide
python3 scripts/fetch_image.py --query "coffee shop interior" --list            # inspect candidates only
python3 scripts/fetch_image.py --query "coffee shop interior" --out x.jpg --pick 3   # take the 3rd acceptable result
```

Output (JSON): `path`, `width`, `height`, `source`, `title`, `creator`, `license`, `license_url`, `landing_url`, `credit`.

Tips for queries: concrete nouns and a scene ("hands typing on laptop"), not abstract words ("synergy"). Add `--orientation square|tall` for portrait slots, `--min-width` to relax the 1600 px default.

## Limits and failure modes

- Anonymous API use is rate-limited. Avoid searching in a loop; one query per image slot.
- Sandboxes often use an **allowlist**: if `doctor.py` reports the hosts unreachable, build the deck without photos (use layouts that rely on text, icons and visuals) or ask the user to attach images.
- Images are validated with Pillow (real image, size cap `max_download_mb`), downscaled to `max_dimension` px and saved as JPEG (PNG when there is transparency). Remote files are never executed or opened by anything else.
- Results are not curated: **always look at the image** before using it (Read tool) and reject text-heavy, watermarked, off-topic or sensitive pictures.
