# Changelog

## 0.2.1 (2026-11-14)
- Phones: the world map zooms with two fingers (or Ctrl/⌘ + scroll on a computer) and has
  +, − and reset buttons; the scatter plot is drawn taller with larger text and dots on narrow screens.
- Security: every page carries a Content-Security-Policy (`biv_web/csp.py`): scripts only from the
  pinned D3 file (integrity hash) and the page's own script (SHA-256), data only from the page's own
  site. Text from the config is escaped before it reaches the page. See `SECURITY.md`.

## 0.2.0 (2026-11-14)
- New explorer mode (`mode = "explore"`, `config_explore.toml`, `biv_web/explore.py`): 12 measures
  (10 GI-TOC 2025, 2 Gallup 2025); the reader picks the two that make the bivariate map.
- New `docs/index.html`: two pickers, swap button, ready-made pairs, plain-language labels,
  "higher is better / worse" hints, titles and notes generated from the variable catalogue.
- `biv_web/standalone.py`: one-file copy of the page with the data inlined.
- The 0.1.0 page is kept as `docs/pair.html`; fixed a duplicated legend/search block in it
  (the same element ids appeared twice).
- meta.json also records the tables' SHA-256 and the upstream `crime_flat` version.

## 0.1.0
- Fixed-pair pages built from `bivariate` GeoPackages (feelsafe, resilience).
