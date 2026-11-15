"""Explorer mode: every variable for every country, so the page can pair any two.

The page does not compute class breaks. They are computed here, once per variable, with the
same rule as `bivariate` 2.x (quantile, three classes, linear interpolation, over all countries
that have the variable; a value equal to a break goes in the upper class).
"""
import bisect
import csv
import json
from pathlib import Path

from .build import simplify
from .provenance import sha256

CLASSES = 3


def read_table(path, key, where=None):
    """CSV -> {key value: row}. `where` = {column: value} keeps only matching rows."""
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if where and any(str(row.get(c)) != str(v) for c, v in where.items()):
                continue
            if row.get(key):
                out[row[key]] = row
    return out


def column(table, field):
    """{iso3: float} for the rows where the field has a number."""
    out = {}
    for iso, row in table.items():
        raw = (row.get(field) or "").strip()
        if raw:
            out[iso] = float(raw)
    return out


def quantile(sorted_vals, q):
    """Linear-interpolation quantile (numpy's default), on an ascending list."""
    pos = (len(sorted_vals) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def tercile_breaks(values, decimals=4):
    srt = sorted(values)
    return [round(quantile(srt, k / CLASSES), decimals) for k in range(1, CLASSES)]


def ranks(values):
    """Competition ranking, 1 = highest value; ties share a rank."""
    srt = sorted(values.values())
    n = len(srt)
    return {iso: n - bisect.bisect_right(srt, v) + 1 for iso, v in values.items()}


def step(values, max_distinct=20):
    """Spacing of a coarse scale (e.g. 0.5 for half-step scores); None for fine scales.
    The page nudges dots on coarse scales so they do not hide each other."""
    distinct = sorted(set(values))
    if len(distinct) < 2 or len(distinct) > max_distinct:
        return None
    return round(min(b - a for a, b in zip(distinct, distinct[1:])), 4)


def variable(spec, tables):
    vals = column(tables[spec["table"]], spec["field"])
    if len(vals) < CLASSES:
        raise ValueError(f"variable {spec['key']}: only {len(vals)} values in {spec['table']}.{spec['field']}")
    breaks = tercile_breaks(vals.values())
    if breaks[0] == breaks[1]:
        raise ValueError(f"variable {spec['key']}: the two class breaks are equal ({breaks[0]})")
    return {
        "key": spec["key"], "label": spec["label"], "short": spec["short"], "phrase": spec["phrase"],
        "unit": spec.get("unit", ""), "decimals": spec.get("decimals", 1),
        "higher_is": spec["higher_is"], "group": spec["group"], "source": spec["source"],
        "description": spec["description"],
        "n": len(vals), "min": min(vals.values()), "max": max(vals.values()),
        "breaks": breaks, "step": step(vals.values()),
        "values": dict(sorted(vals.items())), "ranks": ranks(vals),
    }


def country_features(recs, tol, rnd):
    feats = []
    for r in recs:
        g = simplify(r["_geom"], tol, rnd)
        if g is not None:
            feats.append({"type": "Feature", "geometry": g, "properties": {
                "iso3": r["iso3"], "name": r["name_en"] or r["ne_name"], "region": r["subregion"]}})
    return {"type": "FeatureCollection", "features": feats}


def check_presets(cfg, keys):
    for p in [cfg["default"]] + cfg.get("presets", []):
        for side in ("a", "b"):
            if p[side] not in keys:
                raise ValueError(f"preset/default refers to unknown variable '{p[side]}'")
        if p["a"] == p["b"]:
            raise ValueError("a preset needs two different variables")


def upstream(base, tables_cfg):
    """Versions recorded by the pipelines that made the input tables, when their provenance file is given."""
    out = {}
    for name, t in tables_cfg.items():
        p = t.get("provenance")
        if p and (base / p).exists():
            rec = json.loads((base / p).read_text(encoding="utf-8"))
            out[name] = {"tool": rec.get("tool"), "script_version": rec.get("script_version"),
                         "run_utc": rec.get("run_utc"), "provenance_sha256": sha256(base / p)}
    return out


def build(cfg, base, recs):
    """Returns (countries GeoJSON, variables document)."""
    tables = {name: read_table(base / t["file"], t.get("key", "iso3"), t.get("where"))
              for name, t in cfg["tables"].items()}
    variables = [variable(spec, tables) for spec in cfg["variables"]]
    keys = [v["key"] for v in variables]
    if len(set(keys)) != len(keys):
        raise ValueError("variable keys must be unique")
    check_presets(cfg, keys)
    known = {r["iso3"] for r in recs}
    unmatched = {v["key"]: sorted(set(v["values"]) - known) for v in variables}
    palette = json.loads((base / cfg["input"]["legend"]).read_text())["colors"] if cfg["input"].get("legend") \
        else cfg["palette"]
    doc = {
        "page": cfg["page"],
        "default": cfg["default"],
        "presets": cfg.get("presets", []),
        "groups": cfg["groups"],
        "sources": cfg["sources"],
        "palette": palette,
        "method": {"classes": CLASSES, "rule": "quantile, linear interpolation, over all countries with the variable; "
                                               "value >= break goes to the upper class"},
        "variables": variables,
        "checks": {"codes_without_polygon": {k: v for k, v in unmatched.items() if v}},
        "upstream": upstream(base, cfg["tables"]),
    }
    fc = country_features(recs, cfg["geometry"]["simplify_m"], cfg["geometry"]["round_m"])
    return fc, doc
