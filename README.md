# biv_web

Interactive bivariate world map. Version 0.2.0 adds the **explorer**: the reader picks the two
measures (GI-TOC only, or GI-TOC with the Gallup survey) and the map, legend, title, country card
and scatter plot follow.

```
python -m biv_web config_explore.toml     # -> docs/data/explore/  (page: docs/index.html)
python -m biv_web.standalone docs         # optional one-file copy -> docs/standalone.html
cd docs && python3 -m http.server 8000
```

## Explorer (config_explore.toml)
- Inputs: `data/gitoc_oc_index_wide.csv` (2025 rows) and `data/gallup_safety_2025.csv`, both made by
  `crime_flat`; country polygons from `data/bivariate.gpkg`; colours from `data/legend.json`.
- `[[variables]]` is the catalogue: add, remove or reword a measure there (label, short name,
  description, whether higher is better or worse). Nothing in the page is hard-coded.
- `[[presets]]` are the ready-made pairs with their own title and one-line explanation. Any other
  pair gets a title built from the two labels.
- Class breaks are computed once, in Python (`biv_web/explore.py`), with the rule of `bivariate` 2.x:
  three quantile classes, linear interpolation, over all countries that have the variable; a value
  equal to a break goes to the upper class. They reproduce the published breaks (cyber crime 3.5 / 5.5,
  resilience 4.04 / 5.38, feeling safe 60 / 75). The page only looks classes up.
- `docs/data/explore/meta.json` records input SHA-256s, the config, the script version and the
  `crime_flat` version that made the tables.
- A link can open on a pair: `index.html#resilience_avg--criminality_avg`.
- Works on phones: two-finger zoom on the map, buttons for zoom and reset, larger scatter plot.
- Security: see `SECURITY.md`. If you edit a page's script, run `python -m biv_web.csp docs/index.html`.

## Fixed pair (earlier mode, page: docs/pair.html)
Interactive version of the `bivariate` 2.x outputs: cyber-dependent crime (GI-TOC 2025) against
(1) the share of adults who feel safe walking alone at night (Gallup Global Safety Report 2025) and (2) GI-TOC resilience.

```
config_feelsafe.toml   -> data/bivariate_feelsafe.gpkg  -> docs/data/feelsafe/
config.toml            -> data/bivariate.gpkg + data/legend.json -> docs/data/resilience/
python -m biv_web config_feelsafe.toml
python -m biv_web config.toml
cd docs && python3 -m http.server 8000
```

- Reads GeoPackages with the standard library + shapely (no GDAL). Geometry stays in EPSG:8857 and is drawn as planar coordinates.
- Labels, breaks and colours come from the run's legend.json when given; otherwise breaks are derived from the classes stored in the GeoPackage.
- meta.json records the input SHA-256, config, script version and the bivariate run id.
- Note: the resilience run's config still carries the project name "Fear vs crime: feeling safe at night vs criminality"; its indicator A is GI-TOC `resilience_avg`.

## GitHub Pages
Settings → Pages → Deploy from a branch → `main`, folder `/docs`.

## Licences
- Code: MIT.
- GI-TOC Global Organized Crime Index 2025: CC BY 4.0 (attribution required).
- Feel safe walking alone at night: Gallup, Global Safety Report 2025 (https://www.gallup.com/analytics/356996/gallup-global-safety-research-center.aspx). Gallup publishes these values but states no open licence; they are shown here with credit. An openly licensed alternative is SDG 16.1.4 from Our World in Data, adapted from UNODC (CC BY): https://archive.ourworldindata.org/20261102-112946/grapher/safety-walking-alone.html
- Boundaries: Natural Earth (public domain).

## Gallup data is not in this repository
Gallup publishes the "feel safe walking alone at night" values (Global Safety Report 2025) but states no open
licence, so the source table and the feeling-safe GeoPackage are not redistributed here (`data/gallup_*.csv` is git-ignored). The published page
shows the values with credit. To rebuild the feeling-safe layer:

1. Download the 2025 country table from the Gallup Global Safety Research Center:
   https://www.gallup.com/analytics/356996/gallup-global-safety-research-center.aspx
2. Save it as `processed/gallup_2025.csv` in your `bivariate` project (columns `iso3`, `safe_walking_night_pct`).
3. Run `bivariate` with the feeling-safe config, and copy its `bivariate.gpkg` to `data/bivariate_feelsafe.gpkg` here.
4. `python -m biv_web config_feelsafe.toml`

The SHA-256 of the GeoPackage used for the published page is recorded in `docs/data/feelsafe/meta.json`,
so a rebuilt file can be checked against it.
