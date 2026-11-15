# Security

- **Pinned library:** D3 7.9.0 from jsDelivr with a `sha384` integrity hash; a changed file is refused.
- **Content-Security-Policy** in every page, written by `python -m biv_web.csp <page>` (the explorer
  build and `biv_web.standalone` run it automatically): scripts only from the pinned D3 file and the
  page's own inline script, identified by its SHA-256; data only from the page's own site; fonts only
  from Google Fonts; no forms, no `<base>` changes. After editing a page's script, stamp it again,
  or the browser will refuse to run it.
- **Text is never run as code:** country names and data reach the page through `textContent`;
  labels and descriptions from the config are escaped. The link's `#a--b` is accepted only when it
  names two known variables.
- **No keys or secrets** are needed or published.
- Privacy note: the fonts come from Google Fonts, so a visitor's browser contacts Google. To avoid
  that, remove the two font links; the page falls back to system fonts.

Report a problem through the repository's issues, or via ORCID 0000-0003-3309-5256.
